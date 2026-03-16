from enum import Enum


class StatusEnum(str, Enum):
    ACTIVE = ('ACTIVE',)
    COMPLETE = ('COMPLETE',)
    INACTIVE = ('INACTIVE',)
    INCOMPLETE = ('INCOMPLETE',)
