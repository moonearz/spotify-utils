# Spotify Utilities

A (soon-to-be) collection of Python utilities for managing Spotify things through the API.

## Features

### Playlist Filtering

Create a new playlist by selecting which songs to keep from an existing playlist.

1. Select a playlist from your Spotify library
2. Enter a name for the new playlist
3. Review each song and choose whether to keep it
4. Create a new playlist containing only the selected songs

The original playlist is not modified.

## Prerequisites

Before installing, make sure you have:

- Python 3.13
- Git
- Make
- Spotify API credentials

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/moonearz/spotify-utils.git
cd spotify-utils
```

### 2. Install dependencies

```bash
make setup
```

This creates a Python virtual environment at:

```text
~/.venvs/spotify-utils
```

It also installs the application and its required dependencies.

### 3. Configure Spotify authentication

**Create a Spotify application**

1. Visit the Spotify Developer Dashboard
2. Create a new application
3. Copy your cliend id and client secret
4. Configure the redirect URI used by the application

Use these credentials to setup your `.env` file, using the example.

You may need to authenticate the first time your run the program.

### 4. Run the application

```bash
make run
```