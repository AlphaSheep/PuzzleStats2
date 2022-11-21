import csv
from datetime import datetime, timedelta
from typing import List, Dict

from importer.base_timer_importer import ITimerImporter
from result import Result


class PlusTimerImporter(ITimerImporter):

    def __init__(self):
        super().__init__()
        self.files: List[str] = []
        self.category_config: Dict[str, str] = {}

    def import_all(self) -> None:
        self.reset()
        for source_file_name in self.files:
            self._import_from_file(source_file_name)

    def _import_from_file(self, source_file_name: str) -> None:
        source = 'Plus Timer Android: ' + source_file_name

        with open(source_file_name) as file_stream:
            csv_file = csv.reader(file_stream)
            for solution in csv_file:

                category = self.category_config[solution[0]].strip()
                self.categories.add(category)

                if solution[3] == 'DNF':
                    # Handle DNF penalty
                    if category in self.dnf_counts.keys():
                        self.dnf_counts[category] += 1
                    else:
                        self.dnf_counts[category] = 1
                else:
                    result = self._interpret_solution_line(solution, source, category)
                    self.results.append(result)

    @staticmethod
    def _interpret_solution_line(solution, source, category) -> Result:
        try:
            start = datetime.strptime(solution[1], '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            # If the decimal place is .00, then it is left off during the data export, causing a format
            # mismatch, so we try converting again, but without the decimal.
            start = datetime.strptime(solution[1], '%Y-%m-%d %H:%M:%S')
        time = timedelta(seconds=float(solution[2]))

        try:
            penalty = timedelta(seconds=float(solution[3]))
        except ValueError:
            penalty = timedelta(seconds=0)

        return Result(start, time, category, penalty, source)
