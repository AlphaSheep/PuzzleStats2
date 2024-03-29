import csv
from datetime import timedelta, datetime
from typing import List

from importer.base_timer_importer import BaseTimerImporter
from solves import Statistic, Result


class FMCFileImporter(BaseTimerImporter):

    def __init__(self) -> None:
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

                seen_dates = set()

                for solution in csv_file:
                    start = datetime.strptime(solution[0], '%Y-%m-%d')
                    while start in seen_dates:
                        # Handle multiple attempts on the same day
                        start += timedelta(minutes=1)

                    seen_dates.add(start)

                    time = Result(int(solution[1]))

                    penalty = timedelta(seconds=0)

                    result = Statistic(start, time, category, source)
                    self.solves.append(result)

