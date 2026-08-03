class MazeError(Exception):
    """Base class for projects error"""
    pass


class GenerationError(MazeError):
    """Error during maze generation"""
    pass
