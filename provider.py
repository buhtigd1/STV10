for stream in streams:

    if not isinstance(stream, dict):
        continue

    # Skip stream if JSON contains: "url": "Ok"
    if str(stream.get("url", "")).strip().lower() == "ok":
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
