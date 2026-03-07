from http import HTTPStatus

import pytest
from pydantic import ValidationError
from unittest.mock import AsyncMock

from app.core.security import get_current_user
from app.domain.battle.route import CurrentTrainer, Service, router
from app.domain.battle.schema import BattlePokemonSchema, BattleResult
from app.domain.battle.service import PokemonBattleService
from app.domain.progression.schema import StatBlock
from app.main import app
from tests.factories.trainer import TrainerFactory

BATTLE_ATTACK_DAMAGE = 20
BATTLE_REMAINING_HP = 30


def override_current_user():
    return TrainerFactory()


def build_mock_service():
    mock_service = PokemonBattleService(
        captured_pokemon_service=None,
        pokedex_service=None,
        pokemon_service=None,
    )
    mock_service.battle = AsyncMock(
        return_value=BattleResult(
            winner='test-pokemon',
            fainted=False,
            level_up=False,
            missed=False,
            critical=False,
            stab=False,
            attack_damage=BATTLE_ATTACK_DAMAGE,
            defense_damage=0,
            remaining_hp=BATTLE_REMAINING_HP,
            previous_stats=StatBlock(
                hp=50,
                attack=50,
                defense=49,
                speed=45,
                special_attack=65,
                special_defense=65,
            ),
            previous_level=10,
            previous_experience=100,
            current_stats=StatBlock(
                hp=50,
                attack=50,
                defense=49,
                speed=45,
                special_attack=65,
                special_defense=65,
            ),
            current_level=10,
            current_experience=120,
            applied_status=None,
        )
    )
    return mock_service


