class NflError(Exception):
    """Base class for all NFL exceptions."""


class ValidationError(NflError):
    """User-provided data is invalid."""


class NotFoundError(NflError):
    """A requested resource could not be found."""


class ConfigurationError(NflError):
    """The library is incorrectly configured."""
