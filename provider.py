import json
import logging
from urllib.request import urlopen

URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_1/sports_channels.json"

logging.basicConfig(
    level=logging.INFO,
    filename="stv10.log",
    format="%(asctime)s %(levelname)s %(message)s"
)

print("Downloading:", URL)

try:
    with urlopen(URL, timeout=60) as r:
        raw = r.read()

    print("Downloaded bytes:", len(raw))

    data = json.loads(raw)

    print("JSON type:", type(data).__name__)

    if isinstance(data, dict):
        print("Keys:", list(data.keys())[:20])

    if isinstance(data, list):
        print("Items:", len(data))

    with open("stv10.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

    print("SUCCESS")

except Exception as e:
    print("ERROR:", repr(e))
    raise
