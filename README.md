# yandex2spotify

A simple Python script that allows to import favorite tracks, playlists, albums, and artists from Yandex.Music to Spotify

## Installation

Requires Python 3.8 or higher.

```bash
pip3 install -r requirements.txt
```

## Usage

1) Obtain a Yandex.Music OAuth token.[^1]

2) If you don't want to import some items (likes, playlists, albums, artists) you can exclude them by specifying the `-i/--ignore` argument, for example:
```bash
python3 exporter.py --id <spotify_client_id> --secret <spotify_client_secret> -u <spotify_username> -t <yandex_token> -i playlists albums artists
```

1) After launch, script will store all information inside out directory

2) If authorization succeed - you will see log of import process.

JSON import is also available. Use `--json-path` or `-j` to specify path to JSON file in format described below.
```
[
	{
		"artist": "Artist Name",
		"track": "Track Name"
	},
	{
		"artist": "Artist Name",
		"track": "Track Name"
	},
	...
]
```

[^1]: Since it's impossible to register an OAuth application with Yandex.Music access scope, you have to [reuse the token from music.yandex.ru itself](https://github.com/MarshalX/yandex-music-api/discussions/513).
