from dataclasses import dataclass
from front.elements import InputBase
from hear import WavLocalFileStore
import pandas as pd


@dataclass
class DataLoader(InputBase):
    root_dir: str = None
    annot_path: str = None

    def __post_init__(self):
        super().__post_init__()
        self.store = WavLocalFileStore(self.root_dir)

        self.annots = pd.read_csv(self.annot_path)

    def render(self):
        print("done!")
        return len(self.annots)
