# Exemplos de Uso - Sistema de Pokedex e Pokémon Capturados

## Exemplo 1: Capturar um Pokémon

```python
from app.domain.pokedex.service import PokedexService
from app.domain.captured_pokemon.service import CapturedPokemonService
from app.models import User, Pokemon

# Setup
pokedex_service = PokedexService(session)
captured_service = CapturedPokemonService(session)

# Buscar pokémon e usuário
pikachu = await pokemon_repository.find_one(name='pikachu')
user = await user_repository.find_one(id=user_id)

# Método 1: Adicionar à pokedex e capturar simultaneamente
pokedex_entry, captured_pokemon = await pokedex_service.add_pokemon_to_pokedex_and_capture(
    pokemon=pikachu,
    user=user,
    level=5
)

print(f"Pokémon capturado: {captured_pokemon.nickname}")
print(f"HP: {captured_pokemon.hp}")
print(f"Ataque: {captured_pokemon.attack}")
print(f"IV HP: {captured_pokemon.iv_hp} (genético)")
print(f"IV Ataque: {captured_pokemon.iv_attack} (genético)")
```

## Exemplo 2: Capturar Dois Pikachus Diferentes

```python
# Pikachu #1
pikachu1_data, pikachu1_captured = await pokedex_service.add_pokemon_to_pokedex_and_capture(
    pokemon=pikachu,
    user=user,
    level=5
)

# Pikachu #2
pikachu2_data, pikachu2_captured = await pokedex_service.add_pokemon_to_pokedex_and_capture(
    pokemon=pikachu,
    user=user,
    level=5
)

# Comparar stats - Ambos são Pikachu, mas diferentes!
print("=== Pikachu #1 ===")
print(f"HP: {pikachu1_captured.hp}")
print(f"Ataque: {pikachu1_captured.attack}")
print(f"IV HP: {pikachu1_captured.iv_hp}")
print(f"IV Ataque: {pikachu1_captured.iv_attack}")

print("\n=== Pikachu #2 ===")
print(f"HP: {pikachu2_captured.hp}")
print(f"Ataque: {pikachu2_captured.attack}")
print(f"IV HP: {pikachu2_captured.iv_hp}")
print(f"IV Ataque: {pikachu2_captured.iv_attack}")

# Resultado esperado:
# Pikachu #1 pode ter IV HP: 15, IV Ataque: 28
# Pikachu #2 pode ter IV HP: 22, IV Ataque: 18
# Mesmo sendo a mesma espécie, terão stats finais diferentes!
```

## Exemplo 3: Usar em Batalha

```python
# Pikachu venceu uma batalha
pikachu_updated = await captured_service.record_battle_win(
    captured_pokemon=pikachu1_captured,
    exp_gained=150
)

print(f"Vitórias: {pikachu_updated.wins}")
print(f"Experiência: {pikachu_updated.experience}")

# Pikachu perdeu uma batalha
pikachu_updated = await captured_service.record_battle_loss(
    captured_pokemon=pikachu1_captured
)

print(f"Derrotas: {pikachu_updated.losses}")
print(f"Total de batalhas: {pikachu_updated.battles}")
```

## Exemplo 4: Treinar Pokémon

```python
# Pikachu ganha EV em Ataque após derrotar um pokémon de ataque
pikachu_updated = await captured_service.add_effort_value(
    captured_pokemon=pikachu1_captured,
    ev_type='attack',
    ev_amount=3
)

print(f"EV Ataque: {pikachu_updated.ev_attack}")

# Pikachu sobe de level
pikachu_updated.level = 6

# Recalcular stats com novo level e EVs
pikachu_updated = await captured_service.recalculate_stats_for_level_up(
    captured_pokemon=pikachu_updated,
    pokemon=pikachu
)

print(f"Level: {pikachu_updated.level}")
print(f"Novo HP: {pikachu_updated.hp}")
print(f"Novo Ataque: {pikachu_updated.attack}")
```

