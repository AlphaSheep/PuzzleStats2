import csv
from datetime import datetime, timedelta
from typing import List

from importer.base_timer_importer import ITimerImporter
from result import Result


_PRISMA_CSV_FILES = [
    '../CSVDumps/Prisma_Titan.csv',
    '../CSVDumps/Prisma_Iapetus.csv',
    '../CSVDumps/Prisma_Encaladus.csv']


class PrismaImporter(ITimerImporter):

    def import_all(self) -> None:

        for csvFile in _PRISMA_CSV_FILES:
            print('Reading', csvFile)
            source = 'Prisma: ' + csvFile

            with open(csvFile) as thisFile:
                this_csv_file = csv.reader(thisFile)

                for solution in this_csv_file:

                    if solution[0] == 'SOLUTION_ID':
                        continue  # Skip header line

                    category = solution[10].strip()
                    self.categories.add(category)

                    start = datetime.strptime(solution[4], '%Y-%m-%d %H:%M:%S.%f')
                    end = datetime.strptime(solution[5], '%Y-%m-%d %H:%M:%S.%f')
                    try:
                        penalty = timedelta(seconds=int(solution[6]))
                    except ValueError:
                        penalty = timedelta(seconds=0)

                    if solution[6] == 'DNF':
                        # Handle DNF penalty
                        if category in self.dnf_counts.keys():
                            self.dnf_counts[category] += 1
                        else:
                            self.dnf_counts[category] = 1
                        # Ignore DNFs in the results, just keep a count
                        continue

                    time = (end - start) + penalty
                    result = Result(start, time, category, penalty, source)

                    self.results.append(result)

