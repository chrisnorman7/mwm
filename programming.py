"""Provides the lua environment."""

from contextlib import contextmanager
from lupa import LuaRuntime
import db


lua = LuaRuntime()

lua.globals()['db'] = db


@contextmanager
def manage_environment(**kwargs):
    """Add all kwargs to the lua environment for the lifetime of this
    context."""
    g = lua.globals()
    try:
        for name, value in kwargs.items():
            g[name] = value
        yield lua
    finally:
        for name, value in kwargs.items():
            g[name] = None
