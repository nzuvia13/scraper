import logging

import structlog


def _configure_logging():
    """
    Pulled from: https://www.structlog.org/en/stable/standard-library.html#rendering-within-structlog
    """
    shared_processors = [
        # If log level is too low, abort pipeline and throw away log entry.
        structlog.stdlib.filter_by_level,
        # Add the name of the logger to event dict.
        structlog.stdlib.add_logger_name,
        # Add log level to event dict.
        structlog.stdlib.add_log_level,
        # Perform %-style formatting.
        structlog.stdlib.PositionalArgumentsFormatter(),
        # Add a timestamp in ISO 8601 format.
        structlog.processors.TimeStamper(fmt="iso"),
        # If the "stack_info" key in the event dict is true, remove it and
        # render the current stack trace in the "stack" key.
        structlog.processors.StackInfoRenderer(),
        # If the "exc_info" key in the event dict is either true or a
        # sys.exc_info() tuple, remove "exc_info" and render the exception
        # with traceback into the "exception" key.
        structlog.processors.format_exc_info,
        # If some value is in bytes, decode it to a Unicode str.
        structlog.processors.UnicodeDecoder(),
        # Add callsite parameters.
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        # Render the final event dict as JSON.
        structlog.processors.JSONRenderer(),
    ]
    # if sys.stderr.isatty():
    #     # Pretty printing when we run in a terminal session.
    #     # Automatically prints pretty tracebacks when "rich" is installed
    #     processors = shared_processors + [
    #         structlog.dev.ConsoleRenderer(),
    #     ]
    # else:
    #     # Print JSON when we run, e.g., in a Docker container.
    #     # Also print structured tracebacks.
    #     processors = shared_processors + [
    #         structlog.processors.dict_tracebacks,
    #         structlog.processors.JSONRenderer(),
    #     ]

    structlog.configure(
        processors=shared_processors,
        # `wrapper_class` is the bound logger that you get back from
        # get_logger(). This one imitates the API of `logging.Logger`.
        wrapper_class=structlog.stdlib.BoundLogger,
        # `logger_factory` is used to create wrapped loggers that are used for
        # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
        # string) from the final processor (`JSONRenderer`) will be passed to
        # the method of the same name as that you've called on the bound logger.
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Effectively freeze configuration after creating the first bound
        # logger.
        cache_logger_on_first_use=True,
    )

    # root_logger = logging.getLogger()
    # root_logger.setLevel(logging.INFO)

    # formatter = structlog.stdlib.ProcessorFormatter(
    #     processors=[structlog.dev.ConsoleRenderer()],
    # )

    # handler = logging.StreamHandler()
    # # Use OUR `ProcessorFormatter` to format all `logging` entries.
    # handler.setFormatter(formatter)
    # root_logger = logging.getLogger()
    # root_logger.addHandler(handler)
    # root_logger.setLevel(logging.INFO)

    structlog.stdlib.recreate_defaults(log_level=logging.INFO)


def configure_logging():
    """
    Configure logging for the application.
    """
    if not structlog.is_configured():
        _configure_logging()


def build_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Build a logger with the given name
    """
    # If logging is not set up this has the side-effect of doing that --
    # in the future this should just be done once in __init__.py or something but
    # fine for now
    configure_logging()
    return structlog.get_logger(name)
