import csv
from datetime import datetime, timedelta
from typing import List, Final, Dict, Any

from importer.base_timer_importer import BaseTimerImporter
from result import Result


_ZERO_TIME: Final[datetime] = datetime.strptime('00:00.00', '%M:%S.%f')


class SCTAndroidImporter(BaseTimerImporter):

    def __init__(self):
        super().__init__()
        self.files: List[str] = []
        self.category_config: List[str] = []

    def import_all(self) -> None:
        self.reset()
        for i in range(len(self.files)):
            source_file_name = self.files[i]
            month = self.additional_data['start_months'][i] + 1
            category = self.category_config[i].strip()

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
