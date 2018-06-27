#-*- coding: UTF-8 -*-
from screencap.screencap_match import ScreenCaptureMatch
from screencap.screencap_match_senddata import ScreenCaptureMatchSendData
from screencap.screencap_match_recv import ScreenCaptureMatchRecv
__version__ = '1.0.0'
VERSION = tuple(map(int, __version__.split('.')))


__all__ = [
    'ScreenCaptureMatch','ScreenCaptureMatchSendData','ScreenCaptureMatchRecv'
]
