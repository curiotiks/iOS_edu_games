import json
import subprocess

# Test data for json structure
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

# app_id = "1456710300"  # Example app ID to test

# Now call the TypeScript review scraper
print("Starting subprocess")
# result = subprocess.run(["npx", "ts-node", "scripts/fetch_reviews.ts", app_id], capture_output=True, text=True)

# print("STDOUT:\n", result.stdout)
# print("STDERR:\n", result.stderr)