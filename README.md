# yandex music to json

A simple Python script that allows to expoty favorite tracks, playlists, albums, and artists from Yandex.Music to json.

This data can be imported to Youtube Music. If you want to import data from Yandex.Music to Spotify use original repo.

## Installation

Requires Python 3.8 or higher.

```bash
pip3 install -r requirements.txt
```

## Usage

## Export from Yandex Music
1) Obtain a Yandex.Music OAuth token.[^1]

2) If you don't want to import some items (likes, playlists, albums, artists) you can exclude them by specifying the `-i/--ignore` argument, for example:
```bash
python3 exporter.py -t <yandex_token> -i playlists albums artists
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
## Import to Youtube Music
1) Get YT music OAuth file -> `ytmusicapi oauth`
2) Import available only for likes and playlists. You can exclude them by specifying the `-i/--ignore` argument, for example:
```bash
python3 youtube_music_importer.py  -t <path to oauth.json> -i playlists -if <path to exported data>
```
3) To ensure proper functionality, you must save the exported file structure. All json files inside playlist folder will be considered as playlist for import

[^1]: Since it's impossible to register an OAuth application with Yandex.Music access scope, you have to [reuse the token from music.yandex.ru itself](https://github.com/MarshalX/yandex-music-api/discussions/513).
