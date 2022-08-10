from vimania_uri.environment import ROOT_DIR
from vimania_uri.rifle.rifle import Rifle


def get_mime_type(uri: str) -> str:
    # mimetypes.init()
    # return mimetypes.guess_type(p)

    # rifle has more hits
    rifle = Rifle(
        f"{ROOT_DIR}/rifle/rifle.conf"
    )  # GOTCHA: must be initialized for every call, otherwise same result
    rifle.reload_config()
    return rifle.get_mimetype(uri)


def is_text(uri: str) -> bool:
    return get_mime_type(uri).startswith("text")
