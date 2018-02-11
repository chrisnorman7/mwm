"""All commands should be imported here."""

from .admin import Eval, Exec, Room_Command, MOTD, Edit_Room_Command, Program
from .socials import Say, Emote, Stand, Rest
from .misc import (
    Quit, Password, Inventory, Commands, Shutdown, Abort_Shutdown, Look, Exits
)
from .building import Dig, ZEdit, REdit, Add_Gender, Create_Zone
from .movement import Go

__all__ = [
    'Say', 'Quit', 'Password', 'Inventory', 'Commands', 'Shutdown',
    'Abort_Shutdown', 'Go', 'Emote', 'Dig', 'Eval', 'Exec', 'Look', 'Exits',
    'ZEdit', 'REdit', 'Room_Command', 'MOTD', 'Add_Gender',
    'Edit_Room_Command', 'Program', 'Create_Zone', 'Stand', 'Rest'
]
