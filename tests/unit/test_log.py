import json
import logging

import pytest

from transit.log import JsonFormatter, setup_logging


def make_record(**attrs: object) -> logging.LogRecord:
    """Build a log record with sensible defaults, overridable per test."""
    defaults: dict[str, object] = {
        "name": "test.logger",
        "levelname": "INFO",
        "levelno": logging.INFO,
        "msg": "hello %s",
        "args": ("world",),
    }
    defaults.update(attrs)
    return logging.makeLogRecord(defaults)


def test_basic_fields() -> None:
    output = JsonFormatter().format(make_record())
    data = json.loads(output)

    assert data["level"] == "INFO"
    assert data["logger"] == "test.logger"
    assert data["message"] == "hello world"
    assert "timestamp" in data


def test_run_id_included_when_given() -> None:
    output = JsonFormatter().format(make_record(run_id="r1"))
    data = json.loads(output)
    assert data["run_id"] == "r1"


def test_run_id_absent_when_not_given() -> None:
    record = make_record()
    data = json.loads(JsonFormatter().format(record))
    assert "run_id" not in data


def test_exception_included() -> None:
    with pytest.raises(ValueError) as caught:
        raise ValueError("something broke")

    exc_info = (caught.type, caught.value, caught.tb)
    record = make_record(exc_info=exc_info)
    data = json.loads(JsonFormatter().format(record))

    assert "ValueError: something broke" in data["exception"]


def test_setup_logging_twice_adds_one_handler() -> None:
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level

    try:
        setup_logging("INFO")
        setup_logging("INFO")
        assert len(root.handlers) == 1
    finally:
        root.handlers[:] = saved_handlers
        root.setLevel(saved_level)
