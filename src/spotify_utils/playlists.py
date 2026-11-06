import questionary

from spotify_utils.utils import normalize_track


def get_playlist_by_name(sp, target_name):
    results = sp.current_user_playlists()

    while results:
        for p in results["items"]:
            if p["name"].lower() == target_name.lower():
                return p
        results = sp.next(results) if results["next"] else None

    return None


def get_user_playlists(sp):
    playlists = []
    results = sp.current_user_playlists()

    while results:
        playlists.extend(results["items"])
        results = sp.next(results) if results["next"] else None

    return playlists


def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_items(playlist_id)

    while True:
        tracks.extend(results["items"])

        if not results["next"]:
            break

        results = sp.next(results)

    return tracks


def create_new_playlist(sp, new_name, songs):
    playlist = sp.current_user_playlist_create(
        name=new_name,
        public=False,
    )

    playlist_id = playlist["id"]

    # limited to 100 adds per api call
    for i in range(0, len(songs), 100):
        sp.playlist_add_items(playlist_id, songs[i : i + 100])

    return playlist


def filter_songs(sp, playlist_id):
    results = sp.playlist_items(playlist_id)
    kept_songs = []
    while results:
        for entry in results["items"]:
            track = entry["item"]

            if track and track["type"] == "track":
                name = track["name"]
                artists = ", ".join(artist["name"] for artist in track["artists"])

                answer = questionary.confirm(
                    f"Keep '{name}' by {artists}?",
                    default=True,
                ).ask()

                if answer is None:
                    return None

                if answer:
                    kept_songs.append(track["uri"])

        if results["next"]:
            results = sp.next(results)
        else:
            break

    return kept_songs


def filter_playlist_by_skip_rate(
    tracks,
    skip_stats,
    threshold,
    min_plays,
):
    kept = []
    removed = []

    for item in tracks:
        track = item.get("item")

        if not track or not track.get("artists") or track.get("type") != "track":
            continue

        normalized_track = normalize_track(
            (
                track["name"],
                track["artists"][0]["name"],
            )
        )

        stats = skip_stats.get(normalized_track)

        if (
            stats is not None
            and stats["plays"] >= min_plays
            and stats["skip_rate"] < threshold
        ):
            kept.append(item)
        else:
            removed.append(item)

    return kept, removed
