import json
import os
import argparse
import logging
from base64 import b64encode
from time import sleep

from yandex_music import Client, Artist

REDIRECT_URI = 'https://open.spotify.com'
MAX_REQUEST_RETRIES = 5

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class Exporter:
    def __init__(self, yandex_client: Client, ignore_list,):
        self.yandex_client = yandex_client

        self._exporting_items = {
            'likes': self.export_likes,
            'playlists': self.export_playlists,
            'albums': self.export_albums,
            'artists': self.export_artists
        }

        for item in ignore_list:
            del self._exporting_items[item]

        self.not_exported = {}

    def _save_json(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f)
    
    def _track_to_dict(self, track):
        return {
            'id': track.id,
            'track': track.title,
            'artists': [artist.name for artist in track.artists],
            'duration_ms': track.duration_ms
        }
    
    def _album_to_dict(self, album):
        return {
            'id': album.id,
            'title': album.title,
            'artists': [artist.name for artist in album.artists],
            'year': album.year
        }
    
    def _artist_to_dict(self, artist):
        return {
            'id': artist.id,
            'name': artist.name
        }
        

    def export_likes(self, out_path: str):
        self.not_exported['Likes'] = []
        likes_tracks_response = self.yandex_client.users_likes_tracks()
        if likes_tracks_response is not None:
            likes_tracks = likes_tracks_response.tracks
            tracks = self.yandex_client.tracks([f'{track.id}:{track.album_id}' for track in likes_tracks if track.album_id])
            logger.info('Importing liked tracks...')

            self._save_json([self._track_to_dict(t) for t in tracks], f'{out_path}/likes.json')

    def export_playlists(self, out_path: str):
        playlists = self.yandex_client.users_playlists_list()
        
        os.mkdir(f'{out_path}/playlists')
        for playlist in playlists:
            logger.info(f'Exporting playlist {playlist.title}...')

            self.not_exported[playlist.title] = []

            playlist_tracks = playlist.fetch_tracks()
            if not playlist.collective:
                tracks = [track.track for track in playlist_tracks]
            elif playlist.collective and playlist_tracks:
                tracks = self.yandex_client.tracks([track.track_id for track in playlist_tracks if track.album_id])
            else:
                tracks = []


            self._save_json([self._track_to_dict(t) for t in tracks], f'{out_path}/playlists/{playlist.title}.json')

    def export_albums(self, out_path: str):
        self.not_exported['Albums'] = []

        likes_albums = self.yandex_client.users_likes_albums()
        albums = [album.album for album in likes_albums]
        logger.info('Importing albums...')

        self._save_json([self._album_to_dict(a) for a in albums], f'{out_path}/albums.json')

    def export_artists(self, out_path: str):
        self.not_exported['Artists'] = []

        likes_artists = self.yandex_client.users_likes_artists()
        artists = [artist.artist for artist in likes_artists]
        logger.info('Exporting artists...')

        self._save_json([self._artist_to_dict(a) for a in artists], f'{out_path}/artists.json')

    def export_all(self, out_path: str):
        for item in self._exporting_items.values():
            item(out_path)

        self.print_not_exported()

    def print_not_exported(self):
        logger.error('Not imported items:')
        for section, items in self.not_exported.items():
            logger.info(f'{section}:')
            for item in items:
                logger.info(item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export music data from Yandex Music account to JSON files')

    parser.add_argument('-t', '--token', help='Token from music.yandex.com account')

    parser.add_argument('-i', '--ignore', nargs='+', help='Don\'t import some items',
                        choices=['likes', 'playlists', 'albums', 'artists'], default=[])

    parser.add_argument('-o', '--out-path', help='Folder to save the playlist data', default='./out')

    arguments = parser.parse_args()

    try:
        yandex_client_ = None

        if arguments.token:
            yandex_client_ = Client(arguments.token)
            yandex_client_.init()

        if yandex_client_ is None:
            logger.error('Yandex Music token is required')
            exit(1)

        exporter = Exporter(yandex_client_, arguments.ignore)

        exporter.export_all(arguments.out_path)
    except Exception as e:
        logger.error(f'An unexpected error occurred: {str(e)}')
