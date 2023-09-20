import csv
from datetime import datetime, timedelta
from typing import List, Dict

from importer.base_timer_importer import BaseTimerImporter
from solves import Statistic, Result

_DNF_FLAG = 'DNF'


class PrismaImporter(BaseTimerImporter):

    def __init__(self) -> None:
        super().__init__()
        self.files: List[str] = []
        self.category_config: Dict[str, str] = {}

    def import_all(self) -> None:
        self.reset()
        for csv_file in self.files:
            self._import_from_file(csv_file)

    def _import_from_file(self, source_file_name: str) -> None:
        source = 'Prisma: ' + source_file_name
        with open(source_file_name) as file_stream:
            csv_file = csv.reader(file_stream)

            for solution in csv_file:

                if solution[0] == 'SOLUTION_ID':
                    continue  # Skip header line

                category = solution[10].strip()
                if category in self.category_config.keys():
                    category = self.category_config[category]

                self.categories.add(category)

                if solution[6] == _DNF_FLAG:
                    # Ignore DNFs in the results, just keep a count
                    if category in self.dnf_counts.keys():
                        self.dnf_counts[category] += 1
                    else:
                        self.dnf_counts[category] = 1
                else:
                    result = self._interpret_solution_line(solution, source, category)
                    self.solves.append(result)

    @staticmethod
    def _interpret_solution_line(solution, source, category) -> Statistic:
        start = datetime.strptime(solution[4], '%Y-%m-%d %H:%M:%S.%f')
        end = datetime.strptime(solution[5], '%Y-%m-%d %H:%M:%S.%f')

        try:
            penalty = timedelta(seconds=int(solution[6]))
        except ValueError:
            penalty = timedelta(seconds=0)

        time = Result((end - start) + penalty)

        return Statistic(start, time, category, source)
