from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set

from hasher import HashDict


def calculate_phash_distance(phash_1: str, phash_2: str) -> float:
    if phash_1 is None or phash_2 is None:
        return 0.0

    iphash_1 = int(phash_1, base=16)
    iphash_2 = int(phash_2, base=16)

    xor_result = iphash_1 ^ iphash_2
    distance = bin(xor_result).count('1')

    return distance


def find_duplicates_by_phash(hash_dict: HashDict, distance: int) -> Dict[str, List[str]]:
    phash_dict: Dict[str, str] = hash_dict.get_hash_type_dict("phash")
    duplicates: Dict[str, List[str]] = defaultdict(list)
    found_duplicates_indices: Set[int] = set()
    files: List[str] = list(phash_dict.keys())

    for file_idx in range(len(files)):
        if file_idx in found_duplicates_indices:
            continue

        file_path: str = files[file_idx]
        duplicates[file_path].append(file_path)
        hash_value = phash_dict[files[file_idx]]
        for other_file_idx in range(file_idx, len(files)):
            if file_idx == other_file_idx or other_file_idx in found_duplicates_indices:
                continue

            other_hash_value = phash_dict[files[other_file_idx]]
            if not calculate_phash_distance(hash_value, other_hash_value) < distance:
                continue

            other_file_path: str = files[other_file_idx]

            duplicates[file_path].append(other_file_path)
            duplicates[other_file_path] = duplicates[file_path]
            found_duplicates_indices.add(other_file_idx)

    return duplicates


def find_duplicates_for_file_by_phash(hash_dict: HashDict, file_path: str, distance: int):
    duplicates = find_duplicates_by_phash(hash_dict, distance)
    for file, dupes in duplicates.items():
        if file == file_path:
            return dupes
    return []


def find_files(base_path: str | Path) -> List[Path]:
    def is_video_file(file):
        suffix = Path(file).suffix.lower()
        return suffix in [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm", ".m4v"]

    files = []
    if not isinstance(base_path, Path):
        base_path = Path(base_path)
    for root, _, files_in_dir in base_path.walk():
        for name in files_in_dir:
            file_path = root/name
            if not is_video_file(file_path):
                continue
            files.append(file_path)
    return files
