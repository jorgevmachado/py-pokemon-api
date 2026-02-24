def ensure_external_image(order: int | None) -> str:
    if not order:
        return ''
    return f'https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/detail/{order}.png'
