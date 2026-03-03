from http import HTTPStatus


def test_create_trainer(client, pokemon):
    pokeballs = 5
    capture_rate = 45
    response = client.post(
        '/trainers',
        json={
            'name': 'john Doe',
            'email': 'john@doe.com',
            'password': 'password1',
            'gender': 'MALE',
            'date_of_birth': '1990-07-20',
            'pokemon_name': pokemon.name,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    trainer = response.json()
    assert trainer['name'] == 'john Doe'
    assert trainer['email'] == 'john@doe.com'
    assert trainer['gender'] == 'MALE'
    assert trainer['date_of_birth'] == '1990-07-20T00:00:00'
    assert trainer['authentication_failures'] == 0
    assert trainer['authentication_success'] == 0
    assert trainer['total_authentications'] == 0
    assert trainer['capture_rate'] == capture_rate
    assert trainer['pokedex'] is not None
    assert trainer['captured_pokemons'] is not None
    assert trainer['pokeballs'] == pokeballs
    assert trainer['role'] == 'USER'
    assert trainer['status'] == 'ACTIVE'


def test_create_trainer_should_return_conflict_email_exists(client, trainer):
    response = client.post(
        '/trainers',
        json={
            'name': 'john Doe',
            'email': trainer.email,
            'password': 'password1',
            'gender': 'MALE',
            'date_of_birth': '1990-07-20',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_get_trainer(client, trainer, token):
    response = client.get(
        f'/trainers/{trainer.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == trainer.id
    assert data['email'] == trainer.email
    assert data['name'] == trainer.name
    assert data['email'] == trainer.email
    assert data['gender'] == trainer.gender
    assert data['date_of_birth'] == '1990-07-20T00:00:00'
    assert data['authentication_failures'] == trainer.authentication_failures
    assert data['authentication_success'] == trainer.authentication_success
    assert data['total_authentications'] == trainer.total_authentications
    assert data['capture_rate'] == trainer.capture_rate
    assert data['pokedex'] == []
    assert data['captured_pokemons'] == []
    assert data['pokeballs'] == trainer.pokeballs
    assert data['role'] == trainer.role
    assert data['status'] == trainer.status


def test_get_trainer_should_return_not_permission_error(client, other_trainer, token):
    response = client.get(
        f'/trainers/{other_trainer.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_trainer_should_return_not_found(client, token):
    response = client.get(
        '/trainers/17aafbdd-1cd5-42a1-9516-b3a55ca52e7f',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Trainer not found'}


def test_get_trainer_pokedex(client, trainer, token):
    response = client.get(
        f'/trainers/{trainer.id}/pokedex',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert isinstance(data, list)


def test_get_trainer_pokedex_should_return_forbidden_when_not_owner(
    client, other_trainer, token
):
    response = client.get(
        f'/trainers/{other_trainer.id}/pokedex',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_trainer_pokedex_should_return_forbidden_when_trainer_missing(client, token):
    response = client.get(
        '/trainers/17aafbdd-1cd5-42a1-9516-b3a55ca52e7f/pokedex',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_trainer_pokemons(client, trainer, token):
    response = client.get(
        f'/trainers/{trainer.id}/pokemons',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert isinstance(data, list)


def test_get_trainer_pokemons_should_return_forbidden_when_not_owner(
    client, other_trainer, token
):
    response = client.get(
        f'/trainers/{other_trainer.id}/pokemons',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_trainer_pokemons_should_return_forbidden_when_trainer_missing(client, token):
    response = client.get(
        '/trainers/17aafbdd-1cd5-42a1-9516-b3a55ca52e7f/pokemons',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_trainer_capture_pokemons(client, trainer, token, pokemon):
    trainer.pokeballs = 10
    trainer.capture_rate = 100
    pokemon.capture_rate = 30

    response = client.post(
        f'/trainers/{trainer.id}/capture',
        headers={'Authorization': f'Bearer {token}'},
        json={'pokemon_name': pokemon.name},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['pokemon']['name'] == pokemon.name
    assert 'id' in data
    assert 'nickname' in data


def test_trainer_capture_pokemons_should_return_forbidden_when_not_owner(
    client, other_trainer, token, pokemon
):
    response = client.post(
        f'/trainers/{other_trainer.id}/capture',
        headers={'Authorization': f'Bearer {token}'},
        json={'pokemon_name': pokemon.name},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_trainer_capture_pokemons_should_return_forbidden_when_no_pokeballs(
    client, trainer, token, pokemon
):
    trainer.pokeballs = 0

    response = client.post(
        f'/trainers/{trainer.id}/capture',
        headers={'Authorization': f'Bearer {token}'},
        json={'pokemon_name': pokemon.name},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough pokeballs'}


def test_trainer_capture_pokemons_should_return_forbidden_when_low_capture_rate(
    client, trainer, token, pokemon
):
    trainer.pokeballs = 10
    trainer.capture_rate = 30
    pokemon.capture_rate = 65

    response = client.post(
        f'/trainers/{trainer.id}/capture',
        headers={'Authorization': f'Bearer {token}'},
        json={'pokemon_name': pokemon.name},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'You have 30 capture rate. To capture this Pokemon, you need 65.'
    }


def test_trainer_capture_pokemons_should_return_forbidden_when_trainer_missing(
    client, token, pokemon
):
    response = client.post(
        '/trainers/17aafbdd-1cd5-42a1-9516-b3a55ca52e7f/capture',
        headers={'Authorization': f'Bearer {token}'},
        json={'pokemon_name': pokemon.name},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
