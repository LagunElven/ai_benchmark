class BenchmarkError(Exception):
    """Base class for expected benchmark errors."""


class ConfigurationError(BenchmarkError):
    """Configuration or schema validation failed."""


class DiscoveryError(BenchmarkError):
    """Task discovery failed."""


class WorkspaceError(BenchmarkError):
    """A workspace could not be created safely."""


class ModelClientError(BenchmarkError):
    """The model endpoint returned an invalid response or could not be reached."""


class ContextCapacityError(BenchmarkError):
    """The exact serialized prompt exceeds the configured model context window."""


class ChangeProtocolError(BenchmarkError):
    """The model response violated the file change protocol."""


class ValidationError(BenchmarkError):
    """A validator could not be executed safely."""
