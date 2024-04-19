# enums related to the game logic
import enum


class DifficultyEnum(enum.Enum):
    NORMAL = 1
    HARD = 2
    CUSTOM = 3


class StatusEnum(enum.Enum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    TERMINATED = 3  # TODO: decide whether or not to terminate incomplete games after a certain time
