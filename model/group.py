from typing import List, Dict, Optional, Tuple

from model.video import Video, VideoVersion


class Group:
    name: str
    videos: List[Video]

    def __init__(self):
        self.videos = []
        self.name = ""

    def get_version_by_hash(self, hash_type: str, hash_value: str) -> Optional[Tuple[Video, VideoVersion]]:
        for video in self.videos:
            version = video.get_version_by_hash(hash_type, hash_value)
            if version:
                return video, version
        return None

    def __repr__(self):
        return f"Group: {self.name} with {len(self.videos)} videos"

    def __eq__(self, other):
        if not isinstance(other, Group):
            return False
        if self.name != other.name:
            return False
        if len(self.videos) != len(other.videos):
            return False
        for i, video in enumerate(self.videos):
            if video != other.videos[i]:
                return False
        return True

    def as_dict(self) -> Dict:
        dic = {"name": self.name}
        videos = []
        for video in self.videos:
            videos.append(video.as_dict())
        dic["videos"] = videos
        return dic

    def from_dict(self, dic: Dict):
        self.name = dic["name"]
        for video in dic["videos"]:
            vid = Video()
            vid.from_dict(video)
            self.videos.append(vid)
