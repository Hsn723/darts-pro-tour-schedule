import hashlib
import itertools
import os
import re
import urllib.request
from bs4 import BeautifulSoup, ResultSet, Tag
from datetime import datetime
from icalendar import Calendar
from typing import List, Tuple

from event import *


class Tour:
    CAL_VERSION = '2.0'
    def __init__(self, filename: str, prodid: str):
        self._filename = filename
        self._prodid = prodid

    def get_schedule(self) -> List[TourEvent]:
        return None

    def get_calendar(self, events: List[TourEvent]) -> Calendar:
        cal = Calendar()
        cal.add('prodid', self._prodid)
        cal.add('version', self.CAL_VERSION)
        dtstart = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0)
        cal.add('dtstart', dtstart)
        for event in events:
            cal.add_component(event.to_ical())
        return cal

    def output_calendar(self):
        events = self.get_schedule()
        calendar = self.get_calendar(events)
        contents = calendar.to_ical()
        cur_hash = hashlib.md5(contents).hexdigest()
        if not os.path.exists(self._filename) or hashlib.md5(open(self._filename, 'rb').read()).hexdigest() != cur_hash:
            with open(self._filename, 'wb') as f:
                f.write(contents)


class PerfectTour(Tour):
    PERFECT_SCHED_URL = 'https://www.prodarts.jp/schedule/'
    PERFECT_CAL_PRODID = '-//PERFECT Pro Tour Unofficial Calendar//PERFECT Pro Tour Unofficial Calendar 1.0//'
    PERFECT_ICAL_FILE = 'calendars/perfect.ics'
    def __init__(self):
        super().__init__(self.PERFECT_ICAL_FILE, self.PERFECT_CAL_PRODID)

    def _get_start_dates(self, raw_dates: List[str], year: int) -> List[datetime]:
        start_dates = []
        for date in raw_dates:
            try:
                formatted_date = re.sub(r'\(\w\)', '', date)
                start_date = datetime.strptime(formatted_date, '%m月%d日').replace(year=year, hour=8)
                start_dates.append(start_date)
            except (ValueError, TypeError):
                continue
        return start_dates

    def _get_year(self, raw: Tag) -> int:
        try:
            return int(raw.span.get_text())
        except (ValueError, TypeError):
            return datetime.now().year

    def get_schedule(self) -> List[TourEvent]:
        with urllib.request.urlopen(self.PERFECT_SCHED_URL) as f:
            raw_content = f.read()
        parsed_content = BeautifulSoup(raw_content, 'lxml')
        year = self._get_year(parsed_content.find('h3', class_='midashi1'))
        sched_table = parsed_content.find_all('table', id='list', limit=1)[0]
        sched_rows = sched_table.find_all('tr')
        events = []
        for row in sched_rows:
            if '調整中' in row.get_text():
                continue
            stage = row.th.string
            details = row('td')
            location = details[0].string
            raw_dates = details[1].contents
            venue = details[2].string
            point = details[3].string
            is_men = 'schedule_none' not in details[4].img.attrs['src']
            is_women = 'schedule_none' not in details[5].img.attrs['src']
            start_dates = self._get_start_dates(raw_dates, year)
            for start_date in start_dates:
                events.append(PerfectEvent(stage, start_date, location, venue, point, is_men, is_women))
        return events


class JapanTour(Tour):
    JAPAN_SCHED_URL = 'https://japanprodarts.jp/schedule.php'
    JAPAN_CAL_PRODID = '-//JAPAN Pro Tour Unofficial Calendar//JAPAN Pro Tour Unofficial Calendar 1.0//'
    JAPAN_ICAL_FILE = 'calendars/japan.ics'
    def __init__(self):
        super().__init__(self.JAPAN_ICAL_FILE, self.JAPAN_CAL_PRODID)

    def _get_raw_start_dates(self, raw_dates: List[str]) -> List[datetime]:
        start_dates = []
        for date in raw_dates:
            try:
                formatted_date = re.sub(r'\(\w\)', '', date)
                start_date = datetime.strptime(formatted_date, '%m月%d日').replace(hour=8)
                start_dates.append(start_date)
            except (ValueError, TypeError):
                continue
        return start_dates

    def get_schedule(self) -> List[TourEvent]:
        with urllib.request.urlopen(self.JAPAN_SCHED_URL) as f:
            raw_content = f.read()
        parsed_content = BeautifulSoup(raw_content, 'html.parser')
        schedule = parsed_content.find_all('article', id='schedule', limit=1)[0]
        year = int(parsed_content.find_all('span', class_='numArea', limit=1)[0].get_text().strip())
        japan_year = year
        stages = parsed_content.find_all('section')
        prev_month = 0
        events = []
        for stage in stages:
            stage_num = stage.h3.img['alt']
            raw_dates = stage.find('dt', string=re.compile('日程')).find_next_sibling().string.split(' - ')
            raw_start_dates = self._get_raw_start_dates(raw_dates)
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
            for start_date in start_dates:
                events.append(JapanEvent(stage_num, start_date, location, venue, japan_year, is_ex))
        return events


