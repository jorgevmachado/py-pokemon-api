from typing import Annotated

from fastapi import Depends

from app.domain.move.business import PokemonMoveBusiness
from app.domain.move.model import PokemonMove
from app.domain.move.repository import PokemonMoveRepository
from app.domain.move.schema import CreatePokemonMoveSchema
from app.domain.pokemon.external.schemas import (
    PokemonExternalBaseMoveSchemaResponse,
)
from app.domain.pokemon.external.service import PokemonExternalService
from app.shared.number import ensure_order_number

Repository = Annotated[PokemonMoveRepository, Depends()]


class PokemonMoveService:
    def __init__(self, repository: Repository):
        self.repository = repository
        self.external_service = PokemonExternalService()

    async def verify_pokemon_move(
        self, moves: list[PokemonExternalBaseMoveSchemaResponse]
    ) -> list[PokemonMove]:
        try:
            result_pokemon_moves = []

            for move_response in moves:
                url = move_response.move.url
                name = move_response.move.name
                order = ensure_order_number(url)

                db_pokemon_move = await self.repository.find_one_by_order(order=order)
                if db_pokemon_move:
                    result_pokemon_moves.append(db_pokemon_move)
                    continue

                external_move_data = await self.external_service.pokemon_external_move_by_name(
                    name
                )

                if not external_move_data:
                    continue

                effect_message = PokemonMoveBusiness().ensure_effect_message(
                    external_move_data.effect_entries
                )

                pokemon_move_data = CreatePokemonMoveSchema(
                    pp=external_move_data.pp,
                    url=url,
                    type=external_move_data.type.name,
                    name=external_move_data.name,
                    order=order,
                    power=external_move_data.power or 0,
                    target=external_move_data.target.name,
                    effect=effect_message.effect,
                    priority=external_move_data.priority,
                    accuracy=external_move_data.accuracy or 0,
                    short_effect=effect_message.short_effect,
                    damage_class=external_move_data.damage_class.name,
                    effect_chance=external_move_data.effect_chance,
                )
                pokemon_move = await self.repository.create(pokemon_move_data)
                result_pokemon_moves.append(pokemon_move)

            return result_pokemon_moves
        except Exception as e:
            print(f'# => PokemonMoveService => verify_pokemon_move => error => {e}')
            return []
