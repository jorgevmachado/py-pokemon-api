from app.domain.pokemon.external.schemas.growth_rate import (
    PokemonExternalGrowthRateDescriptionSchemaResponse,
)


class PokemonGrowthRateBusiness:
    @staticmethod
    def ensure_description_message(
        descriptions: list[PokemonExternalGrowthRateDescriptionSchemaResponse],
    ) -> str:
        description = next(
            (entry for entry in descriptions if entry.language.name == 'en'),
            descriptions[0] if descriptions else None,
        )
        return description.description if description else ''
