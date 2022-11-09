import csv
from datetime import datetime, timedelta
from typing import List

from importer.base_timer_importer import ITimerImporter
from result import Result


_ANDROID_MONTHS_START = [9, 8]
_ANDROID_CATEGORY_NAMES = ["Rubik's cube", "2x2x2 cube"]  # Correspond to the names in androidCSVFiles

_ZERO_TIME = datetime.strptime('00:00.00', '%M:%S.%f')

_ANDROID_CSV_FILES = [
    '../CSVDumps/3 x 3 x 3 Cube - S 11, 2014 - 09.22.25 PM.csv',
    '../CSVDumps/2 x 2 x 2 Cube - A 01, 2014 - 11.53.51 AM.csv']


class SCTAndroidImporter(ITimerImporter):

    def load_all(self) -> List[Result]:

        all_results = []
        categories = []

        for i in range(len(_ANDROID_CSV_FILES)):
            source_file_name = _ANDROID_CSV_FILES[i]
            month = _ANDROID_MONTHS_START[i] + 1
            category = _ANDROID_CATEGORY_NAMES[i].strip()

            source = 'SpeedCube Timer Android: ' + source_file_name
            with open(source_file_name) as thisFile:
                this_csv_file = csv.reader(thisFile)

                # Dates from SpeedCube Timer on Android are ambiguous
                # This assumes dates are in reverse chronological order starting from September,
                # all in the same year, and with no months missing, and with the first day of
                # each month less than the last day of the previous month.

                last = 0

                for solution_line in this_csv_file:
                    if solution_line[0] == 'Date & Time':
                        continue  # Skip header line

                    if int(solution_line[0][2:4]) > last:
                        month -= 1
                    last = int(solution_line[0][2:4])

                    date = solution_line[0][5:9] + '-' + '{:02d}'.format(month) + '-' + solution_line[0][2:4] + ' ' + solution_line[0][10:]
                    start = datetime.strptime(date, '%Y-%m-%d %I:%M:%S %p')

                    time = (datetime.strptime(solution_line[1], '%M:%S.%f') - _ZERO_TIME)

                    penalty = timedelta(seconds=0)

                    result = Result(start, time, category, penalty, source)
                    all_results.append(result)
                    categories.append(category)

        return all_results
