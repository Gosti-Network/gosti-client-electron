
INSTALL_PATH = './UserData/InstalledGames/'
TORRENTS_PATH = './UserData/Torrents/'
TORRENT_DATA_PATH = './UserData/TorrentData/'

UI_UPDATE_FREQUENCY = 1

COLOR_BG_MAIN = .1, .1, .1, 1
COLOR_BG_LIGHT = .2, .2, .2, 1
COLOR_BG_DARK = .05, .05, .05, 1

COLOR_THEME_MAIN = .2, .5, .2, 1
COLOR_THEME_LIGHT = .2, .7, .2, 1
COLOR_THEME_DARK = .2, .3, .2, 1

COLOR_VERSION = .2, .2, .2, 1
COLOR_DEV_STATUS_COMPLETE = .2, .2, .2, .8
COLOR_DEV_STATUS_IN_DEVELOPEMENT = .2, .2, .2, .8
COLOR_DEV_STATUS_COMING_SOON = .2, .2, .2, .8
COLOR_PRICE = .1, .1, .1, 1

def get_status_color(status):
    if status == "Coming Soon":
        return COLOR_DEV_STATUS_COMING_SOON
    elif status == "In Development":
        return COLOR_DEV_STATUS_IN_DEVELOPEMENT
    elif status == "Complete":
        return COLOR_DEV_STATUS_COMPLETE
