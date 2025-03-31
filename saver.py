#!/bin/env python3

import dbus

from time import sleep
from json import dumps

from recorder import Recorder
from config import pwTarget, playerTarget, recorderConfig


if __name__ == "__main__":

    print("Starting MPRIS2_SPOTIFY_SAVER...")

    recorder = None
    currentTrack = None

    while True:
        try:
            # Initialize recorder
            if not recorder:
                recorder = Recorder(**recorderConfig)
                continue

            # Check PWController
            if not recorder.controller:
                recorder.initPWController()

                if pwTarget == "MANUAL":
                    print("Valid targets for recording:")
                    print(
                        dumps(
                            recorder.getTargets(),
                            sort_keys=True,
                            indent=4
                        )
                    )
                    choice = input("Pick a target (name or serialnum): ")
                    recorder.setPWTarget(choice)
                else:
                    recorder.setPWTarget(pwTarget)
                continue

            # Check MPRIS connection
            if not recorder.player:
                if playerTarget == "MANUAL":
                    players = {
                        str(num): player
                        for num, player in enumerate(
                            recorder.getPlayers()
                        )
                    }
                    print("Valid players:")
                    print(
                        dumps(
                            {
                                num: str(player)
                                for num, player in players.items()
                            }
                        )
                    )
                    choice = input("Pick a player (index): ")
                    recorder.initMPRIS(players[choice])
                else:
                    for player in recorder.getPlayers():
                        if str(player) == playerTarget:
                            recorder.initMPRIS(player)
                            break
                    else:
                        raise ValueError(f"Player '{playerTarget}' not found.")
                continue

            currentTrack = recorder.getCurrentSong()

            query = input(
                "Currently listening to "
                f"{currentTrack.title} by {currentTrack.artist}. "
                "Do you want to record this song? y/n\n"
            )

            if query.lower() == "y":
                recorder.recordCurrentSong()
            else:
                print("Trying again in a few seconds...")

        except dbus.exceptions.DBusException:
            print("Lost connection to music player")
            recorder.player = None

        sleep(2)
