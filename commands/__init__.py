"""All commands should be imported here."""

from .admin import Eval
from .socials import Say, Emote
from .misc import Quit, Password, Inventory, Commands, Shutdown, Abort_Shutdown
from .building import Dig
from .movement import Go

__all__ = [
    'Say', 'Quit', 'Password', 'Inventory', 'Commands', 'Shutdown',
    'Abort_Shutdown', 'Go', 'Emote', 'Dig', 'Eval'
]
