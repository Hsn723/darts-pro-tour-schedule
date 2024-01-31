import hashlib
import os
import re
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from icalendar import Calendar, Event, vText
from typing import List

PERFECT_SCHED_URL = 'https://www.prodarts.jp/schedule/'
PERFECT_CAL_PRODID = '-//PERFECT Pro Tour Unofficial Calendar//PERFECT Pro Tour Unofficial Calendar 1.0//'
PERFECT_ICAL_FILE = 'calendars/perfect.ics'

class PerfectEvent:
    def __init__(self, stage: str, location: str, raw_date: List[str], venue: str, point: str, is_men: bool, is_women: bool):
        self._stage = stage
        self._location = location
        self._raw_date = raw_date
        self._venue = venue
        self._point = point
        self._is_men = is_men
        self._is_women = is_women

    @property
    def stage(self) -> str:
        return self._stage

    @property
    def location(self) -> str:
        return self._location

    @property
    def raw_date(self) -> List[str]:
        return self._raw_date

    @property
    def venue(self) -> str:
        return self._venue

    @property
    def point(self) -> str:
        return self._point

    @property
    def is_men(self) -> bool:
        return self._is_men

    @property
    def is_women(self) -> bool:
        return self._is_women


def get_schedule() -> List[PerfectEvent]:
    with urllib.request.urlopen(PERFECT_SCHED_URL) as f:
        raw_content = f.read()
        parsed_content = BeautifulSoup(raw_content, 'lxml')
        sched_table = parsed_content.find_all('table', id='list', limit=1)[0]
        sched_rows = sched_table.find_all('tr')
        events = []
        for row in sched_rows:
            stage = row.th.string
            details = row('td')
            location = details[0].string
            raw_date = details[1].contents
            venue = details[2].string
            point = details[3].string
            is_men = 'schedule_none' not in details[4].img.attrs['src']
            is_women = 'schedule_none' not in details[5].img.attrs['src']
            events.append(PerfectEvent(stage, location, raw_date, venue, point, is_men, is_women))
        return events


def get_start_dates(raw_date: str) -> List[datetime]:
    start_dates = []
    for date in raw_date:
        try:
            formatted_date = re.sub(r'\(\w\)', '', date)
            start_date = datetime.strptime(formatted_date, '%m月%d日').replace(year=datetime.now().year, hour=8)
            start_dates.append(start_date)
        except (ValueError, TypeError):
            continue
    return start_dates


def get_ical_events(pe: PerfectEvent) -> List[Event]:
    events = []
    start_dates = get_start_dates(pe.raw_date)
    for start_date in start_dates:
        event = Event()
        end_date = start_date.replace(hour=20)
        event.add('dtstart', start_date)
        event.add('dtend', end_date)
        event.add('dtstamp', start_date)
        participants = []
        if pe.is_men:
            participants.append('男子')
        if pe.is_women:
            participants.append('女子')
        event.add('summary', 'PERFECT {}: {} ({}) ({})'.format(pe.stage, pe.location, '/'.join(participants), pe.point))
        event['location'] = vText(pe.venue)
        event['uid'] = '{}@{}'.format(event['dtstart'].to_ical().decode("utf-8"), pe.stage)
        events.append(event)
    return events


def get_perfect_calendar(events: List[PerfectEvent]) -> Calendar:
    cal = Calendar()
    cal.add('prodid', PERFECT_CAL_PRODID)
    cal.add('version', '2.0')
    now = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0)
    cal.add('dtstart', now)
    for event in events:
        ical_events = get_ical_events(event)
        for ical_event in ical_events:
            cal.add_component(ical_event)
    return cal


def output_calendar(calendar: Calendar):
    contents = calendar.to_ical()
    cur_hash = hashlib.md5(contents).hexdigest()
    if not os.path.exists(PERFECT_ICAL_FILE) or hashlib.md5(open(PERFECT_ICAL_FILE, 'rb').read()).hexdigest() != cur_hash:
        with open(PERFECT_ICAL_FILE, 'wb') as f:
            f.write(contents)


def main():
    events = get_schedule()
    calendar = get_perfect_calendar(events)
    output_calendar(calendar)

if __name__ == '__main__':
    main()
