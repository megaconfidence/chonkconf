"""chonkconf: a tiny TOML config loader with computed values.

A value written as "{{ ... }}" is computed when the file loads:

    [cache]
    max_age = "{{ 7 * day }}"

Since 2.0, computed values are arithmetic only: numbers, + - * / // % **, parentheses and these units:

    second minute hour day week    seconds
    KB MB GB                       bytes, powers of 1000
    KiB MiB GiB                    bytes, powers of 1024

Nothing else runs, so loading a file you didn't write can't run code on your machine.
"""

from __future__ import annotations

import ast
import operator
import re
import tomllib
from pathlib import Path
from typing import Any

__all__ = ["UNITS", "ConfigError", "UnsafeExpressionError", "load", "loads"]
__version__ = "2.0.0"

UNITS: dict[str, int] = {
    "second": 1,
    "minute": 60,
    "hour": 60 * 60,
    "day": 24 * 60 * 60,
    "week": 7 * 24 * 60 * 60,
    "KB": 1000,
    "MB": 1000**2,
    "GB": 1000**3,
    "KiB": 1024,
    "MiB": 1024**2,
    "GiB": 1024**3,
}

_COMPUTED = re.compile(r"\{\{(.*)\}\}", re.DOTALL)
_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_MAX_EXPONENT = 64


class ConfigError(ValueError):
    """A computed value could not be computed. The message names its key."""


class UnsafeExpressionError(ConfigError):
    """A computed value used something other than numbers, units and arithmetic."""


def loads(text: str) -> dict[str, Any]:
    """Parse TOML text and compute its "{{ ... }}" values."""
    return _compute(tomllib.loads(text), "")


def load(path: str | Path) -> dict[str, Any]:
    """Read a TOML file and compute its "{{ ... }}" values."""
    return loads(Path(path).read_text(encoding="utf-8"))


def _compute(value: Any, where: str) -> Any:
    if isinstance(value, dict):
        return {key: _compute(item, f"{where}.{key}" if where else key) for key, item in value.items()}
    if isinstance(value, list):
        return [_compute(item, f"{where}[{index}]") for index, item in enumerate(value)]
    if isinstance(value, str) and (match := _COMPUTED.fullmatch(value.strip())):
        try:
            tree = ast.parse(match.group(1).strip(), mode="eval")
        except SyntaxError as error:
            raise ConfigError(f"{where}: could not compute {value!r}: {error.msg}") from error
        try:
            return _evaluate(tree.body, where)
        except ArithmeticError as error:
            raise ConfigError(f"{where}: could not compute {value!r}: {error}") from error
    return value


def _evaluate(node: ast.expr, where: str) -> int | float:
    match node:
        case ast.Constant(value=bool()):
            pass  # True and False are ints in Python, but not numbers in a config file
        case ast.Constant(value=int() | float() as number):
            return number
        case ast.Name(id=name) if name in UNITS:
            return UNITS[name]
        case ast.UnaryOp(op=op, operand=operand) if type(op) in _UNARY:
            return _UNARY[type(op)](_evaluate(operand, where))
        case ast.BinOp(left=left, op=op, right=right) if type(op) in _BINARY:
            a, b = _evaluate(left, where), _evaluate(right, where)
            if isinstance(op, ast.Pow) and abs(b) > _MAX_EXPONENT:
                raise UnsafeExpressionError(f"{where}: the exponent {b} is too large")
            return _BINARY[type(op)](a, b)
    raise UnsafeExpressionError(
        f"{where}: {{{{ }}}} values can only use numbers, units and arithmetic, not {ast.unparse(node)!r}"
    )
