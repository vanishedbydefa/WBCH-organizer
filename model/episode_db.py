from __future__ import annotations

from typing import List, Dict, Optional, Tuple

from model.group import Group
from model.season import Season
from model.episode import Episode
from model.video import Video, VideoVersion


class EpisodeDb:
    seasons: List[Season]
    other_groups: List[Group]

    def __init__(self):
        self.seasons = []
        self.other_groups = []

    def get_episode(self, season_number: int, episode_number: str) -> Optional[Episode]:
        season = self.get_season(season_number)
        if not season:
            return None
        return season.get_episode_by_number(episode_number)

    def get_season(self, season_number: int) -> Optional[Season]:
        for season in self.seasons:
            if season.number == season_number:
                return season
        return None

    def get_version_by_hash(self, hash_type: str, hash_value: str) -> Optional[Tuple[Season|Group, Video|Episode, VideoVersion]]:
        for season in self.seasons:
            version_tuple = season.get_version_by_hash(hash_type, hash_value)
            if version_tuple:
                (video, version) = version_tuple
                return season, video, version
        for group in self.other_groups:
            version_tuple = group.get_version_by_hash(hash_type, hash_value)
            if version_tuple:
                (video, version) = version_tuple
                return group, video, version
        return None

    def __repr__(self):
        return f"EpisodeDb: {len(self.seasons)} seasons, {len(self.other_groups)} other groups"

    def __eq__(self, other):
        if not isinstance(other, EpisodeDb):
            return False
        if len(self.seasons) != len(other.seasons):
            return False
        if len(self.other_groups) != len(other.other_groups):
            return False
        for i, season in enumerate(self.seasons):
            if season != other.seasons[i]:
                return False
        for i, group in enumerate(self.other_groups):
            if group != other.other_groups[i]:
                return False
        return True

    def from_dict(self, dic: Dict):
        for season in dic["seasons"]:
            new_season = Season()
            new_season.from_dict(season)
            self.seasons.append(new_season)
        for group in dic["other_groups"]:
            new_group = Group()
            new_group.from_dict(group)
            self.other_groups.append(new_group)

    def as_dict(self):
        dic = {}
        seasons = []
        for season in self.seasons:
            seasons.append(season.as_dict())
        dic["seasons"] = seasons

        groups = []
        for group in self.other_groups:
            groups.append(group.as_dict())
        dic["other_groups"] = groups

        return dic
