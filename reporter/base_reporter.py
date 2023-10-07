
from abc import ABC, abstractmethod

from analysis import AnalysisEngine

class BaseReporter(ABC):

    def __init__(self):
        self.analysis: AnalysisEngine

        self.output_file: str = ''
        self.output_folder: str = ''

    def attach_analysis(self, analysis: AnalysisEngine):
        self.analysis = analysis

    @abstractmethod
    def generate(self) -> None:
        raise NotImplementedError
