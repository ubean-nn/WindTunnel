#!/usr/bin/env python3
import time
import sys
import RPi.GPIO as GPIO
from hx711v0_5_1 import HX711
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# --- Configure Modules and Pins ---
# Each tuple is (DATA pin, CLK pin). Change these to the GPIO.BCM numbers you're using.
MODULE_PINS = [
    (5, 6),    # Module 1
    (26, 6),  # Module 2
    (20, 6),  # Module 3
    (16, 6),  # Module 4
]

# Reference unit you calculated; adjust per your calibration
REFERENCE_UNIT = 114

# Reading format constants
READ_FMT = ("MSB", "MSB")

# --- Graphing Setup ---
MAX_POINTS = 100
timestamps = deque(maxlen=MAX_POINTS)
weight_histories = [deque(maxlen=MAX_POINTS) for _ in MODULE_PINS]
fig, ax = plt.subplots()
lines = [ax.plot([], [], label=f"Module {i+1}")[0] for i in range(len(MODULE_PINS))]
ax.legend()
ax.set_xlabel("Time")
ax.set_ylabel("Weight (g)")


def setup_modules(pins_list):
    """Instantiate and configure an HX711 for each pin pair."""
    modules = []
    for data_pin, clk_pin in pins_list:
        hx = HX711(data_pin, clk_pin)
        hx.setReadingFormat(*READ_FMT)
        hx.autosetOffset()
        hx.setReferenceUnit(REFERENCE_UNIT)
        modules.append(hx)
    return modules


def read_all(modules):
    """Poll each HX711 once and return list of weights (grams)."""
    readings = []
    for idx, hx in enumerate(modules, start=1):
        raw = hx.getRawBytes()
        weight = hx.rawBytesToWeight(raw)
        readings.append((idx, weight))
    return readings


def main(poll_interval=1.0):
    # Use BCM numbering
    GPIO.setmode(GPIO.BCM)

    # Instantiate modules
    modules = setup_modules(MODULE_PINS)
    print(f"[INFO] Initialized {len(modules)} HX711 modules.")

    def animate(frame):
        data = read_all(modules)
        timestamps.append(time.strftime("%H:%M:%S"))
        for idx, w in data:
            weight_histories[idx-1].append(w)
        for line, hist in zip(lines, weight_histories):
            line.set_data(range(len(hist)), list(hist))
        ax.relim()
        ax.autoscale_view()
        return lines

    ani = animation.FuncAnimation(fig, animate, interval=poll_interval*1000)
    plt.ion()
    plt.show()

    try:
        while True:
            plt.pause(poll_interval)

    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] Cleaning up GPIO and exiting...")
        GPIO.cleanup()
        plt.close(fig)
        sys.exit(0)


if __name__ == "__main__":
    # Optionally accept a custom poll interval in seconds
    interval = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    main(poll_interval=interval)