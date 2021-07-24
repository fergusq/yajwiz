from typing import Dict, List, NamedTuple, Optional, Set, Tuple, Union
import appdirs
import bz2
import json
from pathlib import Path
import requests
import logging
import sys
import unicodedata

logger = logging.Logger("yajwiz")

DATA_DIR = Path(appdirs.user_data_dir("yajwiz"))
DICTIONARY_PATH = DATA_DIR / "dictionary.json"

KAWHAQ_URL = "https://de7vid.github.io/qawHaq/"
FORMAT = "iOS-1"

def _parse_boqwiz_pos(pos: str) -> Tuple[str, Set[str]]:
    colon = pos.split(":")
    if len(colon) == 1:
        return colon[0], set(colon)
    
    [tpos, tags] = colon
    comma = tags.split(",")
    return tpos, set([tpos]+comma)

class BoqwizEntry(NamedTuple):
    """
    Represents an entry in the boQwI' dictionary, describing a single headword.
    """

    id: str
    name: str
    part_of_speech: str
    simple_pos: str
    tags: Set[str]
    definition: Dict[str, str]
    notes: Dict[str, str]
    examples: Dict[str, str]
    search_tags: Dict[str, List[str]]
    hidden_notes: Optional[str]
    synonyms: Optional[str]
    antonyms: Optional[str]
    see_also: Optional[str]
    components: Optional[str]
    source: Optional[str]

    @staticmethod
    def from_json(id: str, data: dict) -> "BoqwizEntry":
        tpos, tags = _parse_boqwiz_pos(data["part_of_speech"])
        return BoqwizEntry(
            id=id,
            name=data["entry_name"],
            part_of_speech=data["part_of_speech"],
            simple_pos=tpos,
            tags=tags,
            definition=data["definition"],
            notes=data.get("notes", {}),
            examples=data.get("examples", {}),
            search_tags=data.get("search_tags", {}),
            hidden_notes=data.get("hidden_notes", None),
            synonyms=data.get("synonyms", None),
            antonyms=data.get("antonyms", None),
            see_also=data.get("see_also", None),
            components=data.get("components", None),
            source=data.get("source", None)
        )

class BoqwizDictionary(NamedTuple):
    """
    Represents the whole boQwI' dictionary.
    """

    version: str
    locales: Dict[str, str]
    supported_locales: List[str]
    entries: Dict[str, BoqwizEntry]

    @staticmethod
    def from_json(data: dict) -> "BoqwizDictionary":
        return BoqwizDictionary(
            version=data["version"],
            locales=data["locales"],
            supported_locales=data["supported_locales"],
            entries={
                key: BoqwizEntry.from_json(key, value)
                for key, value in data["qawHaq"].items()
            }
        )
    
    def __repr__(self):
        return f"<BoqwizDictionary version={self.version}>"

def _normalize(data: Union[str, int, float, dict, list]) -> Union[str, int, float, dict, list]:
    if isinstance(data, str):
        return unicodedata.normalize("NFC", data)
    
    elif isinstance(data, dict):
        return {
            _normalize(key): _normalize(value)
            for key, value in data.items()
        }
    
    elif isinstance(data, list):
        return [_normalize(item) for item in data]
    
    else:
        return data

def _try_load() -> Optional[dict]:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if DICTIONARY_PATH.exists():
            with open(DICTIONARY_PATH, "r") as f:
                data = f.read()
                data = json.loads(data)
                data = _normalize(data)
            
            return data
        
        else:
            return None
    
    except:
        logger.error("Error while reading the dictionary!", exc_info=sys.exc_info())
        return None

cached_dictionary: Optional[BoqwizDictionary] = None

def load_dictionary() -> BoqwizDictionary:
    """
    Loads the currently installed version of the boQwI' dictionary.
    """

    global cached_dictionary
    if cached_dictionary:
        return cached_dictionary

    data = _try_load()
    if data:
        cached_dictionary = BoqwizDictionary.from_json(data)
        return cached_dictionary
    
    else:
        update_dictionary()
        return load_dictionary()

def update_dictionary():
    """
    Checks if there are available updates to the boQwI' dictionary and installs them.
    """

    global cached_dictionary

    # download the manifest and the latest version
    logger.info("Updating boQwI'...")
    try:
        manifest = requests.get(KAWHAQ_URL + "manifest.json").json()
        latest = manifest[FORMAT]["latest"]
    except:
        logger.error("Error while fetching the qawHaq manifest!", exc_info=sys.exc_info())
        return

    # check for existing versions of the dictionary

    if cached_dictionary and cached_dictionary.version == latest:
        logger.info(f"No update required.")
        return

    data = _try_load()
    if data and data["version"] == latest:
        logger.info(f"No update required.")
        return
    
    # install the update
    try:
        logger.info(f"Downloading boQwI' version {latest}...")
        url = KAWHAQ_URL + manifest[FORMAT][latest]["path"]
        archive = requests.get(url).content
        data = bz2.decompress(archive).decode("utf-8")

        with open(DICTIONARY_PATH, "w") as f:
            f.write(data)

        logger.info(f"Updated boQwI' to version {latest}.")
    
    except:
        logger.error("Error while updating the dictionary!", exc_info=sys.exc_info())
        return