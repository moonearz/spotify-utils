# Spotify Utilities

A (soon-to-be) collection of Python utilities for visualizing and managing Spotify data.

## Structure

The utilities are divided into analytics for your extended spotify streaming history and
functions for managing and creating new playlists (potentially based on your history).

## Features

### Playlist Filtering

Create a new playlist by filtering songs from an existing playlist.

Two filtering methods are available:

1. **Manual filtering:** Review each song individually and decide whether to keep it.
2. **History-based filtering:** Automatically filter songs based on their skip rates.

The original playlist is never modified.

### Spotify History Analytics

Look at interesting data about your listening habits. I'm still adding more of these.

Currently available:
1. Look at your most played artists and how much you've listened to them
2. Get a breakdown of artists you listen to by proportion
3. List your most skipped songs

### Configurable Settings

1. Start date (will also have end date soon)
2. Listening metric (either plays or time)
3. Page size (for viewing results)

## Prerequisites

Before installing, make sure you have:

- Python 3.13
- Git
- Make

Depending on which features you want to use you will also need:
- Spotify API credentials
- Your Spotify extended streaming history

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

### 3. Configure Spotify authentication (optional)

**Create a Spotify application**

1. Visit the Spotify Developer Dashboard
2. Create a new application
3. Copy your cliend id and client secret
4. Configure the redirect URI used by the application

Use these credentials to set up your `.env` file, using the example.

You may need to authenticate the first time you run the program.

### 4. Download your extended spotify history
1. Go to your privacy page https://www.spotify.com/us/account/privacy/
2. Click 'Download your data'
3. Select extended streaming history
4. Download and rename the folder to data in the root of this repository

### 5. Run the application

```bash
make run
```

## Usage

Coming soon