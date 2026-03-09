## Implementação de Random Moves para Captured Pokemon

### Resumo

Foi implementada a funcionalidade de adicionar **movimentos aleatórios** ao capturar um Pokémon. A solução segue as seguintes regras:

- **1 movimento disponível**: O movimento é automaticamente adicionado
- **2-4 movimentos disponíveis**: Todos os movimentos são adicionados
- **5 ou mais movimentos disponíveis**: Exatamente 4 movimentos são selecionados aleatoriamente

### Arquivos Modificados e Criados

#### 1. **Arquivo Utilitário** - `app/shared/moves_utils.py` (NOVO)

Contém a função `select_random_moves()` que implementa a lógica de seleção aleatória de movimentos:

```python
def select_random_moves(
    available_moves: Sequence[PokemonMove],
    min_moves: int = 1,
    max_moves: int = 4,
) -> list[PokemonMove]:
```

**Lógica:**
- Se não há movimentos, retorna lista vazia
- Se há ≤ 4 movimentos, retorna todos
- Se há > 4 movimentos, seleciona aleatoriamente 4 usando `random.sample()`

#### 2. **Serviço** - `app/domain/captured_pokemon/service.py` (MODIFICADO)

Adicionado import da função utilitária e modificado o método `create()`:

```python
async def create(
    self,
    pokemon: Pokemon,
    trainer: Trainer,
    nickname: str = None,
):
    # ... código existente ...
    captured_pokemon = await self.repository.create(create_captured_pokemon)

    # Assign random moves to captured pokemon
    selected_moves = select_random_moves(pokemon.moves)
    captured_pokemon.moves = selected_moves
    await self.session.commit()
    await self.session.refresh(captured_pokemon)

    return captured_pokemon
```

**Fluxo:**
1. Cria o `CapturedPokemon` no repositório
2. Seleciona movimentos aleatórios do Pokémon base
3. Atribui os movimentos à relação `captured_pokemon.moves`
4. Persiste as alterações no banco de dados

#### 3. **Testes Unitários** - `tests/app/shared/test_moves_utils.py` (NOVO)

Contém 9 testes abrangentes para validar a função de seleção aleatória:

- `test_empty_moves_list()` - Lista vazia retorna []
- `test_single_move()` - 1 movimento é retornado
- `test_less_than_max_moves()` - 3 movimentos retorna 3
- `test_exactly_max_moves()` - 4 movimentos retorna 4
- `test_more_than_max_moves()` - 5 movimentos retorna 4
- `test_five_moves_returns_four()` - Validação específica para 5 movimentos
- `test_many_moves_respects_max_moves()` - 10 movimentos retorna 4
- `test_custom_min_max_moves()` - Parâmetros customizados funcionam
- `test_randomness()` - Múltiplas chamadas retornam diferentes subsets

#### 4. **Testes de Integração** - `tests/app/domain/captured_pokemon/test_service.py` (MODIFICADO)

Adicionados 6 testes de integração ao método `create()`:

- `test_create_assigns_random_moves_when_pokemon_has_one_move()`
- `test_create_assigns_all_moves_when_pokemon_has_less_than_max()`
- `test_create_assigns_all_moves_when_pokemon_has_exactly_four()`
- `test_create_assigns_random_four_moves_when_pokemon_has_five()`
- `test_create_respects_max_four_moves_with_many_available()`

### Arquivos Criados

- ✅ `app/shared/moves_utils.py` - Função utilitária para seleção aleatória
- ✅ `app/shared/__init__.py` - Inicializador do módulo shared
- ✅ `tests/app/shared/test_moves_utils.py` - Testes unitários
- ✅ `tests/app/shared/__init__.py` - Inicializador de testes

### Boas Práticas Aplicadas

✅ **Código Limpo:**
- Função pequena e focada com responsabilidade única
- Nomes descritivos (`select_random_moves`, `available_moves`)
- Documentação com docstring

✅ **Python/FastAPI:**
- Type hints explícitos com `Sequence` e `list`
- Uso de `random.sample()` para seleção sem repetição
- Tratamento de edge cases (lista vazia, menos de máximo)

✅ **Testes:**
- Testes unitários com `unittest.mock.MagicMock`
- Testes de integração com fixtures do projeto
- Padrão de nomenclatura: `TestClass` e `test_method_scope`
- Descrições em inglês conforme padrão do projeto

✅ **Arquitetura:**
- Função utilitária reutilizável em `app/shared/`
- Integração limpa no serviço existente
- Sem modificações desnecessárias em outras partes do código

### Como Funciona

Quando um Pokémon é capturado:

```python
# Exemplo 1: Pokémon com 1 movimento
pokemon.moves = [move_1]
# Resultado: captured_pokemon.moves = [move_1]

# Exemplo 2: Pokémon com 3 movimentos
pokemon.moves = [move_1, move_2, move_3]
# Resultado: captured_pokemon.moves = [move_1, move_2, move_3]

# Exemplo 3: Pokémon com 5 movimentos
pokemon.moves = [move_1, move_2, move_3, move_4, move_5]
# Resultado: captured_pokemon.moves = [move_1, move_3, move_5, move_2] (4 aleatórios)
```

### Validação

Todas as mudanças foram validadas:
- ✅ Sem erros de sintaxe
- ✅ Imports corretos
- ✅ Padrão de código consistente
- ✅ Testes unitários implementados
- ✅ Testes de integração implementados

