import datetime
import os
import time
from enum import Enum
from os import system, name

import plotext as plt
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
        return {14: float(f.read())}


class Event(object):
    def __init__(self, event, duration, kwh, kwh_diff, avg, watts):
        self.event = event
        self.duration = duration
        self.kwh = kwh
        self.kwh_diff = kwh_diff
        self.avg = avg
        self.watts = watts


class Hour(object):
    def __init__(self, current_hour, start):
        self.hour = current_hour
        self.start_kwh = start
        self.stop_kwh = start

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
    global graph_y_watt
    global graph_y_volt
    global graph_y_kwh
    global graph_y_kwh_hour
    global graph_y_volt_day

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
                watts=0
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

    graph_y_watt = [0]
    graph_y_volt = [0]
    graph_y_kwh = []
    graph_y_kwh_hour = []
    graph_y_volt_day = []


def print_historical_info(file):
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    print(time_tracker[-7:])
    print()
    for i in time_tracker[-7:]:
        print(
            "event: {}, duration: {}, kwh: {}, avg: {}, watts: {}".format(
                i["event"], i["duration"], i["kwh"], i["avg"], i["watts"]
            )
        )
    print()
    print(prev_event_time)
    print(prev_event)
    print()

    file.write(str(time_tracker[-7:]))
    file.write("\n\n")
    for i in time_tracker[-7:]:
        file.write(
            "event: {}, duration: {}, kwh: {}, avg: {}, watts: {}".format(
                i["event"], i["duration"], i["kwh"], i["avg"], i["watts"]
            )
        )
        file.write("\n")
    file.write("\n\n")
    file.write(str(prev_event_time))
    file.write("\n")
    file.write(str(prev_event))
    file.write("\n\n")


def print_current_info(current_dt, current_power, current_voltage, kwh, kwh_month, file):
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt
    global graph_y_watt
    global graph_y_volt
    global graph_y_kwh
    global graph_y_kwh_hour
    global prev_loop_time
    global graph_y_volt_day

    hours = current_dt.hour + (current_dt.minute / 60) + (current_dt.second / 3600)

    print("{} watts".format(current_power))
    print("{} volts".format(current_voltage))
    print("{} kwh".format(kwh))
    print("{:.2f} watts".format(kwh / hours * 1000))

    file.write("{} watts".format(current_power))
    file.write("\n")
    file.write("{} volts".format(current_voltage))
    file.write("\n")
    file.write("{} kwh".format(kwh))
    file.write("\n")
    file.write("{:.2f} watts".format(kwh / hours * 1000))
    file.write("\n")

    current_voltage = current_voltage * 10

    if len(graph_y_watt) == 1:
        graph_y_watt = [current_power] * 300
    else:
        graph_y_watt = graph_y_watt[-299:] + [current_power]

    if len(graph_y_volt) == 1:
        graph_y_volt = [current_voltage] * 300
    else:
        graph_y_volt = graph_y_volt[-299:] + [current_voltage]

    if len(graph_y_kwh) == 0:
        graph_y_kwh = [kwh]
        graph_y_kwh_hour = [Hour(current_hour=current_dt.hour,start=kwh*1000)]
        graph_y_volt_day = [current_voltage]
    elif kwh < graph_y_kwh[-1]:
        graph_y_kwh = [kwh]
        graph_y_kwh_hour = [Hour(current_hour=current_dt.hour,start=kwh*1000)]
        graph_y_volt_day = [current_voltage]
    else:
        graph_y_kwh.append(kwh)
        graph_y_volt_day.append(current_voltage)
        if current_dt.hour > prev_loop_time.hour:
            graph_y_kwh_hour.append(Hour(current_hour=current_dt.hour,start=kwh*1000))
        else:
            graph_y_kwh_hour[-1].stop_kwh = kwh*1000
        prev_loop_time = current_dt

    temp_graph_y_kwh = []
    temp_hours = []

    if len(graph_y_kwh_hour) <= 1:
        temp_graph_y_kwh = [0.0010]
        temp_hours = ["-1"]

    for hour in graph_y_kwh_hour:
        temp_hours.append("{}:{:.0f}".format(hour.hour, hour.stop_kwh-hour.start_kwh))
        temp_graph_y_kwh.append(hour.stop_kwh - hour.start_kwh)

    plt.clear_figure()
    plt.clear_data()
    plt.subplots(3, 2)
    plt.limitsize(False, True)

    plt.subplot(1, 1)
    plt.title("Watts")
    # plt.colorless()
    plt.grid(None, True)
    plt.plotsize(None, 20)
    plt.plot(graph_y_watt, marker="dot")

    plt.subplot(1, 2)
    plt.title("Volts*10")
    plt.grid(None, True)
    plt.plotsize(None, 20)
    plt.plot(graph_y_volt, marker="dot")

    plt.subplot(2, 1)
    plt.span(2, 1)
    plt.title("Wh Today")
    # plt.grid(None, True)
    plt.plotsize(383, 20)
    # plt.plot(graph_y_kwh, marker="dot")
    plt.bar(temp_hours, temp_graph_y_kwh, marker="dot")

    plt.subplot(3, 1)
    plt.span(2, 1)
    plt.title("Volts*10 Today")
    plt.grid(None, True)
    plt.plotsize(None, 20)
    plt.plot(graph_y_volt_day, marker="dot")

    # plt.show()
    plt.build()
    print(plt.time())
    plt.savefig(os.getenv("GRAPH_FILE"))
    plt.savefig(os.getenv("GRAPH_FILE_TXT"))

    file.write("{:.5f} seconds".format(plt.time()))
    file.write("\n")


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


