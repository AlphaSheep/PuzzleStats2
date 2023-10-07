from typing import Final, List, Dict, Any, Callable, Set

import json
from jsonschema import validate
from datetime import datetime
from pandas import DataFrame, concat

from solves import StatisticCollection, Statistic, Category
from wca import get_official_results

from .aggregations import MovingMeanWindow, MovingAverageWindow, BaseMovingWindow, Aggregation
from .simplification import simplify


_DEFAULT_CONFIG_FILE: Final[str] = "analysis_config.json"
_CONFIG_SCHEMA_FILE: Final[str] = "analysis/analysis_config_schema.json"


class AnalysisEngine():

    def __init__(self) -> None:
        self.averages_config: List[int] = []
        self.means_config: List[int] = []

        self.include_wca: bool = False
        self.wca_id: str = ''

        self.solves: StatisticCollection = StatisticCollection()
        self.statistics: Dict[Category, Dict[Aggregation, StatisticCollection]] = {}
        self.wca_singles: StatisticCollection = StatisticCollection()
        self.wca_averages: StatisticCollection = StatisticCollection()

    def load_configurations(self, config_file: str = _DEFAULT_CONFIG_FILE) -> None:
        with open(config_file, encoding="utf-8") as file_stream:
            config = json.load(file_stream)
        _validate_config(config)

        self.means_config = config["means"]
        self.averages_config = config["averages"]

        if "wca" in config:
            self.include_wca = config["wca"]["include"]
            if "wca_id" in config["wca"]:
                self.wca_id = config["wca"]["wca_id"]

        if self.include_wca and not self.wca_id:
            raise ValueError("WCA ID must be included in config if WCA results are to be included.")


    def attach_results(self, solves: StatisticCollection) -> None:
        self.solves = solves

    def import_wca_results(self) -> None:
        if not self.include_wca:
            return
        singles, averages = get_official_results(self.wca_id)
        self.wca_singles = singles
        self.wca_averages = averages

    def calculate_statistics(self) -> None:
        self._calculate_means()
        self._calculate_averages()

    def _calculate_means(self) -> None:
        self._calculate_generic_statistic(MovingMeanWindow, self.means_config, "mo")

    def _calculate_averages(self) -> None:
        self._calculate_generic_statistic(MovingAverageWindow, self.averages_config, "ao")

    def _calculate_generic_statistic(self, Window: Callable[[int], BaseMovingWindow], config: List[int], keyPrefix: str) -> None:
        for event in self.solves.get_distinct_categories():
            theseSolves = self.solves.filter([category == event for category in self.solves.category])
            if not event in self.statistics.keys():
                self.statistics[event] = {}

            dates = theseSolves.date
            sources = ["Analysis Engine" for _ in theseSolves.source]

            for mean_of_size in config:
                if len(theseSolves) < mean_of_size:
                    continue
                mean_key = Aggregation(f"{keyPrefix}{mean_of_size}")
                means = _calculate_single_statistic(
                    theseSolves,
                    mean_of_size,
                    mean_key,
                    Window,
                    dates,
                    sources
                )

                self.statistics[event][mean_key] = simplify(means)

    def get_categories(self) -> Set[Category]:
        categories = self.solves.get_distinct_categories()
        if self.include_wca:
            categories = categories.union(self.wca_singles.get_distinct_categories())
            categories = categories.union(self.wca_averages.get_distinct_categories())
        return categories

    def get_dataframe_for_category(self, selected_category: str) -> DataFrame:
        solves = self.solves.filter([category == selected_category for category in self.solves.category])
        df = DataFrame({'single': solves.as_timeseries()})
        df.index.name = 'timestamp'

        if self.include_wca:
            singles = self.wca_singles.filter([category == selected_category for category in self.wca_singles.category])
            for date in singles.date:
                df.loc[(date,)] = float('nan')

            df['wca_single'] = singles.as_timeseries()
            averages = self.wca_averages.filter([category == selected_category for category in self.wca_averages.category])
            df['wca_average'] = averages.as_timeseries()

        if selected_category in self.statistics.keys():
            for key, stats in self.statistics[Category(selected_category)].items():
                df[key] = stats.as_timeseries()

        df.sort_index(inplace=True)

        df.insert(0, 'category', selected_category)
        df.set_index('category', append=True, inplace=True)

        return df

    def get_dataframe(self) -> DataFrame:
        df: DataFrame = DataFrame()
        for category in self.get_categories():
            df = concat([df, self.get_dataframe_for_category(category)], axis=0)
        return df



def _validate_config(config: Dict[str, Any]):
    with open(_CONFIG_SCHEMA_FILE, encoding="utf-8") as file_stream:
        schema = json.load(file_stream)
    validate(instance=config, schema=schema)


def _calculate_single_statistic(
        solves: StatisticCollection,
        mean_of_size: int,
        mean_key: str,
        Window: Callable[[int], BaseMovingWindow],
        dates: List[datetime],
        sources: List[str]
    ):

    calculator = Window(mean_of_size)

    means = calculator.calculate(solves.result)
    categories = [Category(f"{category} {mean_key}") for category in solves.category]

    return StatisticCollection([
        Statistic(date, mean, category, source) \
        for date, mean, category, source in zip(dates, means, categories, sources) \
        if mean.has_result()
    ])
