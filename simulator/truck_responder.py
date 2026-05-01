import time
import requests
import argparse

API_BASE = "http://localhost:5000"

# Simple truck responder that polls notifications and auto-ACK then auto-collects

def run(truck_id, poll_interval=5, ack_delay=2, collect_delay=5):
    print(f"Truck responder running for {truck_id}: poll {poll_interval}s")
    while True:
        try:
            url = f"{API_BASE}/api/notifications?all=true&truck_id={truck_id}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                notes = r.json()
                for n in notes:
                    # look for SENT notifications assigned to this truck
                    if n.get('status') == 'SENT' and (n.get('truck_id') == truck_id or not n.get('truck_id')):
                        nid = n.get('notif_id')
                        bin_id = n.get('bin_id')
                        print(f"Found SENT notif {nid} for {bin_id}, ACKing")
                        try:
                            requests.post(f"{API_BASE}/api/notifications/respond", json={"notif_id": nid, "action": "ACK", "truck_id": truck_id}, timeout=5)
                        except Exception as e:
                            print("ACK failed", e)
                        time.sleep(ack_delay)
                        print(f"Collecting {bin_id} by {truck_id}")
                        try:
                            requests.post(f"{API_BASE}/api/collect_by_truck", json={"bin_id": bin_id, "truck_id": truck_id}, timeout=5)
                        except Exception as e:
                            print("Collect failed", e)
                        time.sleep(collect_delay)
        except Exception as e:
            print("Error polling notifications:", e)
        time.sleep(poll_interval)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--truck', required=True, help='Truck id (e.g. TRUCK_1)')
    p.add_argument('--poll', type=int, default=5)
    args = p.parse_args()
    run(args.truck, poll_interval=args.poll)