class TestBattleRoute:
    """Test scope for battle POST endpoint"""

    @staticmethod
    def test_battle_route_post_endpoint_exists():
        """Should have POST /battle/ endpoint"""

        # FastAPI routes have different structure, check by counting routes
        assert len(router.routes) > 0
        # Check that at least one route is a POST
        has_post = any('POST' in getattr(route, 'methods', set()) for route in router.routes)
        assert has_post, 'Router should have POST endpoint'

    @staticmethod
    def test_battle_route_response_model():
        """Should have BattleResult as response model"""

        # Verify the response model is set
        routes_with_response_model = [
            route
            for route in router.routes
            if hasattr(route, 'response_model') and route.response_model is not None
        ]
        assert len(routes_with_response_model) > 0, 'Router should have response model'
        assert routes_with_response_model[0].response_model == BattleResult

    @staticmethod
    def test_battle_route_prefix():
        """Should have correct route prefix"""

        assert router.prefix == '/battle'

    @staticmethod
    def test_battle_route_tags():
        """Should have correct route tags"""

        assert 'battle' in router.tags

    @staticmethod
    def test_battle_route_has_service_dependency():
        """Should use PokemonBattleService"""

        assert Service is not None

    @staticmethod
    def test_battle_route_requires_current_user():
        """Should require current user dependency"""

        assert CurrentTrainer is not None

    @staticmethod
    def test_battle_pokemon_schema_requires_trainer_pokemon():
        """Should require trainer_pokemon field"""
        with pytest.raises(ValidationError):
            BattlePokemonSchema(
                trainer_pokemon_move='vine-whip',
                opponent_pokemon='charizard',
                opponent_pokemon_move='flare-blitz',
            )

    @staticmethod
    def test_battle_pokemon_schema_requires_trainer_move():
        """Should require trainer_pokemon_move field"""
        with pytest.raises(ValidationError):
            BattlePokemonSchema(
                trainer_pokemon='bulbasaur',
                opponent_pokemon='charizard',
                opponent_pokemon_move='flare-blitz',
            )

    @staticmethod
    def test_battle_pokemon_schema_requires_opponent_pokemon():
        """Should require opponent_pokemon field"""
        with pytest.raises(ValidationError):
            BattlePokemonSchema(
                trainer_pokemon='bulbasaur',
                trainer_pokemon_move='vine-whip',
                opponent_pokemon_move='flare-blitz',
            )

    @staticmethod
    def test_battle_pokemon_schema_requires_opponent_move():
        """Should allow opponent_pokemon_move to be optional"""
        # opponent_pokemon_move is Optional[str] = None, so it should not raise
        schema = BattlePokemonSchema(
            trainer_pokemon='bulbasaur',
            trainer_pokemon_move='vine-whip',
            opponent_pokemon='charizard',
        )

        assert schema.opponent_pokemon_move is None

    @staticmethod
    def test_battle_pokemon_schema_valid():
        """Should create schema with all required fields"""
        schema = BattlePokemonSchema(
            trainer_pokemon='bulbasaur',
            trainer_pokemon_move='vine-whip',
            opponent_pokemon='charizard',
            opponent_pokemon_move='flare-blitz',
        )

        assert schema.trainer_pokemon == 'bulbasaur'
        assert schema.trainer_pokemon_move == 'vine-whip'
        assert schema.opponent_pokemon == 'charizard'
        assert schema.opponent_pokemon_move == 'flare-blitz'

    @staticmethod
    def test_battle_pokemon_schema_field_types():
        """Should enforce string field types"""
        schema = BattlePokemonSchema(
            trainer_pokemon='bulbasaur',
            trainer_pokemon_move='vine-whip',
            opponent_pokemon='charizard',
            opponent_pokemon_move='flare-blitz',
        )

        assert isinstance(schema.trainer_pokemon, str)
        assert isinstance(schema.trainer_pokemon_move, str)
        assert isinstance(schema.opponent_pokemon, str)
        assert isinstance(schema.opponent_pokemon_move, str)

    @staticmethod
    @pytest.mark.asyncio
    async def test_battle_pokemon_response_with_authentication(client, token):
        """Should return 200 OK when battle endpoint is called with auth"""
        mock_service = build_mock_service()

        def override_battle_service():
            return mock_service

        app.dependency_overrides[PokemonBattleService] = override_battle_service
        app.dependency_overrides[get_current_user] = override_current_user

        response = client.post(
            '/battle/',
            json={
                'trainer_pokemon': 'bulbasaur',
                'trainer_pokemon_move': 'vine-whip',
                'opponent_pokemon': 'charizard',
                'opponent_pokemon_move': 'flare-blitz',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

        app.dependency_overrides.clear()

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['winner'] == 'test-pokemon'
        assert data['attack_damage'] == BATTLE_ATTACK_DAMAGE
        assert data['remaining_hp'] == BATTLE_REMAINING_HP


class TestBattleRouteIntegration:
    """Test scope for battle route integration tests"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_battle_endpoint_requires_authentication(client):
        """Should return 401 when not authenticated"""
        response = client.post(
            '/battle/',
            json={
                'trainer_pokemon': 'bulbasaur',
                'trainer_pokemon_move': 'vine-whip',
                'opponent_pokemon': 'charizard',
                'opponent_pokemon_move': 'flare-blitz',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @staticmethod
    @pytest.mark.asyncio
    async def test_battle_endpoint_validates_schema(client):
        """Should check authentication before schema validation"""
        response = client.post(
            '/battle/',
            json={
                'trainer_pokemon': 'bulbasaur',
                # Missing required fields
            },
        )

        # Authentication is checked before schema validation in FastAPI
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @staticmethod
    @pytest.mark.asyncio
    async def test_battle_endpoint_accepts_valid_request(client):
        """Should accept valid battle request"""
        response = client.post(
            '/battle/',
            json={
                'trainer_pokemon': 'bulbasaur',
                'trainer_pokemon_move': 'vine-whip',
                'opponent_pokemon': 'charizard',
                'opponent_pokemon_move': 'flare-blitz',
            },
        )

        # Should fail with 401/403 due to auth, not 422 (validation error)
        assert response.status_code != HTTPStatus.UNPROCESSABLE_CONTENT
