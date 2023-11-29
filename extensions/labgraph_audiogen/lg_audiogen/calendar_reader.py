from typing import Dict
from icalendar import Calendar
from main import generate_text_music


def transform_calendar_to_dict(filepath):
    with open(filepath, "rb") as calendar_file:
        calendar = Calendar.from_ical(calendar_file.read())
    
        events = {}
        for component in calendar.walk():
            if component.name == "VEVENT":
                duration = component.decoded("dtend") - component.decoded("dtstart")
                start_date = component.decoded("dtstart").strftime("%Y-%m-%d")
                if start_date not in events:
                    events[start_date] = []
                events[start_date].append({
                    "summary": component.get("summary"),
                    # "description": component.get("description"),
                    "start": component.decoded("dtstart"),
                    "end": component.decoded("dtend"),
                    "duration": duration,
                })
        return events


def transform_duration_to_minutes(duration):
    # duration is in a HH:MM:SS format
    duration = str(duration)
    hours, minutes, seconds = duration.split(":")
    total_seconds = 60 * (int(hours) * 60 + int(minutes))
    return total_seconds

events = transform_calendar_to_dict("ClassesExample.ics")


print("Select a date of the calendar")
print(", ".join(events.keys()))
selected_date = input("Date: ")
if selected_date not in events:
    print("Invalid date")
    exit(1)

print(f"The events of the {selected_date} are:")
for event in events[selected_date]:
    print(f"\t{event['summary']}")
    print(f"\t\t{event['start']}")
    print(f"\t\t{event['end']}")
    print(f"\t\t{event['duration']}")
    print()
    music_duration = transform_duration_to_minutes(event['duration']) // 360
    print([event['summary']], music_duration, None, "musicgen-small")
    generate_text_music([event['summary']], music_duration, None, "musicgen-small")
