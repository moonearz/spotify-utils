def get_playlist_by_name(sp, target_name):
    results = sp.current_user_playlists()

    while results:
        for p in results["items"]:
            if p["name"].lower() == target_name.lower():
                return p
        results = sp.next(results) if results["next"] else None

    return None
