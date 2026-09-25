#!/usr/bin/env python3

import json
from urllib.request import urlopen

JSON_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_5/live_events.json"

M3U_FILE = "stv10.m3u"
LOG_FILE = "stv10.log"


def normalize_drm_key(drm_key):
    if not drm_key:
        return ""

    if isinstance(drm_key, str):
        drm_key = drm_key.strip()

        # already in kid:key format
        if ":" in drm_key and not drm_key.startswith("{"):
            return drm_key

        # JSON string
        if drm_key.startswith("{"):
            try:
                obj = json.loads(drm_key)

                if "keys" in obj and len(obj["keys"]) > 0:
                    item = obj["keys"][0]

                    kid = item.get("kid", "")
                    key = item.get("k", "")

                    if kid and key:
                        return f"{kid}:{key}"

            except Exception:
                pass

    elif isinstance(drm_key, dict):

        if "keys" in drm_key and len(drm_key["keys"]) > 0:
            item = drm_key["keys"][0]

            kid = item.get("kid", "")
            key = item.get("k", "")

            if kid and key:
                return f"{kid}:{key}"

    return ""


def write_kodiprop(fp, url, drm_scheme, drm_key):

    drm_key = normalize_drm_key(drm_key)

    if not drm_key:
        return

    if (drm_scheme or "").lower() != "clearkey":
        return

    manifest_type = "mpd"

    if ".m3u8" in url.lower():
        manifest_type = "hls"

    fp.write("#KODIPROP:inputstream=inputstream.adaptive\n")
    fp.write(
        f"#KODIPROP:inputstream.adaptive.manifest_type={manifest_type}\n"
    )
    fp.write(
        "#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey\n"
    )
    fp.write(
        f"#KODIPROP:inputstream.adaptive.license_key={drm_key}\n"
    )


def load_channels():
    with urlopen(JSON_URL, timeout=60) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def main():

    channels = load_channels()

    total_streams = 0
    total_drm = 0

    with open(M3U_FILE, "w", encoding="utf-8") as m3u, \
         open(LOG_FILE, "w", encoding="utf-8") as log:

        m3u.write("#EXTM3U\n")

        for channel in channels:

            channel_id = str(
                channel.get("name", "unknown")
            )

            logo = channel.get("logo", "")

            streams = channel.get("streams", [])

            if not isinstance(streams, list):
                continue

            for stream in streams:

                if not isinstance(stream, dict):
                    continue

                stream_name = stream.get(
                    "name",
                    channel_id
                )

                url = stream.get(
                    "link",
                    ""
                ).strip()

                if not url:
                    continue

                drm_key = stream.get(
                    "drm_key",
                    ""
                )

                drm_scheme = stream.get(
                    "drm_scheme",
                    ""
                )

                drm_value = normalize_drm_key(
                    drm_key
                )

                m3u.write(
                    f'#EXTINF:-1 tvg-id="{channel_id}" '
                    f'tvg-name="{stream_name}" '
                    f'tvg-logo="{logo}" '
                    f'group-title="Sports",{stream_name}\n'
                )

                write_kodiprop(
                    m3u,
                    url,
                    drm_scheme,
                    drm_key
                )

                m3u.write(url + "\n")

                log.write(
                    f"CHANNEL={stream_name}\n"
                    f"URL={url}\n"
                    f"DRM_SCHEME={drm_scheme}\n"
                    f"DRM_KEY={drm_value}\n"
                    "----------------------------------------\n"
                )

                total_streams += 1

                if drm_value:
                    total_drm += 1

    print(f"Streams : {total_streams}")
    print(f"DRM     : {total_drm}")
    print(f"Saved   : {M3U_FILE}")
    print(f"Log     : {LOG_FILE}")


if __name__ == "__main__":
    main()
