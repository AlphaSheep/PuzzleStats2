import json
import os
from re import compile, match, Pattern
from datetime import datetime, timedelta
from typing import Tuple, Any, Dict, List, Union

from importer.base_timer_importer import ITimerImporter
from result import Result


CSTIMER_EXPORT_FILE_PATTERN = compile('^cstimer_')
DATABASE_FOLDER = '../Databases/'
CSV_DUMPS_FOLDER = '../CSVDumps/'
RESULTS_FILENAME = 'CSTimerResults.json'

CSTIMER_RESULT_FILES = [
    CSV_DUMPS_FOLDER + RESULTS_FILENAME]

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
        _load_convert_and_dump_latest_cstimer_export()
        self.reset()
        for source_file_name in CSTIMER_RESULT_FILES:
            self._import_from_file(source_file_name)

    def _import_from_file(self, source_file_name):
        source = 'cstimer: ' + source_file_name

        with open(source_file_name) as file_stream:
            raw_results = json.load(file_stream)

        for solution in raw_results:
            category = solution[1].strip()
            if category in CSTIMER_CATEGORIES_MAP:
                category = CSTIMER_CATEGORIES_MAP[category]
            self.categories.add(category)

            dnf_flag = solution[3]
            if dnf_flag == -1:
                if category in self.dnf_counts.keys():
                    self.dnf_counts[category] += 1
                else:
                    self.dnf_counts[category] = 1
            else:
                result = self._interpret_solution_line(solution, source, category)
                self.results.append(result)

    @staticmethod
    def _interpret_solution_line(solution, source, category):
        start = datetime.strptime(solution[0], '%Y-%m-%dT%H:%M:%S')
        time = timedelta(seconds=float(solution[2]))
        penalty = timedelta(seconds=0)
        return Result(start, time, category, penalty, source)


def _get_latest_cstimer_export(database_folder: str, pattern: Pattern = CSTIMER_EXPORT_FILE_PATTERN) -> str:
    files = os.listdir(database_folder)
    cstimer_files = [f for f in files if match(pattern, f) is not None]
    cstimer_files.sort()
    return cstimer_files[-1]


def _read_raw_cstimer_export(filename: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    with open(filename) as export_file:
        raw_times = json.load(export_file)
    session_properties = json.loads(raw_times['properties']['sessionData'])
    return raw_times, session_properties


def _process_raw_results_to_list(raw_data: Dict[str, Any], session_properties: Dict[str, Any]) -> List[List[Any]]:
    all_results = []

    for session in session_properties.keys():
        category = session_properties[session]['name']
        results = raw_data['session' + session]
        if len(results) > 0:
            for result in results:
                penalty: int = result[0][0]
                time: int = result[0][1] / 1000
                scramble: str = result[1]
                timestamp: datetime = datetime.utcfromtimestamp(result[3])

                all_results.append([timestamp.isoformat(), category, time, penalty, scramble])
    return all_results


def _save_results(all_results, output_filename):
    with open(output_filename, 'w') as output_file:
        json.dump(all_results, output_file)


def _load_convert_and_dump_latest_cstimer_export() -> None:
    cstimer_export = DATABASE_FOLDER + _get_latest_cstimer_export(DATABASE_FOLDER, CSTIMER_EXPORT_FILE_PATTERN)

    raw_data, session_properties = _read_raw_cstimer_export(cstimer_export)
    all_results = _process_raw_results_to_list(raw_data, session_properties)

    output_filename = CSV_DUMPS_FOLDER + RESULTS_FILENAME
    _save_results(all_results, output_filename)