class DTour(Tour):
    BASE_URL = 'https://www.da-topi.jp'
    D_TOUR_BASE_URL = '{}/d-tour_season4'.format(BASE_URL)
    D_TOUR_CONNECT_SCHED_URL = '{}/connect'.format(D_TOUR_BASE_URL)
    D_TOUR_ARENA_SCHED_BASE_URL = '{}/arena'.format(D_TOUR_BASE_URL)
    D_TOUR_ARENA_REGIONS = [
        ('kyushu', '九州・山口'),
        ('kanto', '関東'),
        ('kitakanto', '北関東'),
        ('chubu', '中部')
    ]
    D_TOUR_CAL_PRODID = '-//D-TOUR Unofficial Calendar//D-TOUR Unofficial Calendar 1.0//'
    D_TOUR_ICAL_FILE = 'calendars/d-tour.ics'
    DATE_TIME_PAT = r'\d{4}/\d{1,2}/\d{1,2}'
    def __init__(self):
        super().__init__(self.D_TOUR_ICAL_FILE, self.D_TOUR_CAL_PRODID)

    def _get_connect_start_date(self, raw_date: str) -> datetime:
        try:
            formatted_date = re.sub(r'\([^)]+\)', '', raw_date)
            full_date = datetime.strptime(formatted_date, '%Y/%m/%d').replace(hour=10)
            return full_date
        except (ValueError, TypeError):
            return None

    def _get_timeless_arena_start_date(self, raw_date: str) -> datetime:
        temporary_start_time = 10
        try:
            formatted_date = re.sub(r'\([^)]+\)', '', raw_date)
            full_date = datetime.strptime(formatted_date, '%m/%d-').replace(year=datetime.now().year, hour=temporary_start_time)
            return full_date
        except (ValueError, TypeError):
            return None

    def _get_arena_start_date(self, raw_date: str) -> datetime:
        temporary_start_time = 10
        arena_datetime_pat = r'\d{4}/\d{1,2}/\d{1,2}（\d{1,2}:\d{1,2}）'
        arena_date_pat = r'\d{4}/\d{1,2}/\d{1,2}-'
        try:
            if re.match(arena_datetime_pat, raw_date):
                return datetime.strptime(raw_date, '%Y/%m/%d（%H:%M）')
            elif re.match(arena_date_pat, raw_date):
                return datetime.strptime(raw_date, '%Y/%m/%d-').replace(hour=temporary_start_time)
            else:
                return None
        except (ValueError, TypeError):
            return self._get_timeless_arena_start_date(raw_date)

    def _get_dtour_schedule(self, url: str) -> ResultSet:
        with urllib.request.urlopen(url) as f:
            raw_content = f.read()
        parsed_content = BeautifulSoup(raw_content, 'html.parser')
        sched_records = parsed_content.find_all('div', class_='scheduleBox')
        return sched_records

    def _get_prelim_period(self, prelim_dates: str) -> Tuple[datetime, datetime]:
        raw_dates = prelim_dates.split('\n\xa0～\xa0')
        if len(raw_dates) != 2:
            return None
        full_dates = []
        for raw_date in raw_dates:
            formatted_date = re.sub(r'\([^)]+\)', ' ', raw_date)
            formatted_date = re.sub('24:00', '23:59', formatted_date)
            full_date = datetime.strptime(formatted_date, '%Y/%m/%d %H:%M')
            full_dates.append(full_date)
        return full_dates[0], full_dates[1]

    def _get_prelim_data(self, entry: ResultSet, raw: Tag) -> Tuple[str, str]:
        prelim_dates = raw.td.get_text().replace('予選会場', '').replace(' ', '').strip()
        prelim_url = raw.a.get('href')
        prelim_url = '予選会場: {}'.format(prelim_url) if prelim_url else ''
        prelim_status = entry.find('a', title='予選状況')
        prelim_status_url = prelim_status.get('href') if prelim_status else ''
        prelim_info = '予選:\n{}\n{}\n予選状況:{}'.format(prelim_dates, prelim_url, prelim_status_url)
        return prelim_dates, prelim_info

    def _get_connect_events(self, record: ResultSet) -> List[DTourEvent]:
        stage = record.h4.get_text()
        details = record.table.find_all('tr')
        events = []
        for detail in details:
            field_header = detail.th.get_text()
            if '会場' in field_header:
                details_url = detail.td.a.get('href')
                details_url = '本戦会場: {}'.format(details_url) if details_url else ''
            elif '大会日程' in field_header:
                raw_date_match = re.search(self.DATE_TIME_PAT, detail.td.get_text())
                if not raw_date_match:
                    return None
                start_date = self._get_connect_start_date(raw_date_match.group())
                if not start_date:
                    return None
            elif '予選期間' in field_header:
                prelim_dates, prelim_info = self._get_prelim_data(record, detail)
        events.append(DTourEvent(stage, start_date, 'CONNECT', details_url, prelim_info))
        prelim_period = self._get_prelim_period(prelim_dates)
        if prelim_period:
            stage_prelim = '{} (予選)'.format(stage)
            prelim_start, prelim_end = prelim_period
            events.append(DTourEvent(stage_prelim, prelim_start, 'CONNECT', '', prelim_info, prelim_end))
        return events

    def _get_connect_schedule(self, url: str=D_TOUR_CONNECT_SCHED_URL) -> List[TourEvent]:
        sched_records = self._get_dtour_schedule(url)
        events = []
        for record in sched_records:
            stage_events = self._get_connect_events(record)
            if stage_events:
                events.extend(stage_events)
        return events

    def _get_arena_events(self, url: str, record: ResultSet, region_name: str) -> List[DTourEvent]:
        stage = record.h4.get_text()
        details = record.table.find_all('tr')
        events = []
        for detail in details:
            field_header = detail.th.get_text()
            if '会場' in field_header:
                location = detail.td.get_text().strip().replace('\n\n', '\n')
                description = '会場: {}'.format(location) if location else ''
            elif '大会日程' in field_header:
                raw_date = detail.td.get_text().replace('\n', '').replace(' ', '')
                start_date = self._get_arena_start_date(raw_date)
                if not start_date:
                    return None
            elif '予選期間' in field_header:
                prelim_dates, prelim_info = self._get_prelim_data(record, detail)
        events.append(DTourEvent(stage, start_date, 'ARENA {}エリア'.format(region_name), url, prelim_info))
        prelim_period = self._get_prelim_period(prelim_dates)
        if prelim_period:
            stage_prelim = '{} (予選)'.format(stage)
            prelim_start, prelim_end = prelim_period
            events.append(DTourEvent(stage_prelim, prelim_start, 'ARENA {}エリア'.format(region_name), url, prelim_info, prelim_end))
        return events

    def _get_arena_schedule(self, url: str, region_name: str) -> List[TourEvent]:
        sched_records = self._get_dtour_schedule(url)
        events = []
        for record in sched_records:
            stage_events = self._get_arena_events(url, record, region_name)
            if stage_events:
                events.extend(stage_events)
        return events

    def get_schedule(self) -> List[TourEvent]:
        connect_schedule = self._get_connect_schedule()
        arena_schedules = [self._get_arena_schedule('{}/{}.html'.format(self.D_TOUR_ARENA_SCHED_BASE_URL, r), n) for r,n in self.D_TOUR_ARENA_REGIONS]
        arena_schedule = list(itertools.chain.from_iterable(arena_schedules))
        return connect_schedule + arena_schedule
