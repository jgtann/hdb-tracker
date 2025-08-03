import pandas as pd
import matplotlib.pyplot as plt
import requests
import datetime
import time
import os

# Create output directory if not exists
output_dir = "chart"
os.makedirs(output_dir, exist_ok=True)

resource_id = "83b2fc37-ce8c-4df4-968b-370fd818138b"
api_base = "https://data.gov.sg/api/action/datastore_search"

all_records = []
offset = 0
batch_size = 10000

print("🔄 Fetching HDB resale records...")

while True:
    url = f"{api_base}?resource_id={resource_id}&limit={batch_size}&offset={offset}"
    res = requests.get(url)
    res.raise_for_status()
    result = res.json()["result"]
    
    records = result["records"]
    if not records:
        break

    all_records.extend(records)
    print(f"✅ Fetched {len(records)} records (offset: {offset})")
    offset += batch_size
    time.sleep(0.5)

print(f"📦 Total records fetched: {len(all_records)}")

df = pd.DataFrame(all_records)
df["resale_price"] = pd.to_numeric(df["resale_price"], errors="coerce")
df = df.dropna(subset=["town", "resale_price"])
df = df[df["resale_price"] > 100000]

# Plot
median_prices = df.groupby("town")["resale_price"].median().sort_values()
plt.figure(figsize=(10, 6))
median_prices.plot(kind="barh", color="skyblue")
plt.title("🏘️ Median HDB Resale Price by Town")
plt.xlabel("SGD")
plt.tight_layout()

# Save
today = datetime.date.today()
filename = f"{output_dir}/median_resale_prices_{today}.png"
plt.savefig(filename)
print(f"✅ Chart saved to: {filename}")
