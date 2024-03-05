import re
import urllib.request, urllib.error
from bs4 import BeautifulSoup, ResultSet
from datetime import datetime
from icalendar import Calendar, Event
from typing import List

from common import output_calendar

BASE_URL = 'https://www.da-topi.jp'
D_TOUR_BASE_URL = '{}/d-tour_{}'.format(BASE_URL, datetime.now().year)
D_TOUR_CONNECT_SCHED_URL = '{}/connect'.format(D_TOUR_BASE_URL)
D_TOUR_ARENA_SCHED_URL = '{}/arena'.format(D_TOUR_BASE_URL)
D_TOUR_CAL_PRODID = '-//D-TOUR Unofficial Calendar//D-TOUR Unofficial Calendar 1.0//'
D_TOUR_ICAL_FILE = 'calendars/d-tour.ics'

class DTourEvent:
    def __init__(self, division: str, stage: str, start_date: datetime, details_url: str, prelim_info: str):
        self._division = division
        self._stage = stage
        self._start_date = start_date
        self._details_url = details_url
        self._prelim_info = prelim_info

    @property
    def division(self) -> str:
        return self._division

    @property
    def stage(self) -> str:
        return self._stage

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @property
    def details_url(self) -> str:
        return self._details_url

    @property
    def prelim_info(self) -> str:
        return self._prelim_info


def get_connect_start_date(raw_date: str) -> datetime:
    try:
        formatted_date = re.sub(r'\([^)]+\)', '', raw_date)
        full_date = datetime.strptime(formatted_date, '%m/%d').replace(year=datetime.now().year, hour=10)
        return full_date
    except (ValueError, TypeError):
        return None


def get_arena_start_date(raw_date:  str) -> datetime:
    try:
        formatted_date = re.sub(r'\([^)]+\)', '-', raw_date)
        full_date = datetime.strptime(formatted_date, '%m/%d-%H:%M').replace(year=datetime.now().year)
        return full_date
    except (ValueError, TypeError):
        return None


def get_dtour_schedule(url: str) -> ResultSet:
    with urllib.request.urlopen(url) as f:
        raw_content = f.read()
    parsed_content = BeautifulSoup(raw_content, 'html.parser')
    sched_table = parsed_content.find_all('table', class_='schedule', limit=1)[0]
    sched_rows = sched_table.find('tbody').find_all('tr')
    return sched_rows


def get_connect_schedule() -> List[DTourEvent]:
    sched_rows = get_dtour_schedule(D_TOUR_CONNECT_SCHED_URL)
    events = []
    for row in sched_rows:
        details = row('td')
        if len(details) == 1:
            break
        stage = details[0].get_text().replace('本戦会場','').strip()
        raw_date = details[1].string
        start_date = get_connect_start_date(raw_date)
        details_url = details[0].a.get('href')
        details_url = '本戦会場: {}'.format(details_url) if details_url else ''
        prelim_dates = details[3].get_text().replace('予選会場', '').replace(' ', '').strip()
        prelim_url = details[3].a.get('href')
        prelim_url = '予選会場: {}'.format(prelim_url) if prelim_url else ''
        prelim_info = '予選:{}\n{}'.format(prelim_dates, prelim_url)
        events.append(DTourEvent('CONNECT', stage, start_date, details_url, prelim_info))
    return events


def get_arena_schedule() -> List[DTourEvent]:
    sched_rows = get_dtour_schedule(D_TOUR_ARENA_SCHED_URL)
    events = []
    for row in sched_rows:
        details = row('td')
        stage = details[0].get_text().strip().replace(' ', '').replace('\n\n', '\n').replace('\n', ': ')
        raw_date = details[1].get_text()
        start_date = get_arena_start_date(raw_date)
        details_url = details[0].a.get('href') if details[0].a else ''
        details_url = '大会詳細: {}{}'.format(BASE_URL, details_url) if details_url else ''
        prelim_dates = details[3].get_text().replace('予選会場', '').replace(' ', '').strip()
        prelim_url = details[3].a.get('href')
        prelim_url = '予選会場: {}'.format(prelim_url) if prelim_url else ''
        prelim_info = '予選:\n{}\n{}'.format(prelim_dates, prelim_url)
        events.append(DTourEvent('ARENA', stage, start_date, details_url, prelim_info))
    return events


def get_schedule() -> List[DTourEvent]:
    connect_schedule = get_connect_schedule()
    arena_schedule = get_arena_schedule()
    return connect_schedule + arena_schedule


def get_ical_event(de: DTourEvent) -> Event:
    event = Event()
    end_date = de.start_date.replace(hour=22)
    event.add('dtstart', de.start_date)
    event.add('dtend', end_date)
    event.add('dtstamp', de.start_date)
    summary = 'DTOUR {} {}'.format(de.division, de.stage)
    event.add('summary', summary)
    description = '{}\n{}'.format(de.details_url, de.prelim_info)
    event.add('description', description)
    event['uid'] = '{}@{}'.format(event['dtstart'].to_ical().decode('utf-8'), de.stage)
    return event


def get_dtour_calendar(events: List[DTourEvent]) -> Calendar:
    cal = Calendar()
    cal.add('prodid', D_TOUR_CAL_PRODID)
    cal.add('version', '2.0')
    dtstart = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0)
    cal.add('dtstart', dtstart)
    for event in events:
        ical_event = get_ical_event(event)
        cal.add_component(ical_event)
    return cal


def main():
    events = get_schedule()
    calendar = get_dtour_calendar(events)
    output_calendar(D_TOUR_ICAL_FILE, calendar)

if __name__ == '__main__':
    main()
