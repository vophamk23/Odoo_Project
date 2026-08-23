# -*- coding: utf-8 -*-
"""
Pagination Demo Script for T4 Gate Keeper.
This script demonstrates the Cursor-Based Pagination mechanism of the Employee Sync API
by calling the local Odoo instance sequentially and retrieving paginated employee batches.
"""
import requests
import json
import time
import sys

# Fix UnicodeEncodeError on Windows (cp1252 console cannot encode Vietnamese characters)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://localhost:8070"
CLIENT_ID = "app_637da3fbc1a6e3e1430a12be2c5e51e4"
CLIENT_SECRET = "Puuf11KY4a6UMhbMW4e6V26ko5CDQzhn4KrVQPnVetU"
CONTROLLER_SN = "CTRL-HN-LOBBY-01"
PAGE_SIZE = 10


def get_token():
    print("[1] Requesting Auth Token...")
    url = f"{BASE_URL}/auth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    token = response.json()["api_token"]["token"]
    print(f"    -> Token obtained successfully: {token[:15]}...")
    return token


def run_pagination_demo():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print(f"\n[2] Starting Paginated Employee Sync (page_size = {PAGE_SIZE})...")

    # Initialize variables for the pagination loop
    page = 1
    has_next = True
    next_cursor_id = None
    latest_write_date = None
    total_fetched = 0

    while has_next:
        print("-" * 80)
        print(f"PAGE {page}:")

        # Build the payload
        payload = {"controller_sn": CONTROLLER_SN, "page_size": PAGE_SIZE}
        if next_cursor_id and latest_write_date:
            payload["next_cursor_id"] = next_cursor_id
            payload["latest_write_date"] = latest_write_date

        print(f"  Sending Request Payload: {json.dumps(payload, ensure_ascii=False)}")

        # Call the endpoint
        url = f"{BASE_URL}/api/v1/ControllerEmployeeSync"
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        duration = int((time.time() - start_time) * 1000)

        if response.status_code != 200:
            print(f"  Error: Received HTTP Status {response.status_code}")
            print(f"  Response Body: {response.text}")
            break

        res_json = response.json()
        data = res_json.get("data", {}).get("data", {})

        new_employees = data.get("new", [])
        update_employees = data.get("update", [])
        deleted_employees = data.get("deleted", [])

        count_page = len(new_employees) + len(update_employees) + len(deleted_employees)
        total_fetched += count_page

        has_next = data.get("has_next_page", False)
        next_cursor_id = data.get("next_cursor_id")
        latest_write_date = data.get("latest_write_date")

        print(f"  Received Response ({duration} ms):")
        print(json.dumps(res_json, indent=2, ensure_ascii=False))

        # Break after page 3 to keep demo concise if there are many pages
        if page >= 5 and has_next:
            print("\n... Demo truncated after 3 pages (to keep output short) ...")
            break

        page += 1
        time.sleep(0.5)  # Short delay between calls

    print("=" * 80)
    print(
        f"Demo Sync completed. Fetched a total of {total_fetched} employees across pages."
    )


if __name__ == "__main__":
    try:
        run_pagination_demo()
    except Exception as e:
        print(f"\n[ERROR] Failed to run demo: {e}")
