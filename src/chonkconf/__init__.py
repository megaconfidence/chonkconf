"""chonkconf: a tiny TOML config loader with computed values.

A value written as "{{ ... }}" is computed when the file loads:

    [cache]
    max_age = "{{ 7 * 24 * 60 * 60 }}"

Pass your own functions to use them in computed values:

    chonkconf.load("app.toml", functions={"days": lambda n: n * 86400})
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

__all__ = ["ConfigError", "load", "loads"]
__version__ = "1.2.0"

Functions = Mapping[str, Callable[..., Any]]

_COMPUTED = re.compile(r"\{\{(.*)\}\}", re.DOTALL)


class ConfigError(ValueError):
    """A computed value could not be computed. The message names its key."""


def loads(text: str, *, functions: Functions | None = None) -> dict[str, Any]:
    """Parse TOML text and compute its "{{ ... }}" values."""
    return _compute(tomllib.loads(text), dict(functions or {}), "")


def load(path: str | Path, *, functions: Functions | None = None) -> dict[str, Any]:
    """Read a TOML file and compute its "{{ ... }}" values."""
    return loads(Path(path).read_text(encoding="utf-8"), functions=functions)


def _compute(value: Any, functions: dict[str, Callable[..., Any]], where: str) -> Any:
    if isinstance(value, dict):
        return {key: _compute(item, functions, f"{where}.{key}" if where else key) for key, item in value.items()}
    if isinstance(value, list):
        return [_compute(item, functions, f"{where}[{index}]") for index, item in enumerate(value)]
    if isinstance(value, str) and (match := _COMPUTED.fullmatch(value.strip())):
        try:
            return eval(match.group(1).strip(), dict(functions))  # noqa: S307
        except Exception as error:
            raise ConfigError(f"{where}: could not compute {value!r}: {error}") from error
    return value
