from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from importlib import import_module
from typing import TYPE_CHECKING, Callable, TypeVar


try:
    import orjson
except ImportError:
    orjson = None


if TYPE_CHECKING:
    from typing import Literal

T = TypeVar('T')

# https://docs.python.org/3/library/logging.html#logrecord-attributes
RESERVED_ATTRS = frozenset({
    'args',
    'asctime',
    'color_message',
    'created',
    'exc_info',
    'exc_text',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'message',
    'module',
    'msecs',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'stack_info',
    'thread',
    'threadName',
})


def ensure_imported(target: T | str) -> T:
    if not isinstance(target, str):
        return target
    path, function = target.rsplit('.', maxsplit=1)
    module = import_module(path)
    return getattr(module, function)


class Formatter(logging.Formatter):
    """Format logs as GCP-compatible JSON.

    https://cloud.google.com/logging/docs/structured-logging#special-payload-fields
    """

    default: Callable[[object], object]

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal['%', '{', '$'] = '%',
        validate: bool = True,
        *,
        default: Callable[[object], object] | str = str,
    ) -> None:
        super().__init__(fmt, datefmt, style, validate)
        self.default = ensure_imported(default)

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        created_at = datetime.fromtimestamp(record.created).astimezone(timezone.utc)

        result: dict[str, object] = {
            'message': record.message,
            'severity': record.levelname.upper(),
            'timestamp': f'{created_at.isoformat()}Z',
            'logging.googleapis.com/sourceLocation': {
                'file': record.pathname,
                'line': record.lineno,
                'function': record.funcName,
            }
        }

        if record.exc_info:
            result['exc_info'] = self.formatException(record.exc_info)
        elif record.exc_text:
            result['exc_info'] = record.exc_text
        if record.stack_info:
            result['stack_info'] = record.stack_info

        for key, value in record.__dict__.items():
            if key.startswith('_'):
                continue
            if key in RESERVED_ATTRS:
                continue
            result[key] = value

        if orjson is not None:
            return orjson.dumps(result, default=self.default).decode()
        return json.dumps(
            result,
            default=self.default,
            allow_nan=False,
            separators=(',', ':'),
        )
