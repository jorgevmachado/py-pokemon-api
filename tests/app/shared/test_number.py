from app.shared.number import ensure_order_number


class TestNumberEnsureOrderNumber:
    @staticmethod
    def test_ensure_order_number():
        test_cases = [
            ('https://pokeapi.co/api/v2/pokemon/1/', 1),
            ('https://pokeapi.co/api/v2/pokemon/2/', 2),
            ('https://pokeapi.co/api/v2/pokemon/3/', 3),
            ('https://pokeapi.co/api/v2/pokemon/4/', 4),
            ('https://pokeapi.co/api/v2/pokemon/5/', 5),
        ]

        for url, expected_order in test_cases:
            assert ensure_order_number(url) == expected_order

    @staticmethod
    def test_ensure_order_number_not_has_url():
        url = None
        assert ensure_order_number(url) == 0
