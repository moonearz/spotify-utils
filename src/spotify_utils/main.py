from spotify_utils.client import get_spotify_client
from spotify_utils.playlists import get_playlist_by_name


def main():
    sp = get_spotify_client()

    user = sp.current_user()
    print(f"Logged in as: {user['display_name']}")

    playlist = get_playlist_by_name(sp, "Misc")

    if playlist:
        print(f"Found playlist: {playlist['name']}")
    else:
        print("Playlist not found.")


if __name__ == "__main__":
    main()
