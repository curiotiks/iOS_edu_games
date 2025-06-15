import json
import subprocess


# Update to reading in the saved data and constructing the json structure
# BUT TRY IT WITH THIS STRUCTURE TO TEST IT FIRST
apps = [
  {
    "appId": "1456710300",
    "name": "Among Us!"
  },
  {
    "appId": "1463372439",
    "name": "Mario Kart Tour"
  },
  {
    "appId": "1483058899",
    "name": "Call of Duty®: Mobile"
  }
]

with open("data/app_ids.json", "w") as f:
    json.dump(apps, f)

# Now call the TypeScript review scraper
result = subprocess.run(["npx", "ts-node", "scripts/fetch_reviews.ts"], capture_output=True, text=True)

print("STDOUT:\n", result.stdout)
print("STDERR:\n", result.stderr)