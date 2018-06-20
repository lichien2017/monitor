
from datetime import datetime,timezone,timedelta

class LocalTime:
    def __init__(self):
        pass

    @classmethod
    def get_local_date(cls,date_str,format):
        date = datetime.strptime(date_str,format)
        dt = date.replace(tzinfo=timezone.utc)
        # print(dt)
        tzutc_8 = timezone(timedelta(hours=8))
        local_dt = dt.astimezone(tzutc_8)
        return local_dt
        pass

    @classmethod
    def get_utc_date(cls, date_str, format):
        date = datetime.strptime(date_str, format)

        return date
        pass

    @classmethod
    def now_month_str(cls):
        dt = datetime.utcnow()
        # print(dt)
        dt = dt.replace(tzinfo=timezone.utc)
        # print(dt)
        tzutc_8 = timezone(timedelta(hours=8))
        local_dt = dt.astimezone(tzutc_8)
        # print(local_dt)
        return local_dt.strftime("%Y%m")
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

    @classmethod
    def now_str(cls,format="%Y%m%d"):
        now = LocalTime.now().strftime(format)
        return now
        pass

    @classmethod
    def nowtime_str(cls, h):
        # 获取当前时间前后小时的时间
        now = LocalTime.now()
        from_todaytime = now + timedelta(hours=h)
        return from_todaytime
        pass

    @classmethod
    def from_today(cls,days):
        now = LocalTime.now()
        from_today = now + timedelta(days=days)
        return from_today
        pass

    @classmethod
    def yestoday(cls):
        now = LocalTime.now()
        yestoday = now + timedelta(days=-1)
        return yestoday
        pass

    @classmethod
    def yestoday_str(cls,format="%Y%m%d"):
        yestoday = LocalTime.yestoday().strftime(format)
        return yestoday
        pass