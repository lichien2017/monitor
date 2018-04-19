
from datetime import datetime,timezone,timedelta

class LocalTime:
    def __init__(self):
        pass
    @classmethod
    def now(cls):
        dt = datetime.utcnow()
        # print(dt)
        dt = dt.replace(tzinfo=timezone.utc)
        # print(dt)
        tzutc_8 = timezone(timedelta(hours=8))
        local_dt = dt.astimezone(tzutc_8)
        # print(local_dt)
        return local_dt
        pass
