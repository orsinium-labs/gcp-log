# gcp-log

Python library to format logs as [GCP](https://cloud.google.com/)-compatible JSON.

Features:

+ Works with standard [logging](https://docs.python.org/3/library/logging.html).
+ Supports [extra](https://docs.python.org/3/library/logging.html#logging.Logger.debug) for structured logging.
+ 100% compatible with [the official spec](https://cloud.google.com/logging/docs/structured-logging#special-payload-fields).
+ Non-invasive, doesn't start any threads or processes, doesn't make network or system calls.
+ Zero configuration.
+ Fast.
+ Pure Python.
+ Type-safe.
+ Zero dependency.
+ Optional integration with [orjson](https://pypi.org/project/orjson/) for better performance.

## Installation

```shell
python3 -m pip install gcp-log
```

**Optional:** If you also install [orjson](https://pypi.org/project/orjson/), gcp-log will automatically use it instead of stdlib [json](https://docs.python.org/3/library/json.html) for faster serialization:

```shell
python3 -m pip install orjson
```

## Usage

To use it, simply set `gcp_log.Formatter` as the [formatter](https://docs.python.org/3/library/logging.html#formatter-objects) for the logger:

```python
import logging
import gcp_log

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = gcp_log.Formatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

And then you can use the logger:

```python
logger.info('aragorn', extra=dict(father='arathorn'))
```

The output:

```json
{"message":"aragorn","severity":"INFO","timestamp":"2022-03-17T10:09:58.393124+00:00Z","logging.googleapis.com/sourceLocation":{"file":"/full/path/to/example.py.py","line":24,"function":"test_gcp_formatter"},"father":"arathorn"}
```

A human-readable version:

```json
{
    "message": "aragorn",
    "severity": "INFO",
    "timestamp": "2022-03-17T10:09:58.393124+00:00Z",
    "logging.googleapis.com/sourceLocation": {
        "file": "/full/path/to/example.py.py",
        "line": 24,
        "function": "test_gcp_formatter",
    },
    "father": "arathorn",
}
```
