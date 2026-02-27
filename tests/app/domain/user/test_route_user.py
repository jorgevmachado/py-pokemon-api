from http import HTTPStatus


def test_create_user(client):
    pokeballs = 5
    capture_rate = 45
    response = client.post(
        '/users',
        json={
            'name': 'john Doe',
            'email': 'john@doe.com',
            'password': 'password1',
            'gender': 'MALE',
            'date_of_birth': '1990-07-20',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    user = response.json()
    assert user['name'] == 'john Doe'
    assert user['email'] == 'john@doe.com'
    assert user['gender'] == 'MALE'
    assert user['date_of_birth'] == '1990-07-20T00:00:00'
    assert user['authentication_failures'] == 0
    assert user['authentication_success'] == 0
    assert user['total_authentications'] == 0
    assert user['capture_rate'] == capture_rate
    assert user['pokedex'] == []
    assert user['captured_pokemons'] == []
    assert user['pokeballs'] == pokeballs
    assert user['role'] == 'USER'
    assert user['status'] == 'ACTIVE'


def test_create_user_should_return_conflict_email_exists(client, user):
    response = client.post(
        '/users',
        json={
            'name': 'john Doe',
            'email': user.email,
            'password': 'password1',
            'gender': 'MALE',
            'date_of_birth': '1990-07-20',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_get_user(client, user, token):
    response = client.get(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == user.id
    assert data['email'] == user.email
    assert data['name'] == user.name
    assert data['email'] == user.email
    assert data['gender'] == user.gender
    assert data['date_of_birth'] == '1990-07-20T00:00:00'
    assert data['authentication_failures'] == user.authentication_failures
    assert data['authentication_success'] == user.authentication_success
    assert data['total_authentications'] == user.total_authentications
    assert data['capture_rate'] == user.capture_rate
    assert data['pokedex'] == []
    assert data['captured_pokemons'] == []
    assert data['pokeballs'] == user.pokeballs
    assert data['role'] == user.role
    assert data['status'] == user.status


def test_get_user_should_return_not_permission_error(client, other_user, token):
    response = client.get(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_user_should_return_not_found(client, token):
    response = client.get(
        '/users/17aafbdd-1cd5-42a1-9516-b3a55ca52e7f',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_initialize_user_returns_user(client, user, token):
    response = client.post(
        '/users/initialize',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == user.id
    assert data['email'] == user.email
    assert data['status'] == user.status


def test_initialize_user_unauthorized(client):
    response = client.post(
        '/users/initialize',
        json={},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
