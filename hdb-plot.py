# hdb_plot_dynamic.py

import requests
import pandas as pd
import plotly.express as px
import datetime
import os

# Prepare
API = "https://data.gov.sg/api/action/datastore_search"
RESOURCE_ID = "83b2fc37-ce8c-4df4-968b-370fd818138b"
BATCH_SIZE = 10000
all_records = []
offset = 0

print("🔄 Fetching data from data.gov.sg...")

while True:
    url = f"{API}?resource_id={RESOURCE_ID}&limit={BATCH_SIZE}&offset={offset}"
    res = requests.get(url)
    res.raise_for_status()
    records = res.json()["result"]["records"]
    if not records:
        break
    all_records.extend(records)
    print(f"✅ Retrieved {len(records)} records (offset {offset})")
    offset += BATCH_SIZE

# Prepare DataFrame
df = pd.DataFrame(all_records)
df["resale_price"] = pd.to_numeric(df["resale_price"], errors="coerce")
df = df.dropna(subset=["town", "resale_price", "month"])
df = df[df["resale_price"] > 100000]
df["month"] = pd.to_datetime(df["month"])

# Compute medians
latest_month = df["month"].max().strftime("%Y-%m")
earliest_month = df["month"].min().strftime("%Y-%m")
summary = df.groupby("town")["resale_price"].median().sort_values()

# Create dynamic chart
fig = px.bar(
    summary,
    orientation='h',
    labels={"value": "Median Resale Price (SGD)", "town": "Town"},
    title=f"🏘️ Median HDB Resale Price by Town<br><sup>Data from {earliest_month} to {latest_month}</sup>",
    template="plotly_white"
)
fig.update_layout(height=800)

# Save chart
os.makedirs("chart", exist_ok=True)
output_path = os.path.join("chart", "resale_chart.html")
fig.write_html(output_path, include_plotlyjs="cdn")
print(f"📊 Chart saved to: {output_path}")
