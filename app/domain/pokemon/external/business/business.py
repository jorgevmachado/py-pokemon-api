from typing import Optional

from app.domain.pokemon.external.business.schemas import (
    EnsureAttributesSchemaResult,
    EnsureSpecieAttributesSchemaResult,
    EnsureStaticsAttributesSchemaResult,
)
from app.domain.pokemon.external.enums.service_enum import ServiceType
from app.domain.pokemon.external.schemas import PokemonExternalByNameSpritesSchemaResponse
from app.domain.pokemon.external.schemas.name import (
    PokemonExternalByNameSchemaResponse,
    PokemonExternalByNameStatsSchemaResponse,
)
from app.domain.pokemon.external.schemas.specie import PokemonExternalSpecieSchemaResponse


class PokemonExternalBusiness:
    @staticmethod
    def ensure_image(sprites: PokemonExternalByNameSpritesSchemaResponse | None) -> str:
        if not sprites:
            return ''

        front_default = sprites.front_default
        dream_world = sprites.other.dream_world.front_default
        return front_default if front_default else dream_world

    @staticmethod
    def ensure_statistics_attributes(
        stats: list[PokemonExternalByNameStatsSchemaResponse],
    ) -> EnsureStaticsAttributesSchemaResult:
        hp = 0
        speed = 0
        attack = 0
        defense = 0
        special_attack = 0
        special_defense = 0
        for stat in stats:
            if stat.stat.name == 'hp':
                hp = stat.base_stat
            if stat.stat.name == 'speed':
                speed = stat.base_stat
            if stat.stat.name == 'attack':
                attack = stat.base_stat
            if stat.stat.name == 'defense':
                defense = stat.base_stat
            if stat.stat.name == 'special-attack':
                special_attack = stat.base_stat
            if stat.stat.name == 'special-defense':
                special_defense = stat.base_stat
        return EnsureStaticsAttributesSchemaResult(
            hp=hp,
            speed=speed,
            attack=attack,
            defense=defense,
            special_attack=special_attack,
            special_defense=special_defense,
        )

    @staticmethod
    def ensure_attributes(
        pokemon_name: PokemonExternalByNameSchemaResponse,
    ) -> EnsureAttributesSchemaResult:
        height = pokemon_name.height if pokemon_name.height else 0
        weight = pokemon_name.weight if pokemon_name.weight else 0
        base_experience = pokemon_name.base_experience if pokemon_name.base_experience else 0
        stats = PokemonExternalBusiness.ensure_statistics_attributes(pokemon_name.stats)
        return EnsureAttributesSchemaResult(
            hp=stats.hp,
            speed=stats.speed,
            attack=stats.attack,
            defense=stats.defense,
            special_attack=stats.special_attack,
            special_defense=stats.special_defense,
            height=height,
            weight=weight,
            base_experience=base_experience,
        )

    @staticmethod
    def ensure_specie_attributes(
        pokemon_specie: PokemonExternalSpecieSchemaResponse,
    ) -> EnsureSpecieAttributesSchemaResult:
        habitat = None

        shape_name = None
        shape_url = None
        evolution_chain_url = None
        evolves_from_species = None

        if pokemon_specie.habitat:
            habitat = pokemon_specie.habitat.name

        if pokemon_specie.shape:
            shape_name = pokemon_specie.shape.name
            shape_url = pokemon_specie.shape.url

        if pokemon_specie.evolution_chain:
            evolution_chain_url = pokemon_specie.evolution_chain.url

        if pokemon_specie.evolves_from_species:
            evolves_from_species = pokemon_specie.evolves_from_species.name

        return EnsureSpecieAttributesSchemaResult(
            habitat=habitat,
            is_baby=pokemon_specie.is_baby,
            shape_name=shape_name,
            shape_url=shape_url,
            is_mythical=pokemon_specie.is_mythical,
            gender_rate=pokemon_specie.gender_rate,
            is_legendary=pokemon_specie.is_legendary,
            capture_rate=pokemon_specie.capture_rate,
            hatch_counter=pokemon_specie.hatch_counter,
            base_happiness=pokemon_specie.base_happiness,
            evolution_chain_url=evolution_chain_url,
            evolves_from_species=evolves_from_species,
            has_gender_differences=pokemon_specie.has_gender_differences,
        )

    @staticmethod
    def build_url(
        base_url: str,
        url: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[int] = None,
        service_type: Optional[ServiceType] = ServiceType.POKEMON,
    ) -> str | None:
        if url is not None:
            return url

        param = order or name

        if not param:
            return None

        path_map = {
            ServiceType.TYPE: 'type',
            ServiceType.MOVE: 'move',
            ServiceType.SPECIE: 'pokemon-species',
            ServiceType.EVOLUTION: 'evolution-chain',
            ServiceType.GROWTH_RATE: 'growth-rate',
            ServiceType.POKEMON: 'pokemon',
        }

        path = path_map.get(service_type, 'pokemon')
        return f'{base_url}/{path}/{param}'
