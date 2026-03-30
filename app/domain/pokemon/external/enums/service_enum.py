from enum import Enum


class ServiceType(str, Enum):
    TYPE = ('TYPE',)
    MOVE = ('MOVE',)
    SPECIE = ('SPECIE',)
    POKEMON = ('POKEMON',)
    EVOLUTION = ('EVOLUTION',)
    GROWTH_RATE = ('GROWTH_RATE',)
