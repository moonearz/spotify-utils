def normalize_track(track):
    title, artist = track
    return (
        title.strip().casefold(),
        artist.strip().casefold(),
    )


def format_playlist_track(entry):
    track = entry["item"]

    title = track["name"]
    artists = ", ".join(artist["name"] for artist in track["artists"])

    return f"{title} by {artists}"
