import argparse
import json
from ytmusicapi import YTMusic

class YoutubeMusicImporter:
    def __init__(self, yt_client, ignore_list):
        self.yt = yt_client
        self._importing_items = {
            'likes': self.import_likes,
            'playlists': self.import_playlists
        }
        for item in ignore_list:
            del self._importing_items[item]

    def import_likes(self, in_path: str):
        # playlistId = self.yt.create_playlist('likes with YM importer', 'This playlist was imported using youtube music importer')
        tracks = []
        with open(f'{in_path}/likes.json', 'r') as f:
            likes = json.load(f)
            for track in likes:
                tracks.append(self._dict_to_track(track))
        
        trackIds = self.search_song_ids_for(tracks)
        # self.yt.add_playlist_items(playlistId, [trackId])
        # Add your implementation here
        pass

    def import_playlists(self, in_path: str):
        # Add your implementation here
        pass
    
    def search_song_ids_for(self, trackList):
        track_ids = []
        for track in trackList:
            search_results = self.yt.search(f'{str.join(' & ', track.artists)} {track.track}')
            for result in search_results:
                if result['resultType'] == 'song':
                    track_ids.append(result['videoId'])
                    break
            break
        print(track_ids)
        return track_ids
    
    def import_all(self, in_path: str):
        for item in self._importing_items.values():
            item(in_path)

    def _dict_to_track(self, track_dict):
        return Track(track_dict['id'], track_dict['track'], track_dict['artists'], track_dict['duration_ms'])
    
    def _dict_to_album(self, album_dict):
        return Album(album_dict['id'], album_dict['title'], album_dict['artists'], album_dict['year'])
    
    def _dict_to_artist(self, artist_dict):
        return Artist(artist_dict['id'], artist_dict['name'])

class Track:
    def __init__(self, id, track, artists, duration_ms):
        self.id = id
        self.track = track
        self.artists = artists
        self.duration_ms = duration_ms

class Album:
    def __init__(self, id, title, artists, year):
        self.id = id
        self.title = title
        self.artists = artists
        self.year = year

class Artist:
    def __init__(self, id, name):
        self.id = id
        self.name = name

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import music data from Yandex Music account to YouTube Music library')
    parser.add_argument('-t', '--oauth', help='Oauth file for YT music. Run `ytmusicapi oauth` to get it.', required=True)

    parser.add_argument('-i', '--ignore', nargs='+', help='Don\'t import some items',
                        choices=['likes', 'playlists'], default=[])

    parser.add_argument('-if', '--import-folder', help='Folder with exported data', default='./out')

    arguments = parser.parse_args()

    importer = YoutubeMusicImporter(YTMusic(arguments.oauth), arguments.ignore)
    importer.import_all(arguments.import_folder)