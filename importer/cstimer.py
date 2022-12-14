import json
import os
from re import compile, match, Pattern
from datetime import datetime, timedelta
from typing import Tuple, Any, Dict, List, Union

from importer.base_timer_importer import BaseTimerImporter
from result import Result


_DNF_FLAG = -1


class CSTimerImporter(BaseTimerImporter):

    def __init__(self):
        super().__init__()
        self.folder: str = ""
        self.pattern: str = ""
        self.category_config: Dict[str, str] = {}

    def import_all(self) -> None:
        self.reset()
        self._load_convert_and_dump_latest_cstimer_export()

    def _get_latest_cstimer_export(self) -> str:
        files = os.listdir(self.folder)
        cstimer_files = [f for f in files if match(compile(self.pattern), f) is not None]
        cstimer_files.sort()
        return cstimer_files[-1]

    @staticmethod
    def _read_raw_cstimer_export(filename: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        with open(filename) as export_file:
            raw_times = json.load(export_file)
        session_properties = json.loads(raw_times['properties']['sessionData'])
        return raw_times, session_properties

    def _import_raw_results(self, raw_data: Dict[str, Any], session_properties: Dict[str, Any]) -> None:
        for session in session_properties.keys():
            category = session_properties[session]['name']
            if category in self.category_config.keys():
                category = self.category_config[category]
            results = raw_data['session' + session]
            if len(results) > 0:
                for solution in results:
                    dnf_flag = solution[0][0]
                    if dnf_flag == _DNF_FLAG:
                        if category in self.dnf_counts.keys():
                            self.dnf_counts[category] += 1
                        else:
                            self.dnf_counts[category] = 1
                    else:
                        result = self._interpret_single_result(category, solution)
                        self.results.append(result)

    @staticmethod
    def _interpret_single_result(category, solution):
        penalty: timedelta = timedelta(seconds=solution[0][0])
        time: timedelta = timedelta(seconds=solution[0][1] / 1000)
        scramble: str = solution[1]
        timestamp: datetime = datetime.utcfromtimestamp(solution[3])
        result = Result(timestamp, time, category, penalty, scramble)
        return result

    def _load_convert_and_dump_latest_cstimer_export(self) -> None:
        latest_file: str = self._get_latest_cstimer_export()
        cstimer_export: str = self.folder + latest_file

        raw_data, session_properties = self._read_raw_cstimer_export(cstimer_export)
        self._import_raw_results(raw_data, session_properties)
