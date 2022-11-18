import csv
from datetime import datetime, timedelta

from importer.base_timer_importer import ITimerImporter
from result import Result


plusTimerCSVFiles = [
    '../CSVDumps/PlusTimerResults.csv']

plusTimerCategories = {
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

        for plusTimerCSV in plusTimerCSVFiles:
            print('Reading', plusTimerCSV)
            source = 'Plus Timer Android: ' + plusTimerCSV

            with open(plusTimerCSV) as thisFile:
                csv_file = csv.reader(thisFile)
                for solution_line in csv_file:
                    try:
                        start = datetime.strptime(solution_line[1], '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        # If the decimal place is .00, then it is left off during the data export, causing a format
                        # mismatch, so we try converting again, but without the decimal.
                        start = datetime.strptime(solution_line[1], '%Y-%m-%d %H:%M:%S')

                    time = timedelta(seconds=float(solution_line[2]))
                    category = plusTimerCategories[solution_line[0]].strip()
                    self.categories.add(category)

                    if solution_line[3] == 'DNF':
                        # Handle DNF penalty
                        if category in self.dnf_counts.keys():
                            self.dnf_counts[category] += 1
                        else:
                            self.dnf_counts[category] = 1
                        # Ignore DNFs in the results, just keep a count
                        continue

                    try:
                        penalty = timedelta(seconds=float(solution_line[3]))
                    except ValueError:
                        penalty = timedelta(seconds=0)

                    result = Result(start, time, category, penalty, source)

                    self.results.append(result)
