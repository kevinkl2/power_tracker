import datetime
import os
import time
from enum import Enum
from os import system, name
from dotenv import load_dotenv

from pyHS100 import SmartPlug


class EventType(Enum):
    ON = "on"
    OFF = "off"


class MockPlug(object):
    def get_emeter_realtime(self):
        f = open("power.txt", "r")
        return {"power": float(f.read())}

    def get_emeter_daily(self, year, month):
        f = open("kwh.txt", "r")
        return {13: float(f.read())}


class Event(object):
    def __init__(self, event, duration, kwh, kwh_diff, avg):
        self.event = event
        self.duration = duration
        self.kwh = kwh
        self.kwh_diff = kwh_diff
        self.avg = avg


def clear():
    if name == "nt":
        _ = system("cls")
    else:
        _ = system("clear")


def initialize():
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    def update_time_tracker(event):
        time_tracker.append(
            Event(
                event=event,
                duration=current_dt - prev_event_time,
                kwh=plug.get_emeter_daily(year=current_dt.year, month=current_dt.month)[
                    current_dt.day
                ],
                kwh_diff=0,
                avg=0,
            ).__dict__
        )

    if len(time_tracker) == 0:
        current_dt = datetime.datetime.now()
        if plug.get_emeter_realtime()["power"] >= threshold_watt:
            update_time_tracker(EventType.ON.value)
            prev_event = EventType.ON.value
        else:
            update_time_tracker(EventType.OFF.value)
            prev_event = EventType.OFF.value


def print_historical_info():
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    print(time_tracker[-7:])
    print()
    for i in time_tracker[-7:]:
        print(
            "event: {}, duration: {}, kwh: {}, avg: {}".format(
                i["event"], i["duration"], i["kwh"], i["avg"]
            )
        )
    print()
    print(prev_event_time)
    print(prev_event)
    print()


def print_current_info(current_dt, current_power, kwh):
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    hours = current_dt.hour + (current_dt.minute / 60) + (current_dt.second / 3600)

    print("{} watts".format(current_power))
    print("{} kwh".format(kwh))
    print("{:.2f} watts".format(kwh / hours * 1000))


def calculate_average_power(kwh, current_dt):
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    return (
        abs(kwh - time_tracker[-1]["kwh"] + time_tracker[-1]["kwh_diff"])
        * 1000
        / (
            (
                current_dt - prev_event_time + time_tracker[-1]["duration"]
            ).total_seconds()
            / 3600
        )
    )


def update(kwh, current_power, current_dt):
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    def update_time_tracker(event):
        time_tracker.append(
            Event(
                event=event,
                duration=current_dt - prev_event_time,
                kwh=kwh,
                kwh_diff=round(kwh - time_tracker[-1]["kwh"], 5),
                avg=calculate_average_power(kwh, current_dt),
            ).__dict__
        )

    if prev_event == EventType.OFF.value:
        if current_power >= threshold_watt:
            update_time_tracker(EventType.OFF.value)
            prev_event = EventType.ON.value
            prev_event_time = current_dt
        else:
            print("Current Duration: {}".format(current_dt - prev_event_time))
    else:
        if current_power < threshold_watt:
            update_time_tracker(EventType.ON.value)
            prev_event = EventType.OFF.value
            prev_event_time = current_dt
        else:
            print("{}".format(current_dt - prev_event_time))


def start():
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    while True:
        try:
            current_dt = datetime.datetime.now()

            current_power = plug.get_emeter_realtime()["power"]

            kwh = plug.get_emeter_daily(year=current_dt.year, month=current_dt.month)[
                current_dt.day
            ]

            clear()
            print_historical_info()
            print_current_info(current_dt, current_power, kwh)

            update(kwh, current_power, current_dt)

            time.sleep(1)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    load_dotenv()

    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    time_tracker = []

    prev_event_time = datetime.datetime.now()

    # prevEventTime = datetime.datetime.strptime("2020-09-14 12:57:02.311040", "%Y-%m-%d %H:%M:%S.%f")

    prev_event = EventType.OFF.value

    plug = SmartPlug(os.getenv("IP"))

    # plug = MockPlug()

    threshold_watt = 150

    initialize()

    start()
