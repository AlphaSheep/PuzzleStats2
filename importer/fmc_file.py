import csv
from datetime import timedelta, datetime

from importer.base_timer_importer import ITimerImporter
from result import Result

FMC_RESULT_FILES = [
    '../CSVDumps/FMCResults.csv']

FMC_CATEGORIES = ['3x3 Fewest Moves'] # Correspond to the files in FMC_RESULT_FILES


class FMCFileImporter(ITimerImporter):

    def import_all(self) -> None:
        self.reset()
        for iFile in range(len(FMC_RESULT_FILES)):
            source_file_name = FMC_RESULT_FILES[iFile]

            category = FMC_CATEGORIES[iFile].strip()
            self.categories.add(category)

            source = 'Manual FMC Results: ' + source_file_name

            with open(source_file_name) as file_stream:
                csv_file = csv.reader(file_stream)
                for solution in csv_file:
                    start = datetime.strptime(solution[0], '%Y-%m-%d')
                    time = timedelta(seconds=float(solution[1]))
                    penalty = timedelta(seconds=0)

                    result = Result(start, time, category, penalty, source)
                    self.results.append(result)

