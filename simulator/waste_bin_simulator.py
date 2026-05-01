import time
import random
import requests
import argparse
import os

API_URL = "http://localhost:5000/api/bin/update"

bins = [
    {"id": "BIN_101", "lat": 10.8505, "lon": 76.2711},
    {"id": "BIN_102", "lat": 10.8550, "lon": 76.2750},
    {"id": "BIN_103", "lat": 10.8600, "lon": 76.2800},
    {"id": "BIN_104", "lat": 10.8480, "lon": 76.2680},
    {"id": "BIN_105", "lat": 10.8620, "lon": 76.2830}
]

levels = {b["id"]: random.randint(0, 30) for b in bins}

def send_payload(payload):
    try:
        resp = requests.post(API_URL, json=payload, timeout=5)
        resp.raise_for_status()
        print("Sent:", payload)
    except Exception as e:
        print("Failed to send", payload, "error:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='Run in demo mode with short interval')
    parser.add_argument('--interval', type=int, help='Interval in seconds to send data')
    args = parser.parse_args()

    # priority: explicit --interval > SIM_INTERVAL env var > demo flag > default 600
    if args.interval:
        interval = args.interval
    else:
        env_iv = os.environ.get('SIM_INTERVAL')
        if env_iv:
            try:
                interval = int(env_iv)
            except Exception:
                interval = 600
        else:
            # demo mode uses 50s interval for a slower demo loop
            interval = 50 if args.demo else 600

    print(f"Simulator interval set to {interval}s")

    while True:
        for b in bins:
            levels[b["id"]] += random.randint(5, 15)
            if levels[b["id"]] > 100:
                levels[b["id"]] = 100

            payload = {
                "bin_id": b["id"],
                "level": levels[b["id"]],
                "latitude": b["lat"],
                "longitude": b["lon"]
            }

            send_payload(payload)

        time.sleep(interval)
