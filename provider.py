#!/usr/bin/env python3

import json
from urllib.request import urlopen

JSON_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_1/sports_channels.json"

OUTPUT_M3U = "stv10.m3u"
OUTPUT_LOG = "stv10.log"


def write_kodi_props(m3u, link, drm_scheme, drm_key):
    if not drm_key:
        return

    drm_scheme = (drm_scheme or "").lower()

    if drm_scheme != "clearkey":
        return

    manifest_type = "hls"

    if ".mpd" in link.lower():
        manifest_type = "mpd"

    m3u.write("#KODIPROP:inputstream=inputstream.adaptive\n")
    m3u.write(
        f"#KODIPROP:inputstream.adaptive.manifest_type={manifest_type}\n"
    )
    m3u.write(
        "#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey\n"
    )
    m3u.write(
        f"#KODIPROP:inputstream.adaptive.license_key={drm_key}\n"
    )


def main():

    print("Downloading JSON...")

    with urlopen(JSON_URL, timeout=60) as resp:
        channels = json.loads(resp.read().decode("utf-8"))

    total = 0
    drm_total = 0

    with open(OUTPUT_M3U, "w", encoding="utf-8") as m3u, \
         open(OUTPUT_LOG, "w", encoding="utf-8") as log:

        m3u.write("#EXTM3U\n")

        for channel in channels:

            channel_name = channel.get("name", "Unknown")
            logo = channel.get("logo", "")
            streams = channel.get("streams", [])

            for stream in streams:

                stream_name = stream.get("name", channel_name)
                link = stream.get("link", "").strip()

                drm_key = stream.get("drm_key", "").strip()
                drm_scheme = stream.get("drm_scheme", "").strip()

                if not link:
                    continue

                m3u.write(
                    f'#EXTINF:-1 tvg-id="{channel_name}" '
                    f'tvg-name="{stream_name}" '
                    f'tvg-logo="{logo}" '
                    f'group-title="Sports",{stream_name}\n'
                )

                write_kodi_props(
                    m3u,
                    link,
                    drm_scheme,
                    drm_key
                )

                m3u.write(link + "\n")

                log.write(
                    f"CHANNEL : {stream_name}\n"
                    f"URL     : {link}\n"
                    f"DRM     : {drm_scheme}\n"
                    f"KEY     : {drm_key}\n"
                    "----------------------------------------\n"
                )

                total += 1

                if drm_key:
                    drm_total += 1

    print(f"Streams : {total}")
    print(f"DRM     : {drm_total}")
    print(f"M3U     : {OUTPUT_M3U}")
    print(f"LOG     : {OUTPUT_LOG}")


if __name__ == "__main__":
    main()
