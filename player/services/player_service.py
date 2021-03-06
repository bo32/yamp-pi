import vlc
import os

from player.global_properties import global_properties
from pathlib import Path

VOLUME_STEP = 5
VOLUME_MAX = 100
VOLUME_MIN = 0

META_DICTIONARY = {
    'title': 0,
    'artist_name': 1,
    'genre': 2,
    'album': 4,
    'date': 8
}

class PlayerService(object):

    _instance = None

    # https://python-patterns.guide/gang-of-four/singleton/#a-more-pythonic-implementation
    def __new__(cls):
        if cls._instance is None:
            print('Initializing Player Service...')
            cls._instance = super(PlayerService, cls).__new__(cls)
            # FIXME I guess some errors are triggered from here is VLC is not installed on the machine. Errors to be caught
            cls._instance.instance = vlc.Instance('--loop')
            cls._instance.list_player = cls._instance.instance.media_list_player_new()
            cls._instance.played_album = None
            cls._instance.played_stream = None
            print('Player Service initialized...')
        return cls._instance

    def get_media_player(self):
        return self.list_player.get_media_player()

    def get_current_track(self):
        if self.played_album is not None:
            current_track = self.get_media_player().get_media()
            current_track.parse()
            result = {}
            for key in META_DICTIONARY.keys():
                result[key] = current_track.get_meta(META_DICTIONARY[key])
            return result
        if self.played_stream is not None:
            return {'title': 'url'} # TODO set to the played URL

        return {'title': 'nothing'}

    def change_sound(self, direction):
        current_volume = self.get_current_volume()
        if direction == 'up':
            new_volume = VOLUME_MAX if current_volume > VOLUME_MAX - VOLUME_STEP else current_volume + VOLUME_STEP
        elif direction == 'down':
            new_volume = VOLUME_MIN if current_volume < VOLUME_STEP else current_volume - VOLUME_STEP
        else:
            raise Exception('wrong volume direction')
        print('setting sound to ' + str(new_volume))
        self.get_media_player().audio_set_volume(new_volume)

    def sound_up(self):
        print('sound up')
        self.change_sound('up')
        return {
            "is_sound_max" : self.get_current_volume() == VOLUME_MAX,
            "is_sound_min" : self.get_current_volume() == VOLUME_MIN }

    def sound_down(self):
        print('sound down')
        self.change_sound('down')
        return {
            "is_sound_max" : self.get_current_volume() == VOLUME_MAX,
            "is_sound_min" : self.get_current_volume() == VOLUME_MIN }

    def get_current_volume(self):
        return self.get_media_player().audio_get_volume()

    def toggle_mute(self):
        print('mute')
        self.get_media_player().audio_toggle_mute()
        return self.get_media_player().audio_get_mute()

    def pause(self):
        self.list_player.pause()

    def next(self):
        self.list_player.next()

    def previous(self):
        self.list_player.previous()

    def get_library_folder(self):
        return Path(global_properties['server']['library_path'])

    def play_index(self, index):
        library_folder_albums = [x for x in sorted(self.get_library_folder().iterdir()) if x.is_dir()]
        self.__play_folder(library_folder_albums[index])

    def __play_folder(self, folder):
        print('playing album ' + str(folder))

        self.played_album = self.instance.media_list_new()
        self.add_folder_to_playlist(folder)

        self.list_player.stop() # clear current playlist
        self.list_player.set_media_list(self.played_album)
        self.list_player.play()
        print('Playing music...')

    def play(self, directory):
        library_folder = self.get_library_folder()
        dir_to_play = library_folder.joinpath(directory)
        self.__play_folder(dir_to_play)

    def add_folder_to_playlist(self, folder):
        for file in sorted(folder.iterdir()):
            if self.is_directory(file):
                # Recursive call if we have another folder
                print('Adding files from folder ' + file.name)
                self.add_folder_to_playlist(file)
            elif self.is_audio_file(file):
                print('Adding song ' + file.name)
                media = self.instance.media_new(str(file))
                self.played_album.add_media(media)
            else:
                print('Skipping non-audio file ' + file.name)
                pass

    def is_audio_file(self, file_path):
        # TODO check mime type https://github.com/ahupp/python-magic
        return file_path.suffix.upper() in ['.MP3', '.FLAC', '.OGG', '.WAV', '.WMA', '.AAC', '.ALAC']

    def is_directory(self, file_path):
        return file_path.is_dir()

    def play_url(self, url):
        self.list_player.stop() # TODO need to find a better way to stop player and clean current media / media list
        self.played_stream = self.instance.media_new(url)
        self.get_media_player().set_media(self.played_stream)
        self.get_media_player().play()
        print('Playing URL...')
