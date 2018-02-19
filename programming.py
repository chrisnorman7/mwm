"""Provides the lua environment."""

import logging
from contextlib import contextmanager
from lupa import LuaRuntime
import db
import util
from permissions import (
    check_privileges, check_builder, check_admin, check_programmer
)


logger = logging.getLogger(__name__)
lua = LuaRuntime()

lua.globals()['logger'] = logger
for thing in (
    db, util, check_privileges, check_builder, check_admin, check_programmer
):
    lua.globals()[thing.__name__] = thing


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


def as_function(code, **kwargs):
    """Execute code like a function returning its value. Use manage_environment
    with the provided keyword arguments."""
    with manage_environment(**kwargs) as runtime:
        return runtime.execute(code)
