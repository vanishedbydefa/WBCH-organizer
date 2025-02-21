from typing import List, Dict, Optional, Tuple

from model.episode import Episode
from model.video import Video, VideoVersion


class Season:
    number: int
    episodes: List[Episode]
    finale: Optional[Video]
    mid_season_finale: Optional[Video]
    name: str

    def __init__(self):
        self.name = ""
        self.episodes = []
        self.finale = None
        self.mid_season_finale = None
        self.number = 0

    def get_episode_by_number(self, episode_number: str) -> Optional[Episode]:
        for episode in self.episodes:
            if episode.number == episode_number:
                return episode
        return None

    def get_finale(self) -> Optional[Video]:
        return self.finale

    def get_version_by_hash(self, hash_type: str, hash_value: str) -> Optional[Tuple[Video | Episode, VideoVersion]]:
        for episode in self.episodes:
            version = episode.get_version_by_hash(hash_type, hash_value)
            if version:
                return episode, version
        if self.finale:
            version = self.finale.get_version_by_hash(hash_type, hash_value)
            if version:
                return self.finale, version

        if self.mid_season_finale:
            version = self.mid_season_finale.get_version_by_hash(hash_type, hash_value)
            if version:
                return self.mid_season_finale, version
        return None

    def __repr__(self):
        return f"Season {self.number}: {len(self.episodes)} episodes"

    def __eq__(self, other):
        if not isinstance(other, Season):
            return False

        if self.number != other.number:
            return False
        if self.name != other.name:
            return False

        if len(self.episodes) != len(other.episodes):
            return False

        if self.finale != other.finale:
            return False
        if self.mid_season_finale != other.mid_season_finale:
            return False

        for i, episode in enumerate(self.episodes):
            if episode != other.episodes[i]:
                return False
        return True

    def as_dict(self) -> Dict:
        dic = {"number": self.number, "name": self.name}
        episodes = []
        for episode in self.episodes:
            episodes.append(episode.as_dict())
        dic["episodes"] = episodes
        if self.finale:
            dic["finale"] = self.finale.as_dict()
        if self.mid_season_finale:
            dic["mid_season_finale"] = self.mid_season_finale.as_dict()
        return dic

    def from_dict(self, dic: Dict):
        self.number = dic["number"]
        self.name = dic["name"]
        for episode in dic["episodes"]:
            ep = Episode()
            ep.from_dict(episode)
            self.episodes.append(ep)
        if "finale" in dic:
            self.finale = Video()
            self.finale.from_dict(dic["finale"])
        if "mid_season_finale" in dic:
            self.mid_season_finale = Video()
            self.mid_season_finale.from_dict(dic["mid_season_finale"])
