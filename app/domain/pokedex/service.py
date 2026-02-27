from datetime import datetime
from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokedex.repository import PokedexRepository
from app.domain.pokedex.schema import CreatePokedexSchema
from app.domain.pokemon.business import PokemonBusiness
from app.models import CapturedPokemon, Pokedex, Pokemon, User

Session = Annotated[AsyncSession, Depends(get_session)]


class PokedexService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = PokedexRepository(session)
        self.business = PokemonBusiness()

    async def initialize(
        self,
        user: User,
        pokemon: Optional[Pokemon],
        pokemons: list[Pokemon],
    ) -> list[Pokedex]:
        try:
            new_entries: list[Pokedex] = []
            pokemon_name = pokemon.name if pokemon else None

            existing_pokemon_ids = await self.repository.find_by_trainer(user.id)

            for item in pokemons:
                if item.id in existing_pokemon_ids:
                    continue

                discovered = item.name == pokemon_name

                stats = self.business.calculate_pokemon_stats(pokemon=item)
                create_pokedex = CreatePokedexSchema(
                    hp=stats['hp'],
                    wins=stats['wins'],
                    level=stats['level'],
                    iv_hp=stats['iv_hp'],
                    ev_hp=stats['ev_hp'],
                    losses=stats['losses'],
                    max_hp=stats['max_hp'],
                    battles=stats['battles'],
                    nickname=stats['nickname'],
                    iv_speed=stats['iv_speed'],
                    ev_speed=stats['ev_speed'],
                    iv_attack=stats['iv_attack'],
                    ev_attack=stats['ev_attack'],
                    iv_defense=stats['iv_defense'],
                    ev_defense=stats['ev_defense'],
                    experience=stats['experience'],
                    iv_special_attack=stats['iv_special_attack'],
                    ev_special_attack=stats['ev_special_attack'],
                    iv_special_defense=stats['iv_special_defense'],
                    ev_special_defense=stats['ev_special_defense'],
                    discovered=discovered,
                    discovered_at=datetime.now(),
                    pokemon_id=item.id,
                    trainer_id=user.id,
                )

                new_entry = await self.repository.create(create_pokedex)
                new_entries.append(new_entry)

            return new_entries
        except Exception as e:
            print(f'# => pokedex => service => initialize => error => {e}')
        return []

    async def initialize_pokedex_entry(
        self,
        pokemon: Pokemon,
        user: User,
        level: int = 1,
    ) -> Pokedex:
        """
        Initialize a new pokedex entry for a user.

        This method creates a new pokedex record with calculated stats
        based on the pokemon's base stats and growth rate formula.
        Each pokemon has unique IVs (Individual Values) to represent
        genetic differences.

        Args:
            pokemon: Pokemon to add to pokedex
            user: User that discovered the pokemon
            level: Initial level (default 1)

        Returns:
            Pokedex entry with calculated and unique stats
        """
        # Calculate stats using pokemon's base stats and growth rate formula
        stats = self.business.calculate_pokemon_stats(
            pokemon=pokemon,
            level=level,
        )

        pokedex_entry = Pokedex(
            hp=stats['hp'],
            wins=stats['wins'],
            level=stats['level'],
            iv_hp=stats['iv_hp'],
            ev_hp=stats['ev_hp'],
            losses=stats['losses'],
            max_hp=stats['max_hp'],
            battles=stats['battles'],
            nickname=stats['nickname'],
            iv_speed=stats['iv_speed'],
            ev_speed=stats['ev_speed'],
            iv_attack=stats['iv_attack'],
            ev_attack=stats['ev_attack'],
            iv_defense=stats['iv_defense'],
            ev_defense=stats['ev_defense'],
            experience=stats['experience'],
            iv_special_attack=stats['iv_special_attack'],
            ev_special_attack=stats['ev_special_attack'],
            iv_special_defense=stats['iv_special_defense'],
            ev_special_defense=stats['ev_special_defense'],
            discovered=True,
            discovered_at=datetime.utcnow(),
            pokemon_id=pokemon.id,
            trainer_id=user.id,
        )

        self.session.add(pokedex_entry)
        await self.session.commit()
        await self.session.refresh(pokedex_entry)

        return pokedex_entry

    async def capture_pokemon(
        self,
        pokemon: Pokemon,
        user: User,
        level: int = 1,
    ) -> CapturedPokemon:
        """
        Create a new captured pokemon entry for a user.

        This method creates a captured pokemon record with calculated stats.
        Each captured pokemon has unique stats based on its IVs (genetics),
        making each pokemon different even if same species.

        Args:
            pokemon: Pokemon that was captured
            user: User that caught the pokemon
            level: Initial level (default 1)

        Returns:
            CapturedPokemon entry with unique calculated stats
        """
        # Calculate stats using pokemon's base stats and growth rate formula
        stats = self.business.calculate_pokemon_stats(
            pokemon=pokemon,
            level=level,
        )

        captured_pokemon = CapturedPokemon(
            pokemon_id=pokemon.id,
            trainer_id=user.id,
            hp=stats['hp'],
            max_hp=stats['max_hp'],
            attack=stats['attack'],
            defense=stats['defense'],
            special_attack=stats['special_attack'],
            special_defense=stats['special_defense'],
            speed=stats['speed'],
            level=stats['level'],
            experience=stats['experience'],
            iv_hp=stats['iv_hp'],
            iv_attack=stats['iv_attack'],
            iv_defense=stats['iv_defense'],
            iv_special_attack=stats['iv_special_attack'],
            iv_special_defense=stats['iv_special_defense'],
            iv_speed=stats['iv_speed'],
            ev_hp=stats['ev_hp'],
            ev_attack=stats['ev_attack'],
            ev_defense=stats['ev_defense'],
            ev_special_attack=stats['ev_special_attack'],
            ev_special_defense=stats['ev_special_defense'],
            ev_speed=stats['ev_speed'],
            wins=stats['wins'],
            losses=stats['losses'],
            battles=stats['battles'],
            nickname=stats['nickname'],
            captured_at=datetime.now(),
        )

        self.session.add(captured_pokemon)
        await self.session.commit()
        await self.session.refresh(captured_pokemon)

        return captured_pokemon

    async def add_pokemon_to_pokedex_and_capture(
        self,
        pokemon: Pokemon,
        user: User,
        level: int = 1,
    ) -> tuple[Pokedex, CapturedPokemon]:
        """
        Add pokemon to both pokedex (discovered) and captured_pokemon list.

        This is the main method to use when a user captures a pokemon.
        It creates both:
        - Pokedex entry: Records the discovery
        - CapturedPokemon entry: The actual pokemon in the user's collection

        Each pokemon receives unique IVs making them genetically different.

        Args:
            pokemon: Pokemon to add
            user: User that caught the pokemon
            level: Initial level (default 1)

        Returns:
            Tuple of (Pokedex entry, CapturedPokemon entry)
        """
        # Create pokedex entry (discovery record)
        pokedex_entry = await self.initialize_pokedex_entry(
            pokemon=pokemon,
            user=user,
            level=level,
        )

        captured_entry = await self.capture_pokemon(
            pokemon=pokemon,
            user=user,
            level=level,
        )

        return pokedex_entry, captured_entry
