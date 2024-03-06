import urllib.request, urllib.error
from datetime import datetime
from icalendar import Event, vText
from typing import List

class TourEvent:
    def __init__(self, stage: str, start_date: datetime, end_hour: int):
        self._stage = stage
        self._start_date = start_date
        self._end_hour = end_hour

    @property
    def stage(self) -> str:
        return self._stage

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @property
    def end_date(self) -> datetime:
        return self.start_date.replace(hour=self._end_hour)

    def start_datestr(self) -> str:
        return self.start_date.strftime('%Y%m%dT%H%M%S')

    def get_summary(self) -> str:
        pass

    def get_location(self) -> vText:
        return None

    def get_description(self) -> str:
        pass

    def get_uid(self) -> str:
        return '{}@{}'.format(self.start_datestr(), self.stage)

    def to_ical(self) -> Event:
        event = Event()
        event.add('dtstart', self.start_date)
        event.add('dtend', self.end_date)
        event.add('dtstamp', self.start_date)
        event.add('summary', self.get_summary())
        if self.get_location():
            event['location'] = self.get_location()
        event['uid'] = self.get_uid()
        event.add('description', self.get_description())
        return event


class PerfectEvent(TourEvent):
    END_HOUR = 20
    def __init__(self, stage: str, start_date: datetime, location: str, venue: str, point: str, is_men: bool, is_women: bool):
        self._location = location
        self._venue = venue
        self._point = point
        self._is_men = is_men
        self._is_women = is_women
        super().__init__(stage, start_date, self.END_HOUR)

    def get_summary(self) -> str:
        participants = []
        if self._is_men:
            participants.append('男子')
        if self._is_women:
            participants.append('女子')
        return 'PERFECT {}: {} ({}) ({})'.format(self.stage, self._location, '/'.join(participants), self._point)

    def get_location(self) -> vText:
        return vText(self._venue)

    def get_description(self) -> str:
        date = self.start_datestr()
        url = 'https://www.prodarts.jp/archives/outline/{}'.format(date[:date.index('T')])
        req = urllib.request.Request(url, method='HEAD')
        try:
            resp = urllib.request.urlopen(req)
            if resp.status == 200:
                return url
        except urllib.error.HTTPError:
            return ''


class JapanEvent(TourEvent):
    END_HOUR = 23
    def __init__(self, stage: str, start_date: datetime, location: str, venue: str, japan_year: int, is_ex: bool):
        self._location = location
        self._venue = venue
        self._japan_year = japan_year
        self._is_ex = is_ex
        super().__init__(stage, start_date, self.END_HOUR)

    def get_summary(self) -> str:
        summary = 'JAPAN {}: {}'.format(self.stage, self._location)
        if self._is_ex:
            summary += ' (EX)'
        return summary

    def get_location(self) -> vText:
        return vText(self._venue)

    def get_description(self) -> str:
        url = 'https://japanprodarts.jp/{}/{}.php'.format(self._japan_year, self.stage)
        req = urllib.request.Request(url, method='HEAD')
        try:
            resp = urllib.request.urlopen(req)
            if resp.status == 200:
                return url
        except urllib.error.HTTPError:
            pass
        url = 'https://japanprodarts.jp/{}/{}.php'.format(self._japan_year, self.stage.lower())
        req = urllib.request.Request(url, method='HEAD')
        try:
            resp = urllib.request.urlopen(req)
            if resp.status == 200:
                return url
        except urllib.error.HTTPError:
            pass
        return ''


class DTourEvent(TourEvent):
    END_HOUR = 22
    def __init__(self, stage: str, start_date: datetime, division: str, details_url: str, prelim_info: str):
        self._division = division
        self._details_url = details_url
        self._prelim_info = prelim_info
        super().__init__(stage, start_date, self.END_HOUR)

    def get_summary(self) -> str:
        return 'DTOUR {} {}'.format(self._division, self.stage)

    def get_description(self) -> str:
        return '{}\n{}'.format(self._details_url, self._prelim_info)
