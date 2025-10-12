import os
import sys
import signal
import hashlib
import argparse
import concurrent.futures
import multiprocessing

from logger import logger
from epdb import download_epdb, load_db, find_episode_by_hash, report
from messagebox import ask_rename

# Fix multiprocessing issues in PyInstaller
multiprocessing.set_start_method("spawn", force=True)

wbch_files = []

def hash_file(file_path):
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(1 * 10 ** 6), b""):
                sha256_hash.update(chunk)
        return file_path, sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing file: {file_path}, Error: {e}")
        return file_path, None

def index_files(base_path: os.PathLike):
    logger.info(f"Indexing WBCH files in: {base_path}")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(base_path):
            for name in files:
                file_path = os.path.join(root, name)
                futures.append(executor.submit(hash_file, file_path))

        for future in concurrent.futures.as_completed(futures):
            file_path, file_hash = future.result()
            if file_hash:
                wbch_files.append([file_path, file_hash])
                logger.debug(f"Indexed file: {file_path} with hash: {file_hash}")

    logger.info("Indexing done")

def rename_files(db):
    episode_cache = {}

    for file in wbch_files:
        file_hash = file[1]
        if file_hash in episode_cache:
            episode = episode_cache[file_hash]
        else:
            episode = find_episode_by_hash(db, file_hash)
            episode_cache[file_hash] = episode

        if episode is None:
            continue

        new_name = f"{episode.get('name')}.mp4".replace("?", "")
        old_file_path = file[0]
        new_file_path = os.path.join(os.path.dirname(old_file_path), new_name)

        try:
            os.rename(old_file_path, new_file_path)
            logger.debug(f"Renamed {old_file_path} to {new_file_path}")
        except Exception as e:
            logger.error(f"Error renaming file: {old_file_path} to {new_file_path}, Error: {e}")

def main(base_path: os.PathLike):
    print("Run this Program in a terminal with emojie support")
    rename = ask_rename()
    epdb_path = download_epdb(base_path)
    db = load_db(epdb_path)

    index_files(base_path)
    if rename:
        rename_files(db)
    report(db, wbch_files)

    if hasattr(sys, '_MEIPASS') or ".exe" in sys.argv[0]:
        input("Press Enter to exit...")

def signal_handler(sig, frame):
    logger.info('Program interrupted, stopping...')
    sys.exit(0)

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Fix PyInstaller multiprocessing bug
    signal.signal(signal.SIGINT, signal_handler)

    if hasattr(sys, '_MEIPASS') or ".exe" in sys.argv[0]:
        base_path = input("Enter the path to your WBCH collection: ")
    else:
        parser = argparse.ArgumentParser(description="WBCH-Organizer to organize and rename your WBCH collection")
        parser.add_argument("-p", "--base_path", type=str, required=True, default="./", help="Path to your WBCH collection")
        args = parser.parse_args()
        base_path = args.base_path
    
    if not os.path.exists(base_path):
        logger.error(f"Provided path does not exist: {base_path}")
        sys.exit(1)
    main(base_path)
