import mpris2

from pathlib import Path
from threading import Thread
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository.GLib import MainLoop
from pwcontroller import PWController
from time import time, sleep

from utils import debug_print, sanitize_name
from songinfo import SongInfo


DBusGMainLoop(set_as_default=True)


class Recorder:
    def __init__(self, **kw):
        self.ignoreSeeksTimer = kw.get("ignoreSeeksTimer", 1)

        self.mainloop = MainLoop()
        self.isRecording = False
        self.recordingStartTime = 0

        self.player = None
        self.controller = None

        if "songDirectory" in kw:
            self.songDirectory = Path(kw.get("songDirectory")).resolve()
        else:
            self.songDirectory = Path(__file__).resolve().parent / "songs"

    def initMPRIS(self, player_uri) -> mpris2.Player:
        def _onSeek(new_pos):
            ignore = time() - self.recordingStartTime < self.ignoreSeeksTimer
            ignore = ignore or not self.isRecording
            if ignore:
                return
            self.mainloop.quit()

        def _onPropertiesChanged(player, *args, **kw):
            if not self.isRecording:
                return
            dc = args[0]

            if "Metadata" in dc and "mpris:trackid" in dc["Metadata"]:
                self.mainloop.quit()

        print("Starting MPRIS2...")
        try:
            players = mpris2.get_players_uri()
            while True:
                next_uri = next(players)
                debug_print(f"Found player '{player_uri.split('.')[3]}'")
                if next_uri == player_uri:
                    dbus_info = {"dbus_uri": player_uri}
                    player = mpris2.Player(dbus_interface_info=dbus_info)

                    player.PropertiesChanged = _onPropertiesChanged
                    player.Seeked = _onSeek

                    self.player = player
                    return player
        except StopIteration:
            self.player = None
            return None

    def initPWController(self):
        # Initialize controller
        controller = PWController()

        self.controller = controller
        return controller

    def setPWTarget(self, target):
        if self.controller is None:
            raise ValueError("PipeWire controller not initialized.")

        self.controller.set_config(target=target)

    def getCurrentSong(self):
        if self.player is None:
            raise ValueError("Player not initialized.")

        return SongInfo.fromPlayer(self.player)

    def getTargets(self):
        if self.controller is None:
            raise ValueError("PipeWire controller not initialized.")

        return self.controller.getTargets()

    @staticmethod
    def getPlayers():
        return list(mpris2.get_players_uri())

    def setSongDirectory(self, path):
        self.songDirectory = Path(path).resolve()

    def recordCurrentSong(self):
        if self.controller is None:
            raise ValueError("PipeWire controller not initialized.")
        if self.player is None:
            raise ValueError("Player not initialized.")

        track = self.getCurrentSong()

        artist_directory = self.songDirectory / sanitize_name(track.artist)
        album_directory = artist_directory / sanitize_name(track.album)
        song_path = album_directory / sanitize_name(track.title)

        album_directory.mkdir(parents=True, exist_ok=True)

        player = self.player
        controller = self.controller

        while not player.PlaybackStatus == "Paused":
            if player.PlaybackStatus == "Stopped":
                raise ValueError("Player is stopped")
            player.Pause()

            sleep(0.5)

        while player.Position != 0:
            player.SetPosition(track.trackId, 0)
            sleep(0.5)

        sleep(0.5)

        # Length + 100ms as buffer
        length = track.lengthMS / 1000
        length += 0.1

        t = Thread(
            target=controller.record,
            args=[
                song_path.with_name(song_path.name + ".wav").absolute(),
                length
            ]
        )

        print("Recording...")

        self.isRecording = True
        self.recordingStartTime = time()

        t.start()
        player.Play()

        self.mainloop.run()

        player.Pause()

        self.isRecording = False
        self.recordingStartTime = 0

        print("Done recording.")
