from __future__ import annotations

import json
import logging
from io import StringIO
from pathlib import Path
from unittest.mock import ANY

from gcp_log import Formatter


def test_gcp_formatter():
    stream = StringIO()
    logger = logging.getLogger('arnor')
    handler = logging.StreamHandler(stream)
    handler.formatter = Formatter()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    logger.info('aragorn', extra=dict(father='arathorn'))
    stream.seek(0)
    stdout = stream.read()
    assert stdout
    record = json.loads(stdout)
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
