from device.runner import DeviceRunner
from device.group import DeviceGroup

__version__ = '1.0.0'
VERSION = tuple(map(int, __version__.split('.')))


__all__ = [
    'DeviceGroup', 'DeviceRunner'
]
