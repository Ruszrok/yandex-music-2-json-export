import argparse
import json
import os
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
        self._import_from_file(f'{in_path}/likes.json', 'YM Importer: likes')

    def import_playlists(self, in_path: str):
        #get all playlists from playlist folder and import them
        for playlist in os.listdir(f'{in_path}/playlists'):
            if playlist.endswith('.json'):
                self._import_from_file(f'{in_path}/playlists/{playlist}', f'YM Importer: {playlist[:-5]}') #cut .json from playlist name

    
    def _import_from_file(self, filename, playlist_name):
        playlistId = self.yt.create_playlist(playlist_name, 'This playlist was imported using youtube music importer')
        print(f'Created playlist {playlist_name} with id {playlistId}')
        tracks = []
        with open(filename, 'r') as f:
            tracks_file = json.load(f)
            for track in tracks_file:
                tracks.append(self._dict_to_track(track))
        
        print('here')

        total_tracks = len(tracks)
        print(f'Importing {total_tracks} tracks')
        batchSize = 10
        for i in range(0, len(tracks), batchSize):
            batch = tracks[i:i+batchSize]
            batchIds = self.search_song_ids_for(batch)
            self.yt.add_playlist_items(playlistId, batchIds)
            print('Progress ', i + len(batchIds), f' of {total_tracks} tracks to playlist - {playlist_name}')
        print(f'Finished importing {total_tracks} liked tracks to playlist {playlist_name}')

    def search_song_ids_for(self, trackList):
        track_ids = []
        for track in trackList:
            search_results = self.yt.search(f'{str.join(' & ', track.artists)} {track.track}')
            for result in search_results:
                if result['resultType'] == 'song':
                    track_ids.append(result['videoId'])
                    break
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