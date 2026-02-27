# Documentação - Sistema de Pokedex e Pokémon Capturados

## Visão Geral

O sistema gerencia dois tipos de registros para cada usuário:

1. **Pokedex**: Registro de descobertas de pokémons (quais espécies o usuário já viu)
2. **CapturedPokemon**: Pokémons capturados/na coleção do usuário

## Componentes Principais

### 1. PokemonBusiness.calculate_pokemon_stats()

Calcula os atributos iniciais de um pokémon baseado em:
- **Stats base**: Força bruta da espécie (HP, Ataque, Defesa, etc)
- **IVs (Individual Values)**: Valores genéticos únicos (0-31 por stat) - gerados aleatoriamente
- **EVs (Effort Values)**: Valores de treinamento (começam em 0)
- **Growth Rate Formula**: Fórmula específica da espécie para calcular experiência

#### Fórmula de Cálculo de Stats:
```
Stat = ((2 * Base + IV + EV/4) * Level / 100) + Modificador

Modificador = Level + 5 (para HP)
Modificador = 5 (para outros stats)
```

#### Exemplo:
```python
# Mesmo Pikachu, diferentes IVs = pokémons diferentes
pikachu1_stats = {
    'hp': 35,
    'iv_hp': 15,
    'iv_attack': 28,
    # ... outros IVs únicos
}

pikachu2_stats = {
    'hp': 37,
    'iv_hp': 22,
    'iv_attack': 18,
    # ... outros IVs únicos
}
```

### 2. PokedexService

Gerencia as entradas de pokedex (descobertas).

#### Métodos principais:

```python
# Inicializar entrada de pokedex
pokedex_entry = await pokedex_service.initialize_pokedex_entry(
    pokemon=bulbasaur,
    user=user,
    level=1
)

# Capturar pokémon (cria na pokedex e em captured_pokemon)
pokedex_entry, captured = await pokedex_service.add_pokemon_to_pokedex_and_capture(
    pokemon=pikachu,
    user=user,
    level=1
)
```

### 3. CapturedPokemonService

Gerencia pokémons capturados e estatísticas de batalha.

#### Métodos principais:

```python
# Criar pokémon capturado
captured = await captured_service.create_captured_pokemon(
    pokemon=charizard,
    user=user,
    level=5
)

# Registrar vitória em batalha
captured = await captured_service.record_battle_win(
    captured_pokemon=captured,
    exp_gained=100
)

# Registrar derrota em batalha
captured = await captured_service.record_battle_loss(
    captured_pokemon=captured
)

# Adicionar effort value (treinamento)
captured = await captured_service.add_effort_value(
    captured_pokemon=captured,
    ev_type='attack',
    ev_amount=1
)

# Recalcular stats após level up
captured = await captured_service.recalculate_stats_for_level_up(
    captured_pokemon=captured,
    pokemon=charizard
)
```

## Fluxo de Captura de Pokémon

```
┌─────────────────────────────────────────┐
│  Usuário encontra pokémon na natureza   │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Validar pokémon e usuário              │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  calculate_pokemon_stats()              │
│  - Gera IVs aleatórios (0-31)          │
│  - Calcula stats base + IVs            │
│  - Calcula experiência inicial         │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Criar entrada Pokedex (descoberta)     │
│  + Pokémon Capturado (coleção)         │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Adicionar à coleção do usuário         │
└─────────────────────────────────────────┘
```

## Diferenças Entre Dois Pokémons da Mesma Espécie

Cada pokémon capturado é **único** porque:

1. **IVs Únicos**: Gerados aleatoriamente durante captura
   - HP: 0-31
   - Attack: 0-31
   - Defense: 0-31
   - Special Attack: 0-31
   - Special Defense: 0-31
   - Speed: 0-31

2. **EVs Diferentes**: Ganhos através de treinamento (batalhas)

3. **Stats Finais**: Resultado da combinação de base + IV + EV

### Exemplo Prático:
```
Pikachu #1 (stats baixos):
- HP: 35 (base) + IV:3 + EV:0 = 35
- Attack: 55 (base) + IV:5 + EV:0 = 55

Pikachu #2 (stats altos):
- HP: 35 (base) + IV:29 + EV:0 = 37
- Attack: 55 (base) + IV:31 + EV:0 = 59

Diferença: Pikachu #2 será mais forte!
```

## Growth Rate (Fórmula de Crescimento)

A fórmula de crescimento é específica por pokémon e determina quanto XP é necessário para cada level.

### Exemplos de Fórmulas:
- **Fast**: x^3 / 5 (Gengar)
- **Medium-Fast**: x^3 (Pikachu - padrão)
- **Medium-Slow**: x^3 - 6x^2 + 12x - 8 (Bulbasaur)
- **Slow**: (5x^3) / 4 (Gyarados)

### Cálculo de Experiência:
```python
# Growth rate formula é armazenado como string
growth_rate.formula = "x^3"  # Pikachu

# Na captura, experiência é calculada:
experience = _calculate_experience(growth_rate, level=1)
# Resultado: 1^3 = 1 XP necessário para level 2
```

## Atributos de Bataille

Cada pokémon capturado rastreia:
- **wins**: Vitórias em batalha
- **losses**: Derrotas em batalha
- **battles**: Total de batalhas (wins + losses)
- **experience**: XP acumulado
- **level**: Nível atual

## Resumo de Funcionalidades

✅ **IVs Únicos**: Cada pokémon é geneticamente único
✅ **EVs Treináveis**: Ganhar pontos de treinamento em batalhas
✅ **Growth Rate**: Fórmulas específicas por espécie
✅ **Histórico de Batalhas**: Rastreamento de vitórias/derrotas
✅ **Recalculação de Stats**: Atualizar stats após level up
✅ **Pokedex vs Capturado**: Separação clara de descoberta vs coleção

