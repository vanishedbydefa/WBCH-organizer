import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple

import requests as re

from model import Episode, Video
from model.episode_db import EpisodeDb
from hasher import HashDict
from logger import logger


def download_epdb(base_path: str | Path) -> Optional[Path]:
    if not isinstance(base_path, Path):
        base_path = Path(base_path)
    url = "https://raw.githubusercontent.com/vanishedbydefa/WBCH-decider/refs/heads/main/epdb_new.json"
    resp = re.get(url, timeout=10)
    if resp.status_code == 200:
        filename = base_path / os.path.basename(url)
        with open(filename, "wb") as f:
            f.write(resp.content)
        logger.info(f"epdb downloaded and saved to: {filename}")
        return filename
    else:
        logger.error(f"Failed to download epdb. Status code: {resp.status_code}")
        return None


def load_db(file_path: Path | str) -> Optional[EpisodeDb]:
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    if not file_path.is_file():
        logger.error(f"Path is not a file: {file_path}")

    try:
        with open(file_path, 'r') as f:
            epdb_dict = json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Error while decoding json db: {file_path}")
        return None

    epdb = EpisodeDb()
    epdb.from_dict(epdb_dict)
    return epdb


def process_episode(episode: Episode | Video, season: int, episode_type: str, hash_to_file_dict: Dict[str, str],
                    root_folder: Path) -> Tuple[int, int, List[str]]:
    if not episode or not episode.versions:
        return 0, 0, []

    # Determine episode number format
    if episode_type == 'finale':
        episode_number = 'SF'
    elif episode_type == 'msf':
        episode_number = 'MSF'
    else:
        episode_number = episode.number
        if episode_number.isdigit():
            episode_number = f"{int(episode_number):02d}"

    episode_string = f"S{season:02d}E{episode_number} - {episode.name}"
    output_lines = []
    found_count = 0
    total_count = len(episode.versions)

    if not episode.versions:
        output_lines.append(f"  ⚠️  '{episode_string}' - No hash available")
        return 0, 0, output_lines

    output_lines.append(f"  📺 '{episode_string}'")
    for version in episode.versions:
        episode_hash = version.hashes.get("hash")
        tag_string = " ".join(version.tags) or "Normal"

        if episode_hash in hash_to_file_dict:
            found_count += 1
            episode_file = hash_to_file_dict[episode_hash]
            episode_file = Path(episode_file).relative_to(root_folder)
            output_lines.append(f"\t\t✅ Version '{tag_string}' - Found at '{episode_file}'")
        else:
            output_lines.append(f"\t\t❌ Version '{tag_string}' - Missing")

    return found_count, total_count, output_lines


def report(db: EpisodeDb, hashes: HashDict, root_folder: Path):
    # Create a dictionary for quick lookup of available files (hash → file path)
    hash_to_file_dict: Dict[str, str] = {hashes.get_hash(file, "hash"): file for file in
                                         hashes.get_file_names_in_dict()}
    total_episodes = 0
    found_episodes = 0

    print("\n📢  WBCH Collection Report  📢\n")

    for season_data in db.seasons:
        season = season_data.number
        season_found = 0
        season_total = 0

        print(f"🎬 Season {season}\n" + "-" * 40)

        # Process regular episodes
        for episode in season_data.episodes:
            found, total, lines = process_episode(
                episode, season, 'regular', hash_to_file_dict, root_folder
            )
            season_found += found
            season_total += total
            print("\n".join(lines))

        # Process season finale
        found, total, lines = process_episode(
            season_data.finale, season, 'finale', hash_to_file_dict, root_folder
        )
        season_found += found
        season_total += total
        print("\n".join(lines))

        # Process mid-season finale
        found, total, lines = process_episode(
            season_data.mid_season_finale, season, 'msf', hash_to_file_dict, root_folder
        )
        season_found += found
        season_total += total
        print("\n".join(lines))

        print(f"📊 Season {season}: Found {season_found}/{season_total} episodes\n")

        total_episodes += season_total
        found_episodes += season_found

    print("📋 Final Report")
    print(f"📀 Total Episodes Found: {found_episodes}/{total_episodes}")
    print(
        f"✅ Completion: {found_episodes / total_episodes:.2%}\n" if total_episodes > 0 else "⚠️ No episodes in database.")
