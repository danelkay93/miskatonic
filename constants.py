from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class Faction(StrEnum):
    MYTHOS: str = "mythos"
    ROGUE: str = "rogue"
    SEEKER: str = "seeker"
    MYSTIC: str = "mystic"
    SURVIVOR: str = "survivor"
    GUARDIAN: str = "guardian"
    NEUTRAL: str = "neutral"


class Skill(StrEnum):
    INTELLECT: str = "intellect"
    AGILITY: str = "agility"
    WILLPOWER: str = "willpower"
    COMBAT: str = "combat"
    WILD: str = "wild"


class PlayerCardType(StrEnum):
    ASSET: str = "asset"
    EVENT: str = "event"
    SKILL: str = "skill"


class DeckTag(StrEnum):
    SOLO: str = "solo"
    BEGINNER: str = "beginner"
    MULTIPLAYER: str = "multiplayer"
    THEME: str = "theme"


class PlayerCounts(StrEnum):
    SOLO: str = "SOLO"
    TWO_PLAYER: str = "TWO-PLAYER"
    FOUR_PLAYER: str = "FOUR-PLAYER"
    MULTIPLAYER: str = "MULTIPLAYER"
    UNKNOWN: str = "UNKNOWN"
