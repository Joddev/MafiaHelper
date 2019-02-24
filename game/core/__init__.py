from game.core.handler import RoomHandler
from game.core.job import *

room_container = RoomHandler()
job_list = [
    Citizen.__name__.lower(),
    Police.__name__.lower(),
    Doctor.__name__.lower(),
    Mafia.__name__.lower()
]

__all__ = ['room_container', 'job_list']
