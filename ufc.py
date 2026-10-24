import os, requests
from datetime import datetime, timezone

UFC_KEY = os.environ["UFCAL_KEY"]
VB_KEY = os.environ["VESTABOARD_KEY"]

r = requests.get(
    "https://api.ufcalendar.com/v1/events",
    params={"org": "ufc"},
    headers={"Authorization": f"Bearer {UFC_KEY}"},
    timeout=30,
)
r.raise_for_status()
ev = r.json()["data"][0]  # soonest upcoming event

start = datetime.fromisoformat(ev["starts_at"].replace("Z", "+00:00"))
days = (start.date() - datetime.now(timezone.utc).date()).days
when = "TODAY" if days <= 0 else f"IN {days} DAY" + ("S" if days != 1 else "")

head, _, rest = ev["title"].partition(":")
text = "\n".join([head.strip(), rest.strip(), when]).upper()

r = requests.post(
    "https://cloud.vestaboard.com/",
    headers={"X-Vestaboard-Token": VB_KEY, "Content-Type": "application/json"},
    json={"text": text},
    timeout=30,
)
r.raise_for_status()
