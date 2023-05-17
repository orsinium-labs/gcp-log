from __future__ import annotations

import json
import logging
from io import StringIO
from pathlib import Path
from unittest.mock import ANY

from gcp_log import Formatter


def make_logger(stream: StringIO) -> logging.Logger:
    logger = logging.getLogger('arnor')
    handler = logging.StreamHandler(stream)
    handler.formatter = Formatter()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def test_gcp_formatter() -> None:
    stream = StringIO()
    logger = make_logger(stream)
    logger.info('aragorn', extra=dict(father='arathorn'))
    record = json.loads(stream.getvalue())
    assert record == {
        'message': 'aragorn',
        'severity': 'INFO',
        'father': 'arathorn',
        'timestamp': ANY,
        'logging.googleapis.com/sourceLocation': {
            'file': ANY,
            'line': ANY,
            'function': 'test_gcp_formatter',
        },
    }
    assert record['timestamp'].endswith('Z')
    source = record['logging.googleapis.com/sourceLocation']
    assert source['file'].endswith(Path(__file__).name)
