from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, trainer):
    response = client.post(
        '/auth/token',
        json={'email': trainer.email, 'password': trainer.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_should_unauthorized_when_not_user_found(client, trainer):
    response = client.post(
        '/auth/token',
        json={'email': 'not-trainer@mail.com', 'password': trainer.clean_password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_should_unauthorized_when_password_invalid(client, trainer):
    response = client.post(
        '/auth/token',
        json={'email': trainer.email, 'password': 'password-weak'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_auth_me(client, trainer, token):
    response = client.get('/auth/me', headers={'Authorization': f'Bearer {token}'})
    data = response.json()
    assert response.status_code == HTTPStatus.OK
    assert data['email'] == trainer.email


def test_token_expired_dont_refresh(client, trainer):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            json={'email': trainer.email, 'password': trainer.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 13:01:00'):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
