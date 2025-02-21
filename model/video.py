from __future__ import annotations

from typing import List, Optional, Dict


class Video:
    name: str
    versions: List[VideoVersion]

    def __init__(self):
        self.name = ""
        self.versions = []

    def __repr__(self):
        return f"Video: {self.name} with {len(self.versions)} versions"

    def __eq__(self, other):
        if not isinstance(other, Video):
            return False
        if self.name != other.name:
            return False
        if len(self.versions) != len(other.versions):
            return False
        for i, version in enumerate(self.versions):
            if version != other.versions[i]:
                return False
        return True

    def get_version_by_hash(self, hash_type: str, hash_value: str) -> Optional[VideoVersion]:
        for version in self.versions:
            if version.hashes.get(hash_type, None) == hash_value:
                return version
        return None

    def as_dict(self) -> Dict:
        dic = {"name": self.name}
        versions = []
        for version in self.versions:
            versions.append(version.as_dict())
        dic["versions"] = versions
        return dic

    def from_dict(self, dic: Dict):
        self.name = dic["name"]
        self.versions = []
        for version in dic["versions"]:
            ver = VideoVersion()
            ver.from_dict(version)
            self.versions.append(ver)


class VideoVersion:
    tags: List[str]
    hashes: Dict[str, str]
    suffix: str

    def __init__(self):
        self.tags = []
        self.hashes = {}
        self.suffix = ""

    def __repr__(self):
        return f"VideoVersion: {self.tags} with {len(self.hashes)} hashes"

    def __eq__(self, other):
        if not isinstance(other, VideoVersion):
            return False
        if self.suffix != other.suffix:
            return False

        if len(self.tags) != len(other.tags):
            return False
        if len(self.hashes) != len(other.hashes):
            return False
        for i, tag in enumerate(self.tags):
            if tag != other.tags[i]:
                return False
        for key, value in self.hashes.items():
            if value != other.hashes.get(key, None):
                return False

        return True

    def as_dict(self) -> Dict:
        dic = {}
        if self.tags is not None:
            dic["tags"] = self.tags
        if self.hashes is not None:
            dic["hashes"] = self.hashes
        if self.suffix is not None:
            dic["suffix"] = self.suffix
        return dic

    def from_dict(self, dic: Dict):
        self.tags = dic.get("tags", [])
        self.hashes = dic.get("hashes", {})
        self.suffix = dic.get("suffix", "")
