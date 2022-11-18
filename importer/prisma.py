import csv
from datetime import datetime, timedelta

from importer.base_timer_importer import ITimerImporter
from result import Result

_PRISMA_CSV_FILES = [
    '../CSVDumps/Prisma_Titan.csv',
    '../CSVDumps/Prisma_Iapetus.csv',
    '../CSVDumps/Prisma_Encaladus.csv']


class PrismaImporter(ITimerImporter):

    def import_all(self) -> None:
        for csv_file in _PRISMA_CSV_FILES:
            self._import_from_file(csv_file)

    def _import_from_file(self, source_file_name: str) -> None:
        source = 'Prisma: ' + source_file_name
        with open(source_file_name) as file_stream:
            csv_file = csv.reader(file_stream)

            for solution in csv_file:

                if solution[0] == 'SOLUTION_ID':
                    continue  # Skip header line

                category = solution[10].strip()
                self.categories.add(category)

                if solution[6] == 'DNF':
                    # Ignore DNFs in the results, just keep a count
                    if category in self.dnf_counts.keys():
                        self.dnf_counts[category] += 1
                    else:
                        self.dnf_counts[category] = 1
                else:
                    result = self._interpret_solution_line(solution, source, category)
                    self.results.append(result)

    @staticmethod
    def _interpret_solution_line(solution, source, category) -> Result:
        start = datetime.strptime(solution[4], '%Y-%m-%d %H:%M:%S.%f')
        end = datetime.strptime(solution[5], '%Y-%m-%d %H:%M:%S.%f')

        try:
            penalty = timedelta(seconds=int(solution[6]))
        except ValueError:
            penalty = timedelta(seconds=0)

        time = (end - start) + penalty

        return Result(start, time, category, penalty, source)
