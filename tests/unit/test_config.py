from urllib.parse import unquote, urlsplit

import pytest
from pydantic import ValidationError

from transit.config import Settings


def test_dsn_is_built_from_settings() -> None:
    s = Settings(
        _env_file=None,
        postgres_user="user1",
        postgres_password="p",
        postgres_host="host",
        postgres_port=1234,
        postgres_db="d",
        gtfs_url="x",
        stride_base_url="y",
    )

    assert s.postgres_dsn == "postgresql://user1:p@host:1234/d"


@pytest.mark.parametrize(
    "password",
    ["simple", "p@ss", "p/ss", "w rd", "p@ss/w rd"],
)
def test_password_round_trips_through_dsn(password: str) -> None:
    s = Settings(
        _env_file=None,
        postgres_password=password,
        gtfs_url="x",
        stride_base_url="y",
    )
    parts = urlsplit(s.postgres_dsn)
    assert parts.password is not None
    assert unquote(parts.password) == password
    assert parts.hostname == "localhost"


@pytest.mark.parametrize("user", ["simple", "data@team", "a/b", "my user"])
def test_user_round_trips_through_dsn(user: str) -> None:
    s = Settings(
        _env_file=None,
        postgres_user=user,
        postgres_password="p",
        gtfs_url="x",
        stride_base_url="y",
    )
    parts = urlsplit(s.postgres_dsn)
    assert parts.username is not None
    assert unquote(parts.username) == user
    assert parts.hostname == "localhost"


def test_missing_password_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)

    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            gtfs_url="x",
            stride_base_url="y",
        )


def test_empty_password_raises() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            postgres_password="",
            gtfs_url="x",
            stride_base_url="y",
        )
