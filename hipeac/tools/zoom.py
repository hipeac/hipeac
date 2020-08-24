import csv

from datetime import datetime
from typing import Dict, Optional, Tuple, Union


def to_bool(val: str) -> bool:
    return val == "Yes"


def to_datetime(dt: str) -> Optional[datetime]:
    return datetime.strptime(dt, "%b %d, %Y %H:%M:%S") if dt != "--" else None


def to_minutes(minutes: Union[str, int]) -> int:
    return int(minutes) if minutes != "--" else 0


def attendee_report(csv_path: str) -> Tuple[int, Dict]:
    """Given a standard Zoom CSV attendee report, returns massaged information.
    """
    duration = 0
    report = []
    field_map = {
        "email": ["Email", str],
        "first_name": ["First Name", str],
        "last_name": ["Last Name", str],
        "attended": ["Attended", to_bool],
        "join_time": ["Join Time", to_datetime],
        "leave_time": ["Leave Time", to_datetime],
        "minutes": ["Time in Session (minutes)", to_minutes],
    }

    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        section = None
        tmp = None

        for row in csv_reader:
            if len(row) > 2 and row[0] == "Topic":
                section = "duration"
                continue

            if len(row) == 2 and row[0] in ["Host Details", "Panelist Details", "Other Attended"]:
                section = None
                continue

            if len(row) == 2 and row[0] == "Attendee Details":
                section = "attendees"
                continue

            if not section:
                continue

            if not len(report) and section == "duration":
                duration = int(row[3])
                continue

            if not len(report) and row[0] == "Attended":
                fields = row
                continue

            tmp = dict(zip(fields, row))
            report.append({k: v[1](tmp[v[0]]) for k, v in field_map.items()})

    return duration, report
