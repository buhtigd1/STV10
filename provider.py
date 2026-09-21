#!/usr/bin/env python3

import json
import logging
from urllib.request import urlopen

JSON_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_1/sports_channels.json"

M3U_FILE = "stv10.m3u"
LOG_FILE = "stv10.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_field(item, names, default=""):
    for name in names:
        if name in item and item[name\]:
            return item[name]
    return default

def main():
    logging.info("Downloading JSON from GitHub")

    with urlopen(JSON_URL) as response:
        data = json.load(response)

    logging.info(f"Loaded {len(data)} channels")

    count = 0

    with open(M3U_FILE, "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n")

        for item in data:

            name = get_field(
                item,
                ["name", "title", "channel_name"],
                "Unknown"
            )

            logo = get_field(
                item,
                ["logo", "logo_url", "image"],
                ""
            )

            group = get_field(
                item,
                ["group", "category", "group-title"],
                "Sports"
            )

            stream = get_field(
                item,
                [
                    "url",
                    "stream_url",
                    "stream",
                    "play_url",
                    "source"
                ]
            )

            if not stream:
                logging.warning(f"Skip: {name} (no stream URL)")
                continue

            m3u.write(
                f'#EXTINF:-1 tvg-name="{name}" '
                f'tvg-logo="{logo}" '
                f'group-title="{group}",{name}\n'
            )

            m3u.write(stream + "\n")

            count += 1

    logging.info(f"Generated {M3U_FILE}")
    logging.info(f"Channels written: {count}")

    print(f"Done. {count} channels saved to {M3U_FILE}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(str(e))
        print("ERROR:", e)
        raise
