from concurrent.futures import ProcessPoolExecutor, Future, as_completed
import json
from pathlib import Path
from typing import List, Dict, Optional, Callable, Tuple

from logger import logger
import os


class HashDict:
    __hash_dict: Dict[str, Dict[str, str]]
    json_path: Path

    def __init__(self, json_path: str | Path):
        if not isinstance(json_path, Path):
            json_path = Path(json_path)
        self.json_path = json_path
        self.__hash_dict = {}

    def load_dict_from_file(self):
        if not self.json_path.exists():
            logger.warn("No index found")
            return

        with open(self.json_path, "r") as f:
            wbch_files = json.load(f)

        for file_path, hashes in wbch_files.items():
            single_file_hash_dict = {}
            for hash_name, hash_value in hashes.items():
                single_file_hash_dict[hash_name] = hash_value
            self.__hash_dict[file_path] = single_file_hash_dict

    def persist_dict_to_file(self):
        wbch_str = json.dumps(self.__hash_dict, indent=2)
        with open(self.json_path, "w") as f:
            f.write(wbch_str)
        logger.info("Index persisted")

    def get_file_names_in_dict(self) -> List[str]:
        return list(self.__hash_dict.keys())

    def file_has_hash(self, file_path: str | Path, hash_type: str) -> bool:
        file_path = str(file_path)
        if file_path in self.__hash_dict:
            return hash_type in self.__hash_dict[file_path]
        return False

    def get_hash(self, file_path: str | Path, hash_type: str) -> Optional[str]:
        file_path = str(file_path)
        if file_path in self.__hash_dict:
            return self.__hash_dict[file_path][hash_type]
        return None

    def get_hashes(self, file_path: str | Path) -> Dict[str, str]:
        file_path = str(file_path)
        if file_path in self.__hash_dict:
            return self.__hash_dict[file_path]
        return {}

    def clear_hash_type(self, hash_type: str):
        for file_path, hash_dict in self.__hash_dict.items():
            if hash_type in hash_dict:
                del hash_dict[hash_type]

    def find_file_by_hash(self, hash_value: str, hash_type: Optional[str] = None) -> Optional[Path]:
        for file_path, hash_dict in self.__hash_dict.items():
            if hash_type:
                if hash_type in hash_dict and hash_dict[hash_type] == hash_value:
                    return Path(file_path)
            else:
                for hash_name, hash_val in hash_dict.items():
                    if hash_val == hash_value:
                        return Path(file_path)
        return None

    def set_hash(self, file_path: str | Path, hash_type: str, hash_value: str):
        file_path = str(file_path)
        if file_path not in self.__hash_dict:
            self.__hash_dict[file_path] = {}
        self.__hash_dict[file_path][hash_type] = hash_value

    def get_dict(self) -> Dict[str, Dict[str, str]]:
        return self.__hash_dict.copy()

    def get_hash_type_dict(self, hash_type: str) -> Dict[str, str]:
        hash_type_dict = {}
        for file_path, hash_dict in self.__hash_dict.items():
            if hash_type in hash_dict:
                hash_type_dict[file_path] = hash_dict[hash_type]
        return hash_type_dict

    def clean_removed_files(self):
        for file_path in list(self.__hash_dict.keys()):
            if not os.path.exists(file_path):
                logger.info(f"Removing file: {file_path} from index")
                del self.__hash_dict[file_path]


class Hasher:
    hash_function: Callable[[Path], Tuple[Path, Optional[str]]]
    hash_name: str
    hash_dict: HashDict
    file_names: List[Path]
    num_workers: int

    def __init__(self, hash_function: Callable[[Path], Tuple[Path, Optional[str]]], hash_name: str, hash_dict: HashDict,
                 file_names: List[str | Path], num_workers: int = 4):
        self.hash_function = hash_function
        self.hash_name = hash_name
        self.hash_dict = hash_dict
        self.file_names = []
        self.num_workers = num_workers
        for file_name in file_names:
            if not isinstance(file_name, Path):
                file_name = Path(file_name)
            if not os.path.exists(file_name):
                logger.warn(f"File not found: {file_name}")
                continue
            if self.hash_dict.file_has_hash(file_name, hash_name):
                continue
            self.file_names.append(file_name)

    def hash_files(self):
        if len(self.file_names) == 0:
            logger.info(f"No files to hash with hasher: {self.hash_name}")
            return
        if self.num_workers > 1:
            self.__hash_files_parallel()
        else:
            self.__hash_files_serial()

    def __hash_files_parallel(self):
        logger.info(f"Hashing {len(self.file_names)} files with {self.num_workers} workers")
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures: List[Future] = []
            for file_path in self.file_names:
                futures.append(executor.submit(self.hash_function, file_path))

            for future in as_completed(futures):
                file_path, file_hash = future.result()
                if file_hash:
                    self.hash_dict.set_hash(file_path, self.hash_name, file_hash)
                    logger.debug(f"Hash: {file_hash} belongs to file: {file_path}")

    def __hash_files_serial(self):
        logger.info(f"Hashing {len(self.file_names)} files serially")
        for file_path in self.file_names:
            _, file_hash = self.hash_function(file_path)
            if file_hash:
                self.hash_dict.set_hash(file_path, self.hash_name, file_hash)
                logger.debug(f"Hash: {file_hash} belongs to file: {file_path}")


def phash_file(file_path: Path, work_dir: Optional[Path] = None) -> Tuple[Path, Optional[str]]:
    from videohash2 import VideoHash, VideoHashError
    work_dir = str(work_dir) if work_dir else None
    try:
        video_hash = VideoHash(path=str(file_path), storage_path=work_dir, frame_interval=0.5, do_not_copy=True)
        phash = video_hash.hash_hex
        video_hash.delete_storage_path()
        return file_path, phash
    except VideoHashError as e:
        logger.error(f"Error hashing file: {file_path}, Error: {e}")
        return file_path, None


def hash_file(file_path: Path) -> Tuple[Path, Optional[str]]:
    import hashlib
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(1 * 10 ** 6), b""):
                sha256_hash.update(chunk)
        return file_path, sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing file: {file_path}, Error: {e}")
        return file_path, None
