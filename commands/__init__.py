"""All commands should be imported here."""

from .admin import (
    Eval, Exec, Room_Command, MOTD, Edit_Room_Command, Program, Create_Race,
    Set_Race_Home, Message, Teleport, Config
)
from .socials import Say, Emote, Stand, Rest
from .misc import (
    Quit, Password, Inventory, Commands, Shutdown, Abort_Shutdown, Look, Exits,
    Zone, Gold, Uptime
)
from .building import Dig, ZEdit, REdit, Create_Gender, Create_Zone
from .movement import Go

__all__ = [
    'Say', 'Quit', 'Password', 'Inventory', 'Commands', 'Shutdown',
    'Abort_Shutdown', 'Go', 'Emote', 'Dig', 'Eval', 'Exec', 'Look', 'Exits',
    'ZEdit', 'REdit', 'Room_Command', 'MOTD', 'Create_Gender',
    'Edit_Room_Command', 'Program', 'Create_Zone', 'Stand', 'Rest',
    'Create_Race', 'Set_Race_Home', 'Message', 'Teleport', 'Zone', 'Config',
    'Gold', 'Uptime'
]
