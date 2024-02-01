import re
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from icalendar import Calendar, Event, vText
from typing import List

from common import output_calendar

JAPAN_SCHED_URL = 'https://japanprodarts.jp/schedule.php'
JAPAN_CAL_PRODID = '-//JAPAN Pro Tour Unofficial Calendar//JAPAN Pro Tour Unofficial Calendar 1.0//'
JAPAN_ICAL_FILE = 'calendars/japan.ics'

class JapanEvent:
    def __init__(self, stage: str, location: str, start_dates: List[datetime], venue: str, is_ex: bool):
        self._stage = stage
        self._location = location
        self._start_dates = start_dates
        self._venue = venue
        self._is_ex = is_ex

    @property
    def stage(self) -> str:
        return self._stage

    @property
    def location(self) -> str:
        return self._location

    @property
    def start_dates(self) -> List[datetime]:
        return self._start_dates

    @property
    def venue(self) -> str:
        return self._venue

    @property
    def is_ex(self) -> bool:
        return self._is_ex


def get_raw_start_dates(raw_dates: List[str]) -> List[datetime]:
    start_dates = []
    for date in raw_dates:
        try:
            formatted_date = re.sub(r'\(\w\)', '', date)
            start_date = datetime.strptime(formatted_date, '%m月%d日').replace(hour=8)
            start_dates.append(start_date)
        except (ValueError, TypeError):
            continue
    return start_dates


def get_schedule() -> List[JapanEvent]:
    with urllib.request.urlopen(JAPAN_SCHED_URL) as f:
        raw_content = f.read()
        parsed_content = BeautifulSoup(raw_content, 'html.parser')
        schedule = parsed_content.find_all('article', id='schedule', limit=1)[0]
        year_raw = schedule.find_all('option', selected=True, limit=1)[0].string
        year = int(year_raw.replace('年', ''))
        stages = parsed_content.find_all('section')
        prev_month = 0
        events = []
        for stage in stages:
            stage_num = stage.h3.img['alt']
            raw_dates = stage.find('dt', string=re.compile('日程')).find_next_sibling().string.split(' - ')
            raw_start_dates = get_raw_start_dates(raw_dates)
            if len(raw_start_dates) == 0:
                continue
            cur_month = raw_start_dates[0].month
            if cur_month < prev_month:
                year += 1
            prev_month = cur_month
            start_dates = list(map(lambda d: d.replace(year=year), raw_start_dates))
            location = stage.find('dt', string=re.compile('エリア')).find_next_sibling().string
            venue = stage.find('dt', string=re.compile('会場')).find_next_sibling().string
            is_ex = stage.find(class_='exciting_stageicon') is not None
            events.append(JapanEvent(stage_num, location, start_dates, venue, is_ex))
    return events


def get_ical_events(je: JapanEvent) -> List[Event]:
    events = []
    for start_date in je.start_dates:
        event = Event()
        end_date = start_date.replace(hour=23)
        event.add('dtstart', start_date)
        event.add('dtend', end_date)
        event.add('dtstamp', start_date)
        summary = 'JAPAN {}: {}'.format(je.stage, je.location)
        if je.is_ex:
            summary += ' (EX)'
        event.add('summary', summary)
        event['location'] = vText(je.venue)
        event['uid'] = '{}@{}'.format(event['dtstart'].to_ical().decode('utf-8'), je.stage)
        events.append(event)
    return events


def get_japan_calendar(events: List[JapanEvent]) -> Calendar:
    cal = Calendar()
    cal.add('prodid', JAPAN_CAL_PRODID)
    cal.add('version', '2.0')
    start_year = events[0].start_dates[0].year
    dtstart = datetime.now().replace(year=start_year, month=1, day=1, hour=0, minute=0, second=0)
    cal.add('dtstart', dtstart)
    for event in events:
        ical_events = get_ical_events(event)
        for ical_event in ical_events:
            cal.add_component(ical_event)
    return cal


def main():
    events = get_schedule()
    calendar = get_japan_calendar(events)
    output_calendar(JAPAN_ICAL_FILE, calendar)

if __name__ == '__main__':
    main()
