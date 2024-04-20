from __future__ import annotations

from logging.config import dictConfig
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Receive, Scope, Send

    from src.core.config import AppConfig


def configure(app_config: AppConfig) -> None:
    config = get_dict_config(app_config)
    dictConfig(config=config)


def get_dict_config(app_config: AppConfig) -> dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"level": app_config.log_level, "handlers": ["stream_stdout"]},
        "loggers": {
            "gunicorn": {"handlers": ["stream_stdout"], "propagate": False},
            "uvicorn": {"handlers": ["stream_stdout"], "propagate": False},
            "sqlalchemy": {"level": "WARNING"},
        },
        "handlers": {
            "stream_stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "structlog",
            },
        },
        "formatters": {
            "structlog": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "foreign_pre_chain": [
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                ],
                "processors": get_structlog_processors(app_config),
            },
        },
    }


def get_structlog_processors(app_config: AppConfig) -> list[structlog.typing.Processor]:
    processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.PROCESS,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ]
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]

    if app_config.log_json:
        processors.extend((
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ))
    else:
        processors.append(structlog.dev.ConsoleRenderer(pad_event=50, colors=True))

    return processors


class StructlogMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        structlog.contextvars.clear_contextvars()

        try:  # noqa: SIM105 (suppressible exception)
            structlog.contextvars.bind_contextvars(request_path=scope["path"])
        except KeyError:
            pass

        await self.app(scope, receive, send)
