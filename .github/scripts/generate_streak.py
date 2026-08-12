import json
import os
import urllib.request
from datetime import date, timedelta
from xml.sax.saxutils import escape

USERNAME = "krishna-choudhary2607"
TOKEN = os.environ["GITHUB_TOKEN"]

query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

payload = json.dumps({"query": query, "variables": {"login": USERNAME}}).encode()
request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "krishna-choudhary2607-streak-generator",
    },
    method="POST",
)

with urllib.request.urlopen(request, timeout=30) as response:
    data = json.load(response)

if data.get("errors"):
    raise RuntimeError(data["errors"])

calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
days.sort(key=lambda x: x["date"])
counts = {day["date"]: day["contributionCount"] for day in days}

# Calculate current streak. A streak can end today or yesterday.
today = date.today()
current = 0
cursor = today
if counts.get(cursor.isoformat(), 0) == 0:
    cursor -= timedelta(days=1)
while counts.get(cursor.isoformat(), 0) > 0:
    current += 1
    cursor -= timedelta(days=1)

# Calculate longest streak across the complete calendar.
longest = 0
running = 0
for day in days:
    if day["contributionCount"] > 0:
        running += 1
        longest = max(longest, running)
    else:
        running = 0

total = calendar["totalContributions"]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="220" viewBox="0 0 900 220" role="img" aria-label="GitHub streak stats for {USERNAME}">
  <rect width="900" height="220" rx="12" fill="#1a1b27"/>
  <text x="450" y="48" text-anchor="middle" fill="#70a5fd" font-family="Arial, Helvetica, sans-serif" font-size="24" font-weight="700">GitHub Streak</text>
  <text x="450" y="78" text-anchor="middle" fill="#a9b1d6" font-family="Arial, Helvetica, sans-serif" font-size="14">{escape(USERNAME)}</text>

  <rect x="45" y="105" width="250" height="80" rx="10" fill="#24283b"/>
  <rect x="325" y="105" width="250" height="80" rx="10" fill="#24283b"/>
  <rect x="605" y="105" width="250" height="80" rx="10" fill="#24283b"/>

  <text x="170" y="132" text-anchor="middle" fill="#a9b1d6" font-family="Arial, Helvetica, sans-serif" font-size="13">Current Streak</text>
  <text x="170" y="164" text-anchor="middle" fill="#70a5fd" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="700">{current} days</text>

  <text x="450" y="132" text-anchor="middle" fill="#a9b1d6" font-family="Arial, Helvetica, sans-serif" font-size="13">Longest Streak</text>
  <text x="450" y="164" text-anchor="middle" fill="#70a5fd" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="700">{longest} days</text>

  <text x="730" y="132" text-anchor="middle" fill="#a9b1d6" font-family="Arial, Helvetica, sans-serif" font-size="13">Contributions</text>
  <text x="730" y="164" text-anchor="middle" fill="#70a5fd" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="700">{total}</text>
</svg>
'''

os.makedirs("profile", exist_ok=True)
with open("profile/streak.svg", "w", encoding="utf-8") as file:
    file.write(svg)
