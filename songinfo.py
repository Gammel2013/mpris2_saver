from urllib import parse as parse_url
import requests

from utils import debug_print
from config import musicbrainzHeaders


class SongInfo(object):
    def __init__(
        self,
        trackId,
        artist,
        album,
        title,
        lengthMS,
        cover_url=None
    ):
        self.trackId = trackId
        self.artist = artist
        self.album = album
        self.title = title
        self.lengthMS = lengthMS

        if cover_url:
            self.cover_url = cover_url
        else:
            self._fetch_cover()

    def __eq__(self, other):
        if other is None:
            return False
        elif not isinstance(other, SongInfo):
            error_message = (
                "Can only compare SongInfo to SongInfo, not "
                f"{type(other)}"
            )
            raise NotImplementedError(error_message)

        same_trackId = self.trackId == other.trackId
        same_artist = self.artist == other.artist
        same_album = self.album == other.album
        same_title = self.title == other.title

        return same_trackId and same_artist and same_album and same_title

    def __neq__(self, other):
        return not (self == other)

    def _fetch_cover(self):
        # API URLs and query strings
        musicbrainzUrl = (
            "https://musicbrainz.org/"
            "ws/2/release/"
            "?fmt=json&query="
        )
        coverartarchiveUrl = "https://coverartarchive.org/release/"

        musicbrainzQuery = "artist:\"{}\" AND release:\"{}\""

        artist = self.artist
        album = self.album

        debug_print(f"Fetching cover art for \033[3m{artist} – {album}\033[0m")
        query = parse_url.quote(musicbrainzQuery.format(artist, album))

        idx = 0
        while True:
            # If we run out of releases, give up
            try:
                ret = requests.get(
                    musicbrainzUrl+query,
                    headers=musicbrainzHeaders
                ).json()
                release_id = ret["releases"][idx]['id']
            except IndexError:
                debug_print(
                    "No cover found for "
                    f"\033[3m{self.artist} – {self.album}\033[0m"
                )
                self.cover_url = None
                break
            except KeyError:
                print("MusicBrainz API returned error")

            cover_data = requests.get(coverartarchiveUrl+release_id)

            # If release has no covers, try the next one
            if cover_data.status_code == 404:
                debug_print("Cover not found, trying next release")
                idx += 1
                continue

            debug_print("Found cover")
            cover_json = cover_data.json()
            self.cover_url = cover_json["images"][0]["image"]
            break

    @staticmethod
    def fromPlayer(player):
        trackId = player.Metadata["mpris:trackid"]
        title = player.Metadata["xesam:title"]
        album = player.Metadata["xesam:album"]
        artist = player.Metadata["xesam:artist"][0]
        lengthMS = player.Metadata["mpris:length"]/1000

        return SongInfo(trackId, artist, album, title, lengthMS)
