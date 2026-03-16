from app.shared.utils.image import ensure_external_image


class TestImageEnsureExternalImage:
    @staticmethod
    def test_ensure_external_image():
        image = 'https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/detail/1.png'
        assert ensure_external_image(1) == image

    @staticmethod
    def test_ensure_external_image_not_has_order():
        assert not ensure_external_image(None)
