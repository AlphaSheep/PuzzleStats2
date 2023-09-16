from typing import Dict
import os
import csv
from datetime import datetime, timedelta
from re import compile, match


from importer.base_timer_importer import BaseTimerImporter
from solves import Solve


class CubeastImporter(BaseTimerImporter):

    def __init__(self) -> None:
        super().__init__()
        self.folder: str = ""
        self.pattern: str = ""
        self.category_config: Dict[str, str] = {}


    def import_all(self) -> None:
        self.reset()
        self._load_latest_cubeast_export()

    def _get_latest_cubeast_export(self) -> str:
        all_files = os.listdir(self.folder)
        files = [f for f in all_files if match(compile(self.pattern), f) is not None]
        files.sort()
        return files[-1]

    def _import_from_file(self, source_file_name: str, source: str) -> None:
        with open(source_file_name) as file_stream:
            csv_file = csv.DictReader(file_stream)

            for solution in csv_file:

                category = solution['session_name']
                if category in self.category_config.keys():
                    category = self.category_config[category]

                if solution['dnf'] == 'true':
                    # Ignore DNFs in the results, just keep a count
                    if category in self.dnf_counts.keys():
                        self.dnf_counts[category] += 1
                    else:
                        self.dnf_counts[category] = 1

                else:
                    result = self._solution_to_sovle(solution, source, category)
                    self.solves.append(result)


    @staticmethod
    def _solution_to_sovle(solution: Dict[str, str], source: str, category: str) -> Solve:
        start = datetime.strptime(solution['date'], "%Y-%m-%d %H:%M:%S %Z")
        time = timedelta(seconds=float(solution['timer_time']) / 1000)

        two_sec = timedelta(seconds=2)
        zero_sec = timedelta(seconds=0)

        penalty: timedelta = \
            two_sec if solution['one_turn_away_two_second_penalty'] == 'true' else zero_sec + \
            two_sec if solution['inspection_two_second_penalty'] == 'true' else zero_sec

        return Solve(start, time, category, penalty, source)



    def _load_latest_cubeast_export(self) -> None:
        latest_file: str = self._get_latest_cubeast_export()
        cubeast_export: str = self.folder + latest_file

        source: str = 'Cubeast Export: ' + latest_file

        self._import_from_file(cubeast_export, source)

