import csv
from datetime import datetime, timedelta
from typing import List, Final

from importer.base_timer_importer import ITimerImporter
from result import Result


_ANDROID_CSV_FILES: Final[List[str]] = [
    '../CSVDumps/3 x 3 x 3 Cube - S 11, 2014 - 09.22.25 PM.csv',
    '../CSVDumps/2 x 2 x 2 Cube - A 01, 2014 - 11.53.51 AM.csv']
_ANDROID_CATEGORY_NAMES: Final[List[str]] = ["Rubik's cube", "2x2x2 cube"]  # Correspond to the names in androidCSVFiles

# Dates from SpeedCube Timer on Android are ambiguous
# This assumes dates are in reverse chronological order starting from a hardcoded  month,
# all in the same year, and with no months missing, and with the first day of
# each month less than the last day of the previous month.
_ANDROID_MONTHS_START: Final[List[int]] = [9, 8]

_ZERO_TIME: Final[datetime] = datetime.strptime('00:00.00', '%M:%S.%f')


class SCTAndroidImporter(ITimerImporter):

    def import_all(self) -> None:
        self.reset()
        for i in range(len(_ANDROID_CSV_FILES)):
            source_file_name = _ANDROID_CSV_FILES[i]
            month = _ANDROID_MONTHS_START[i] + 1
            category = _ANDROID_CATEGORY_NAMES[i].strip()

            self._import_from_file(category, month, source_file_name)

    def _import_from_file(self, category: str, month: int, source_file_name: str) -> None:
        source = 'SpeedCube Timer Android: ' + source_file_name
        last = 0

        with open(source_file_name) as file_stream:
            csv_file = csv.reader(file_stream)

            for solution_line in csv_file:
                if solution_line[0] == 'Date & Time':
                    continue  # Skip header line
                if int(solution_line[0][2:4]) > last:
                    month -= 1
                last = int(solution_line[0][2:4])

                result = self._interpret_solution_line(category, month, solution_line, source)

                self.results.append(result)
                self.categories.add(category)

    @staticmethod
    def _interpret_solution_line(category, month, solution_line, source) -> Result:
        # date = solution_line[0][5:9] + '-' + '{:02d}'.format(month) +
        # '-' + solution_line[0][2:4] + ' ' + solution_line[0][10:]
        date = f"{solution_line[0][5:9]}-{month:02d}-{solution_line[0][2:4]} {solution_line[0][10:]}"

        start = datetime.strptime(date, '%Y-%m-%d %I:%M:%S %p')
        time = (datetime.strptime(solution_line[1], '%M:%S.%f') - _ZERO_TIME)

        penalty = timedelta(seconds=0)
        return Result(start, time, category, penalty, source)
