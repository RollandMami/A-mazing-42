class ConfigError(Exception):
    """Exception raised for configuration loading and validation errors.

    This exception is raised when raw input parameters or configuration files
    fail validation rules or contain invalid values.
    """
    ...
