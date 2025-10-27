from abc import ABC, abstractmethod

class SheetFileReader(ABC):
    @abstractmethod
    def read(bytes, sheet_number = 1):
        pass