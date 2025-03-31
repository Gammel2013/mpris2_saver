# Whether to print debug messages
debug = False

# Header for fetching album cover art
musicbrainzHeaders = {
    "User-Agent": "MPRIS2_SAVER/0.0.1"
}

recorderConfig = {
    "ignoreSeeksTimer": 1,
    # "songDirectory": "/tmp/"
}

# Refresh rate of script, can be used to reduce performance hit
rateInterval = 2.5

# Target mpris player to use
playerTarget = "org.mpris.MediaPlayer2.spotify"
# Target pipewire node to record
pwTarget = "spotify"
