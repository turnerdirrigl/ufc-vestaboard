import os, requests
from datetime import datetime, timezone

VB_KEY = os.environ["VESTABOARD_KEY"]
WINDOW_MIN = float(os.environ.get("WINDOW_MIN", "10"))
SKIP = ("fight night", "contender", "road to ufc")

def parse(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)

r = requests.get(
    "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard",
    timeout=30,
)
r.raise_for_status()
calendar = r.json()["leagues"][0].get("calendar", [])

now = datetime.now(timezone.utc)
message = None

for entry in calendar:
    label = entry.get("label", "")
    low = label.lower()
    if not low.startswith("ufc") or any(s in low for s in SKIP):
        continue
    try:
        mins = (parse(entry["startDate"]) - now).total_seconds() / 60
    except (KeyError, ValueError):
        continue
    if 0 < mins <= WINDOW_MIN:
        head = label.partition(":")[0].strip()
        message = f"{head}\nSTARTS IN\n{int(mins) + 1} MIN".upper()
        break

if not message:
    print("No major card starting soon.")
else:
    r = requests.post(
        "https://cloud.vestaboard.com/",
        headers={"X-Vestaboard-Token": VB_KEY, "Content-Type": "application/json"},
        json={"text": message},
        timeout=30,
    )
    r.raise_for_status()
    print("Posted:", message)
