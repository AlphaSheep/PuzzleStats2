from typing import List, Dict
from dataclasses import dataclass

import json

from solves import Category, StatisticCollection
from analysis.aggregations import Aggregation
from ..base_reporter import BaseReporter


@dataclass
class JSONResult:
    date: str
    value: float


class JSONReporter(BaseReporter):

    def __init__(self):
        super().__init__()
        self.output_file: str = ''

    def generate(self) -> None:
        categories = self.analysis.solves.get_distinct_categories()
        result: Dict[Category, Dict[Aggregation, List[JSONResult]]] = {}

        for category in categories:
            result[category] = self._get_for_category(category)

        with open(self.output_file, 'w') as file_stream:
            json.dump(result, file_stream, indent=4, default=lambda o: o.__dict__)

    def _get_for_category(self, category: Category) -> Dict[Aggregation, List[JSONResult]]:
        result: Dict[Aggregation, List[JSONResult]] = {}

        singles = self.analysis.solves.filter([category == event for event in self.analysis.solves.category])
        result[Aggregation("single")] = _get_JSONResult_List(singles)

        for stat_name in self.analysis.statistics[category]:
            result[stat_name] = self._get_for_statistic(category, stat_name)

        return result

    def _get_for_statistic(self, category: Category, stat_name: Aggregation) -> List[JSONResult]:
        return _get_JSONResult_List(self.analysis.statistics[category][stat_name])


def _get_JSONResult_List(solves: StatisticCollection) -> List[JSONResult]:
    return [ JSONResult(
        date=solve.date.isoformat(),
        value=float(solve.result)
    ) for solve in solves ]
