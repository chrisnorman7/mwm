"""All commands should be imported here."""

from .admin import Eval, Exec, Room_Command, MOTD
from .socials import Say, Emote
from .misc import (
    Quit, Password, Inventory, Commands, Shutdown, Abort_Shutdown, Look, Exits
)
from .building import Dig, ZEdit, REdit, Add_Gender
from .movement import Go

__all__ = [
    'Say', 'Quit', 'Password', 'Inventory', 'Commands', 'Shutdown',
    'Abort_Shutdown', 'Go', 'Emote', 'Dig', 'Eval', 'Exec', 'Look', 'Exits',
    'ZEdit', 'REdit', 'Room_Command', 'MOTD', 'Add_Gender'
]
