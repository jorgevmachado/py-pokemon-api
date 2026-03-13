from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import Depends, HTTPException

from app.domain.battle.business import PokemonBattleBusiness
from app.domain.battle.schema import (
    BattlePokemonSchema,
    BattleResult,
    BattleSchema,
    GetBattlePokemonSchema,
)
from app.domain.captured_pokemon.schema import (
    FindCapturePokemonSchema,
    PartialCapturedPokemonSchema,
)
from app.domain.captured_pokemon.service import CapturedPokemonService, PokemonService
from app.domain.move.business import PokemonMoveBusiness
from app.domain.move.model import PokemonMove
from app.domain.pokedex.model import Pokedex
from app.domain.pokedex.schema import PartialPokedexSchema
from app.domain.pokedex.service import PokedexService
from app.domain.progression.business import PokemonProgressionBusiness
from app.domain.progression.schema import StatBlock
from app.domain.trainer.model import Trainer

PokemonService = Annotated[PokemonService, Depends()]
CapturedPokemonService = Annotated[CapturedPokemonService, Depends()]
PokedexService = Annotated[PokedexService, Depends()]


class PokemonBattleService:
    def __init__(
        self,
        captured_pokemon_service: CapturedPokemonService,
        pokedex_service: PokedexService,
        pokemon_service: PokemonService,
    ):
        self.pokemon_service = pokemon_service
        self.pokedex_service = pokedex_service
        self.captured_pokemon_service = captured_pokemon_service
        self.business = PokemonBattleBusiness()
        self.progression_business = PokemonProgressionBusiness()
        self.business_pokemon_move = PokemonMoveBusiness()

    async def battle(self, trainer: Trainer, battle_pokemon: BattlePokemonSchema):
        trainer_pokemon_result = await self.get_trainer_pokemon(
            trainer_id=trainer.id,
            pokemon_name=battle_pokemon.trainer_pokemon,
            pokemon_move=battle_pokemon.trainer_pokemon_move,
        )

        attacker = trainer_pokemon_result.pokemon
        trainer_pokemon_move = trainer_pokemon_result.pokemon_move

        defender_pokemon_result = await self.get_opponent_pokemon(
            trainer_id=trainer.id,
            pokemon_name=battle_pokemon.opponent_pokemon,
            pokemon_move=battle_pokemon.opponent_pokemon_move,
        )

        defender = defender_pokemon_result.pokemon
        defender_pokemon_move = defender_pokemon_result.pokemon_move

        attack_battle_result = self.battle_attack(
            attacker=attacker,
            defender=defender,
            move=trainer_pokemon_move,
        )

        if not attack_battle_result.fainted:
            print('NOT FAINTED')
            pokedex = await self.pokedex_service.update(
                pokedex_id=defender.id,
                pokedex_update=PartialPokedexSchema(
                    hp=attack_battle_result.remaining_hp,
                ),
            )

            new_attacker = self.business.convert_pokedex_to_pokemon_stats(pokedex=pokedex)

            defender_battle_result = self.battle_attack(
                attacker=new_attacker,
                defender=attacker,
                move=defender_pokemon_move,
            )

            captured_pokemon_update = PartialCapturedPokemonSchema(
                hp=defender_battle_result.remaining_hp
            )
            if defender_battle_result.remaining_hp <= 0:
                captured_pokemon_update.losses = attacker.losses + 1

            captured_pokemon = await self.captured_pokemon_service.update(
                captured_pokemon_id=attacker.id,
                captured_pokemon_update=captured_pokemon_update,
            )
            if captured_pokemon.hp <= 0:
                attack_battle_result.winner = defender.nickname

            attack_battle_result.previous_stats.hp = captured_pokemon.hp
            attack_battle_result.defense_damage = defender_battle_result.attack_damage
            return attack_battle_result

        print('FAINTED')
        if defender.hp != defender.max_hp:
            await self.pokedex_service.update(
                pokedex_id=defender.id,
                pokedex_update=PartialPokedexSchema(
                    hp=defender.max_hp,
                ),
            )

        await self.captured_pokemon_service.update(
            captured_pokemon_id=attacker.id,
            captured_pokemon_update=PartialCapturedPokemonSchema(
                hp=attack_battle_result.current_stats.hp,
                level=attack_battle_result.current_level,
                wins=attacker.wins + 1,
                attack=attack_battle_result.current_stats.attack,
                defense=attack_battle_result.current_stats.defense,
                speed=attack_battle_result.current_stats.speed,
                experience=attack_battle_result.current_experience,
                special_attack=attack_battle_result.current_stats.special_attack,
                special_defense=attack_battle_result.current_stats.special_defense,
            ),
        )
        attack_battle_result.winner = attacker.nickname
        return attack_battle_result

    def battle_attack(
        self,
        move: PokemonMove,
        attacker: BattleSchema,
        defender: BattleSchema,
    ) -> BattleResult:

        attack_result = self.business.execute_attack(
            attacker=attacker,
            defender=defender,
            move=move,
        )

        if attack_result.error:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=attack_result.error_detail
            )

        progression_result_attack = self.progression_business.apply_attack_result(
            attacker=attacker,
            defender=defender,
            attack_result=attack_result,
        )

        attacker_progression = progression_result_attack.attacker_progression

        return BattleResult(
            winner='IN BATTLE',
            fainted=attack_result.fainted,
            level_up=progression_result_attack.level_up,
            missed=attack_result.missed,
            critical=attack_result.critical,
            stab=attack_result.stab,
            attack_damage=attack_result.damage,
            defense_damage=0,
            remaining_hp=attack_result.remaining_hp,
            previous_stats=StatBlock(
                hp=attacker.hp,
                attack=attacker.attack,
                defense=attacker.defense,
                speed=attacker.speed,
                special_attack=attacker.special_attack,
                special_defense=attacker.special_defense,
            ),
            previous_level=attacker.level,
            previous_experience=attacker.experience,
            current_stats=StatBlock(
                hp=attacker_progression.hp,
                attack=attacker_progression.attack,
                defense=attacker_progression.defense,
                speed=attacker_progression.speed,
                special_attack=attacker_progression.special_attack,
                special_defense=attacker_progression.special_defense,
            ),
            current_level=attacker_progression.level,
            current_experience=attacker_progression.experience,
            applied_status=attack_result.applied_status,
        )

    async def get_opponent_pokemon(
        self, trainer_id: str, pokemon_name: str, pokemon_move: Optional[str] = None
    ) -> GetBattlePokemonSchema:

        opponent_pokemon = await self.pokedex_service.find_by(
            trainer_id=trainer_id, name=pokemon_name
        )

        if not opponent_pokemon:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Opponent Pokedex Pokemon not found',
            )

        if not opponent_pokemon.discovered:
            opponent_pokemon_discovered = await self.pokedex_service.discover(
                trainer_id=trainer_id, pokemon_name=pokemon_name
            )
            opponent_pokemon_moves = self.get_opponent_pokemon_move(
                pokedex=opponent_pokemon_discovered, pokemon_move=pokemon_move
            )

            return GetBattlePokemonSchema(
                pokemon=self.business.convert_pokedex_to_pokemon_stats(
                    pokedex=opponent_pokemon_discovered
                ),
                pokemon_move=opponent_pokemon_moves,
            )

        opponent_pokemon_moves = self.get_opponent_pokemon_move(
            pokedex=opponent_pokemon, pokemon_move=pokemon_move
        )

        return GetBattlePokemonSchema(
            pokemon=self.business.convert_pokedex_to_pokemon_stats(pokedex=opponent_pokemon),
            pokemon_move=opponent_pokemon_moves,
        )

    def get_opponent_pokemon_move(
        self, pokedex: Pokedex, pokemon_move: Optional[str] = None
    ) -> PokemonMove | None:
        pokemon = pokedex.pokemon
        random_moves = self.business_pokemon_move.select_random_moves(
            available_moves=pokemon.moves, max_moves=1
        )
        random_move = random_moves[0] if random_moves else None

        if not pokemon_move:
            return random_move

        move = next((move for move in pokemon.moves if move.name == pokemon_move), None)
        if not move:
            return random_move

        return move

    async def get_trainer_pokemon(
        self, trainer_id: str, pokemon_name: str, pokemon_move: str
    ) -> GetBattlePokemonSchema:
        captured_pokemon = await self.captured_pokemon_service.find_by_pokemon(
            FindCapturePokemonSchema(trainer_id=trainer_id, name=pokemon_name)
        )

        if not captured_pokemon:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Trainer Pokemon not found'
            )

        trainer_pokemon_move = next(
            (move for move in captured_pokemon.moves if move.name == pokemon_move), None
        )

        if not trainer_pokemon_move:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Move not found in trainer pokemon moves',
            )

        return GetBattlePokemonSchema(
            pokemon=self.business.convert_captured_pokemon_to_pokemon_stats(captured_pokemon),
            pokemon_move=trainer_pokemon_move,
        )
