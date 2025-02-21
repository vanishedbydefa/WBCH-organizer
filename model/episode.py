from typing import Dict

from model.video import Video, VideoVersion


class Episode(Video):
    number: str

    def __init__(self):
        super().__init__()
        self.number = str(0)

    def __repr__(self):
        return f"Episode {self.number}: {self.name} with {len(self.versions)} versions"

    def from_dict(self, dic: Dict):
        super().from_dict(dic)
        self.number = dic["number"]

    def as_dict(self) -> Dict:
        dic = super().as_dict()
        dic["number"] = self.number
        return dic

    def __eq__(self, other):
        if not isinstance(other, Episode):
            return False
        if self.number != other.number:
            return False
        return super().__eq__(other)
