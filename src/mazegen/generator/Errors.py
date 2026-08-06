class MazeError(Exception):
    """Base exception class for all errors within the MazeGenerator package.

    Serves as the root exception for catching any domain-specific error
    raised by configuration loaders, engines, writers, or solvers.
    """
    pass


class GenerationError(MazeError):
    """Exception raised when an error occurs during
    the maze generation process.

    Typically thrown when grid initialization fails,
    invalid generation parameters
    are encountered at runtime, or an algorithm reaches
    an unrecoverable state.
    """
    pass