def update(kwh, current_power, current_dt, file):
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    def update_time_tracker(event, watts):
        time_tracker.append(
            Event(
                event=event,
                duration=current_dt - prev_event_time,
                kwh=kwh,
                kwh_diff=round(kwh - time_tracker[-1]["kwh"], 5),
                avg=calculate_average_power(kwh, current_dt),
                watts=watts
            ).__dict__
        )

    if prev_event == EventType.OFF.value:
        if current_power >= threshold_watt:
            update_time_tracker(EventType.OFF.value, current_power)
            prev_event = EventType.ON.value
            prev_event_time = current_dt
        else:
            print("Current Duration: {}".format(current_dt - prev_event_time))
            file.write("Current Duration: {}".format(current_dt - prev_event_time))
    else:
        if current_power < threshold_watt:
            update_time_tracker(EventType.ON.value, current_power)
            prev_event = EventType.OFF.value
            prev_event_time = current_dt
        else:
            print("Current Duration: {}".format(current_dt - prev_event_time))
            file.write("Current Duration: {}".format(current_dt - prev_event_time))


def start():
    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt

    while True:
        try:
            start_time = time.time()
            current_dt = datetime.datetime.now()

            realtime = plug.get_emeter_realtime()
            current_power = realtime["power"]
            current_voltage = realtime["voltage"]

            kwh_month = plug.get_emeter_daily(year=current_dt.year, month=current_dt.month)
            test = "{} seconds".format(time.time() - start_time)

            kwh = kwh_month[current_dt.day]

            with open(os.getenv("FILE"), "w") as file:
                clear()
                print_historical_info(file)
                print_current_info(current_dt, current_power, current_voltage, kwh, kwh_month, file)

                update(kwh, current_power, current_dt, file)
                file.write("\n\n{} seconds".format(time.time() - start_time))
                print("{} seconds".format(time.time() - start_time))
                print(test)

            # time.sleep(1)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    load_dotenv()

    global time_tracker
    global prev_event_time
    global prev_event
    global plug
    global threshold_watt
    global graph_y_watt
    global graph_y_volt
    global graph_y_kwh
    global graph_y_kwh_hour
    global prev_loop_time
    global graph_y_volt_day

    time_tracker = []

    prev_event_time = datetime.datetime.now()
    prev_loop_time = datetime.datetime.now()

    # prevEventTime = datetime.datetime.strptime("2020-09-14 12:57:02.311040", "%Y-%m-%d %H:%M:%S.%f")

    prev_event = EventType.OFF.value

    plug = SmartPlug(host=os.getenv("IP"), cache_ttl=0)

    # plug = MockPlug()

    threshold_watt = 150

    initialize()

    start()
