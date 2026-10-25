import questionary


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
