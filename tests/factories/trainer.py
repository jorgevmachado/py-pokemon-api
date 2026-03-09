import factory

from app.domain.trainer.model import Trainer
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum


class TrainerFactory(factory.Factory):
    class Meta:
        model = Trainer

    name = factory.Faker('name')
    email = factory.Sequence(lambda n: f'test{n}@test.com')
    password = 'hashed_password'
    gender = GenderEnum.MALE
    role = RoleEnum.USER
    status = StatusEnum.ACTIVE
    date_of_birth = '1990-07-20T00:00:00'
    pokeballs = 5
    capture_rate = 45
    total_authentications = 0
    authentication_success = 0
    authentication_failures = 0
