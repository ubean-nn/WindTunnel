#!/usr/bin/env python3
import time
import sys
import RPi.GPIO as GPIO
from hx711v0_5_1 import HX711

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

    try:
        while True:
            data = read_all(modules)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"--- {timestamp} ---")
            for idx, w in data:
                print(f"Module {idx}: {w:.2f} g")
            time.sleep(poll_interval)

    except (KeyboardInterrupt, SystemExit):
        print("\n[INFO] Cleaning up GPIO and exiting...")
        GPIO.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    # Optionally accept a custom poll interval in seconds
    interval = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    main(poll_interval=interval)