from miskatonic.exceptions import MiskatonicException


class CardDataRetrievalError(MiskatonicException):
    """
    Indicates a failure to retrieve card data from ArkhamDB
    """


class UnexpectedEncounterCardError(MiskatonicException):
    """
    Indicates that a scenario/mythos/encouner card was returned rather than a player card
    """


class DecklistRetrievalError(MiskatonicException):
    """
    Indicates a failure to retrieve decklist data from ArkhamDB
    """


class DeckDetailsRetrievalError(DecklistRetrievalError):
    """
    Indicates a failure to retrieve deck detail data from ArkhamDB
    """


class UserInfoRetrievalError(MiskatonicException):
    """
    Indicates a failure to retrieve user data from ArkhamDB
    """
