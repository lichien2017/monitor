from util.log import Logger
from util.log import SingleLogger

__version__ = '1.0.0'
VERSION = tuple(map(int, __version__.split('.')))


__all__ = [
    'Logger','SingleLogger'
]
