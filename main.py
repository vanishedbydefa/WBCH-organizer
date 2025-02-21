import sys
import signal
import argparse
import multiprocessing
from pathlib import Path
from typing import Optional, List

from file_management import find_files
from hasher import Hasher, HashDict, hash_file, phash_file
from logger import logger
from epdb import download_epdb, load_db, report

# Fix multiprocessing issues in PyInstaller
multiprocessing.set_start_method("spawn", force=True)

hash_dict: Optional[HashDict] = None

def main(base_path: str | Path):
    global hash_dict
    if not isinstance(base_path, Path):
        base_path = Path(base_path)

    print("Run this Program in a terminal with emojie support")

    # epdb_path = download_epdb(base_path)
    db = load_db("epdb.json")
    files: List[Path] = find_files(base_path)
    hash_dict = HashDict(base_path/"wbch_index.json")
    hash_dict.load_dict_from_file()

    # hash_dict.clear_hash_type("phash")
    hash_dict.clean_removed_files()

    hash_types = {
        "hash": hash_file,
        "phash": phash_file
    }
    for hash_type, hash_func in hash_types.items():
        hasher = Hasher(hash_func, hash_type, hash_dict, files, num_workers=4)
        hasher.hash_files()
    hash_dict.persist_dict_to_file()

    report(db, hash_dict, base_path)

    if hasattr(sys, '_MEIPASS') or ".exe" in sys.argv[0]:
        input("Press Enter to exit...")


def signal_handler(sig, frame):
    logger.info('Program interrupted, stopping...')
    if hash_dict:
        hash_dict.persist_dict_to_file()
    sys.exit(0)


if __name__ == "__main__":
    multiprocessing.freeze_support()  # Fix PyInstaller multiprocessing bug
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="WBCH-Organizer to organize and rename your WBCH collection")
    parser.add_argument("-p", "--base_path", type=str, default="./", help="Path to your WBCH collection")
    args = parser.parse_args()
    main(args.base_path)
