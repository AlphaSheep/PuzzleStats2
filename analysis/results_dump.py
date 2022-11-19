from datetime import datetime
from typing import Final, List, Set

from result import Result


DEFAULT_RESULTS_FILE: Final[str] = '../solvetimes.csv'


def dump_results(results: List[Result],
                 filter_categories: Set[str] = None,
                 file_name: str = DEFAULT_RESULTS_FILE) -> None:

    with open(file_name, 'w') as file_stream:
        result: Result
        for result in results:
            start: str = datetime.strftime(result.start, '%Y-%m-%d %H:%M:%S.%f')
            time: str = str(result.result.total_seconds())
            category: str = result.category
            penalty: str = str(result.penalty.total_seconds())
            source: str = result.source

            if filter_categories is None or category in filter_categories:
                file_stream.write(','.join([start, time, category, penalty, source]) + '\n')
