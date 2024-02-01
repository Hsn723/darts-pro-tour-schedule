import hashlib
import os
from icalendar import Calendar

def output_calendar(filename: str, calendar: Calendar):
    contents = calendar.to_ical()
    cur_hash = hashlib.md5(contents).hexdigest()
    if not os.path.exists(filename) or hashlib.md5(open(filename, 'rb').read()).hexdigest() != cur_hash:
        with open(filename, 'wb') as f:
            f.write(contents)
