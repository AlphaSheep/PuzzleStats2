import csv
from datetime import timedelta, datetime
from typing import List

from importer.base_timer_importer import BaseTimerImporter
from solves import Solve


class FMCFileImporter(BaseTimerImporter):

    def __init__(self):
        super().__init__()
        self.files: List[str] = []
        self.category_config: List[str] = []

    def import_all(self) -> None:
        self.reset()
        for iFile in range(len(self.files)):
            source_file_name = self.files[iFile]

            category = self.category_config[iFile].strip()
            self.categories.add(category)

            source = 'Manual FMC Results: ' + source_file_name

            with open(source_file_name) as file_stream:
                csv_file = csv.reader(file_stream)
                for solution in csv_file:
                    start = datetime.strptime(solution[0], '%Y-%m-%d')
                    time = timedelta(seconds=float(solution[1]))
                    penalty = timedelta(seconds=0)

                    result = Solve(start, time, category, penalty, source)
                    self.solves.append(result)

