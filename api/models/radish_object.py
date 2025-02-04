import json
from abc import ABC, abstractmethod

class RadishObject(ABC):
    @abstractmethod
    def toJSON(self):
        pass