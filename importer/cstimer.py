import json
from datetime import datetime, timedelta

from importer.base_timer_importer import ITimerImporter
from result import Result

CSTIMER_RESULT_FILES = [
    '../CSVDumps/CSTimerResults.json']

CSTIMER_CATEGORIES_MAP = {
    '3x3x3 Cube': "Rubik's cube",
    '2x2x2': "2x2x2 cube",
    '4x4x4': "4x4x4 cube",
    '5x5x5': "5x5x5 cube",
    '6x6x6': "6x6x6 cube",
    '7x7x7': "7x7x7 cube",
    'Skewb': "Skewb",
    'Pyraminx': "Pyraminx",
    'Megaminx': "Megaminx",
    'Square-1': "Square-1",
    'FTO': "FTO",
    '3x3 Blindfolded': "Rubik's cube blindfolded",
    'Clock': "Rubik's clock",
    'ZZ One handed': "Rubik's cube one-handed",
    'Roux Practice': "Roux Practice"}


class CSTimerImporter(ITimerImporter):

    def import_all(self) -> None:
        for source_file_name in CSTIMER_RESULT_FILES:
            source = 'cstimer: ' + source_file_name

            with open(source_file_name) as file_stream:
                raw_results = json.load(file_stream)

            for solution in raw_results:
                category = solution[1].strip()
                if category in CSTIMER_CATEGORIES_MAP:
                    category = CSTIMER_CATEGORIES_MAP[category]
                self.categories.add(category)

                start = datetime.strptime(solution[0], '%Y-%m-%dT%H:%M:%S')
                time = timedelta(seconds=float(solution[2]))

                dnf = solution[3]
                if dnf == -1:
                    if category in self.dnf_counts.keys():
                        self.dnf_counts[category] += 1
                    else:
                        self.dnf_counts[category] = 1

                penalty = timedelta(seconds=0)

                result = Result(start, time, category, penalty, source)
                self.results.append(result)
