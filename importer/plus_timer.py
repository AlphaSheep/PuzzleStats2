import csv
from datetime import datetime, timedelta

from importer.base_timer_importer import ITimerImporter
from result import Result


PLUS_TIMER_FILES = [
    '../CSVDumps/PlusTimerResults.csv']

PLUS_TIMER_CATEGORIES = {
    '3x3': "Rubik's cube",
    '3x3-OH': "Rubik's cube one-handed",
    '3x3-Feet': "Rubik's cube with feet",
    '4x4': '4x4x4 cube',
    '5x5': '5x5x5 cube',
    '6x6': '6x6x6 cube',
    '7x7': '7x7x7 cube',
    'Pyraminx': 'Pyraminx',
    'Megaminx': 'Megaminx',
    'Skewb': 'Skewb',
    '3x3-BLD': "Rubik's cube blindfolded",
    'Square-1': 'Square-1',
    'Clock': "Rubik's clock"}


class PlusTimerImporter(ITimerImporter):

    def import_all(self) -> None:
        self.reset()
        for source_file_name in PLUS_TIMER_FILES:
            self._import_from_file(source_file_name)

    def _import_from_file(self, source_file_name: str) -> None:
        source = 'Plus Timer Android: ' + source_file_name

        with open(source_file_name) as file_stream:
            csv_file = csv.reader(file_stream)
            for solution in csv_file:

                category = PLUS_TIMER_CATEGORIES[solution[0]].strip()
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
