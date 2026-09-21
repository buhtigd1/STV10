#!/usr/bin/env python3

import json
import logging

JSON_FILE = "https://github.com/darkbyteprojects/iptv_png/blob/main/provider_1/sports_channels.json"
M3U_FILE = "stv10.m3u"
LOG_FILE = "stv10.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        channels = json.load(f)

    with open(M3U_FILE, "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n")

        count = 0

        for ch in channels:

            name = ch.get("name", "Unknown")
            logo = ch.get("logo", "")
            group = ch.get("group", "Sports")
            url = ch.get("url") or ch.get("stream_url")

            if not url:
                logging.warning(f"Skipping {name}: no stream URL")
                continue

            m3u.write(
                f'#EXTINF:-1 tvg-name="{name}" '
                f'tvg-logo="{logo}" '
                f'group-title="{group}",{name}\n'
            )

            m3u.write(url + "\n")

            count += 1

    logging.info(f"Generated {M3U_FILE}")
    logging.info(f"Total channels: {count}")

    print(f"Done: {count} channels written to {M3U_FILE}")

except Exception as e:
    logging.exception(str(e))
    print("ERROR:", e)