## Exemplo 5: Comparar Força de Dois Pokémons

```python
# Calcular força baseada em stats
def calculate_power_level(pokemon):
    return (
        pokemon.hp +
        pokemon.attack * 1.5 +
        pokemon.defense +
        pokemon.special_attack * 1.5 +
        pokemon.special_defense +
        pokemon.speed * 1.2
    )

pikachu1_power = calculate_power_level(pikachu1_captured)
pikachu2_power = calculate_power_level(pikachu2_captured)

print(f"Pikachu #1 Poder: {pikachu1_power:.2f}")
print(f"Pikachu #2 Poder: {pikachu2_power:.2f}")

if pikachu1_power > pikachu2_power:
    print("Pikachu #1 é mais forte!")
else:
    print("Pikachu #2 é mais forte!")
```

## Exemplo 6: Growth Rate - Experiência Necessária para Level Up

```python
# Pikachu usa fórmula: x^3
pikachu_growth = pikachu.growth_rate  # formula: "x^3"

# XP necessário para cada level
levels = {
    1: _calculate_experience(pikachu_growth, 1),  # 1
    2: _calculate_experience(pikachu_growth, 2),  # 8
    3: _calculate_experience(pikachu_growth, 3),  # 27
    10: _calculate_experience(pikachu_growth, 10),  # 1000
    50: _calculate_experience(pikachu_growth, 50),  # 125000
}

print("XP necessário por nível:")
for level, xp in levels.items():
    print(f"  Level {level}: {xp} XP")
```

## Notas Importantes

1. **IVs são gerados uma única vez**: Quando um pokémon é capturado, seus IVs são definidos e nunca mudam
2. **EVs mudam com treinamento**: Acumulam com vitórias em batalha
3. **Stats recalculam com level**: Usar `recalculate_stats_for_level_up` ao subir de level
4. **Cada pokémon é único**: Mesmo dois Pikachus terão genetic differences diferentes
5. **Growth rate é por espécie**: Toda espécie tem uma fórmula de crescimento fixa

## Estrutura de Dados Esperada

### Pokedex Entry
```python
{
    'id': 'uuid',
    'pokemon_id': 'pokemon-uuid',
    'trainer_id': 'user-uuid',
    'hp': 35,
    'max_hp': 35,
    'attack': 55,
    'defense': 40,
    'special_attack': 50,
    'special_defense': 50,
    'speed': 90,
    'level': 5,
    'experience': 125,
    'iv_hp': 15,
    'iv_attack': 28,
    'iv_defense': 12,
    'iv_special_attack': 20,
    'iv_special_defense': 18,
    'iv_speed': 25,
    'ev_hp': 0,
    'ev_attack': 0,
    'ev_defense': 0,
    'ev_special_attack': 0,
    'ev_special_defense': 0,
    'ev_speed': 0,
    'wins': 0,
    'losses': 0,
    'battles': 0,
    'nickname': 'pikachu',
    'discovered': True,
    'discovered_at': datetime,
}
```

### CapturedPokemon Entry
```python
{
    'id': 'uuid',
    'pokemon_id': 'pokemon-uuid',
    'trainer_id': 'user-uuid',
    'hp': 35,
    'max_hp': 35,
    'attack': 55,
    'defense': 40,
    'special_attack': 50,
    'special_defense': 50,
    'speed': 90,
    'level': 5,
    'experience': 125,
    'iv_hp': 15,
    'iv_attack': 28,
    'iv_defense': 12,
    'iv_special_attack': 20,
    'iv_special_defense': 18,
    'iv_speed': 25,
    'ev_hp': 0,
    'ev_attack': 0,
    'ev_defense': 0,
    'ev_special_attack': 0,
    'ev_special_defense': 0,
    'ev_speed': 0,
    'wins': 0,
    'losses': 0,
    'battles': 0,
    'nickname': 'pikachu',
    'captured_at': datetime,
}
```

