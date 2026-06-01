from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    @abstractmethod
    def run(self, df: pd.DataFrame) -> dict:
        pass
