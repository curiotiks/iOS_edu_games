import json
import subprocess

# Sample list of apps with appIds (replace with your own search logic)
apps = [
    {"appId": "553834731", "name": "Example Game 1"},
    {"appId": "123456789", "name": "Example Game 2"}
]

with open("data/app_ids.json", "w") as f:
    json.dump(apps, f)

# Now call the TypeScript review scraper
result = subprocess.run(["npx", "ts-node", "scripts/fetch_reviews.ts"], capture_output=True, text=True)

print("STDOUT:\n", result.stdout)
print("STDERR:\n", result.stderr)