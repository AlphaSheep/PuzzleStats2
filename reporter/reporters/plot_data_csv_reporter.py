from typing import cast

import os
import shutil

from pandas import DataFrame, concat, DatetimeIndex

from solves import Category
from ..base_reporter import BaseReporter


class PlotDataCSVReporter(BaseReporter):

    def __init__(self):
        super().__init__()
        self.output_folder: str = ''

    def generate(self) -> None:
        self._prepare_output_folder()

        categories = self.analysis.solves.get_distinct_categories()

        for category in categories:
            self._generate_single_for_category(category)
            self._generate_averages_for_category(category)
            self._generate_official_singles_for_category(category)
            self._generate_official_averages_for_category(category)

    def _prepare_output_folder(self) -> None:
        if os.path.exists(self.output_folder):
            shutil.rmtree(self.output_folder)
        os.makedirs(self.output_folder)

    def _generate_single_for_category(self, category: Category) -> None:
        data = self._get_single_data_for_category(category)
        with open(self._get_single_name(category), 'w', newline='', encoding="utf-8") as file_stream:
            data.to_csv(file_stream, index=True, header=True)


    def _get_single_data_for_category(self, category: Category) -> DataFrame:
        solves = self.analysis.solves.filter([category == event for event in self.analysis.solves.category])
        data = DataFrame(solves.as_timeseries().apply(float))

        days = cast(DatetimeIndex, data.index).date
        result = data.groupby(days).apply(_get_daily_summary)
        result.index = result.index.droplevel(0)

        result.index.name = 'timestamp'

        return result

    def _generate_averages_for_category(self, category: Category) -> None:
        date = self._get_averages_data_for_category(category)
        with open(self._get_average_name(category), 'w', newline='', encoding="utf-8") as file_stream:
            date.to_csv(file_stream, index=True, header=True)

    def _get_averages_data_for_category(self, category: Category) -> DataFrame:
        solves = self.analysis.statistics[category]

        result = DataFrame()
        result.index.name = 'timestamp'

        for key, value in solves.items():
            stat = DataFrame(value.as_timeseries().apply(float))
            stat.index.name = 'timestamp'
            stat.columns = [key]
            result = result.join(stat, how='outer')

        return result

    def _generate_official_singles_for_category(self, category: Category) -> None:
        data = self._get_official_singles_data_for_category(category)
        if len(data) > 0:
            with open(self._get_official_singles_name(category), 'w', newline='', encoding="utf-8") as file_stream:
                data.to_csv(file_stream, index=True, header=True)

    def _get_official_singles_data_for_category(self, category: Category) -> DataFrame:
        singles = self.analysis.wca_singles.filter([category == event for event in self.analysis.wca_singles.category])
        result = DataFrame(singles.as_timeseries().apply(float))
        result.index.name = 'timestamp'
        result.columns = ['single']
        return result

    def _generate_official_averages_for_category(self, category: Category) -> None:
        data = self._get_official_averages_data_for_category(category)
        if len(data) > 0:
            with open(self._get_official_averages_name(category), 'w', newline='', encoding="utf-8") as file_stream:
                data.to_csv(file_stream, index=True, header=True)

    def _get_official_averages_data_for_category(self, category: Category) -> DataFrame:
        averages = self.analysis.wca_averages.filter([category == event for event in self.analysis.wca_averages.category])
        result = DataFrame(averages.as_timeseries().apply(float))
        result.index.name = 'timestamp'
        result.columns = ['average']
        return result

    def _get_single_name(self, category: Category) -> str:
        return f"{self.output_folder}/{category}_singles.csv"

    def _get_average_name(self, category: Category) -> str:
        return f"{self.output_folder}/{category}_averages.csv"

    def _get_official_singles_name(self, category: Category) -> str:
        return f"{self.output_folder}/{category}_singles_wca.csv"

    def _get_official_averages_name(self, category: Category) -> str:
        return f"{self.output_folder}/{category}_averages_wca.csv"


def _get_daily_summary(solves: DataFrame) -> DataFrame:
    result = solves

    mean = solves[0].mean()
    std = solves[0].std()
    upper_threshold = mean + 2 * std
    lower_threshold = mean - std

    middle = (solves[0] >= lower_threshold) & (solves[0] <= upper_threshold)

    result['count'] = 1
    result['lower'] = result[0]
    result['upper'] = result[0]

    middle_count = solves[middle][0].count()

    if middle_count > 5:
        result = result.drop(result[middle].index)

        middle_min = solves[middle][0].min()
        middle_max = solves[middle][0].max()
        middle_timestamp = solves[middle].index[-1]

        summary = DataFrame({'lower': [middle_min], 'upper': [middle_max], 'count': [middle_count]}, index=[middle_timestamp])

        result = concat([result, summary])

    result.drop(0, axis=1, inplace=True)

    assert sum(result['count']) == len(solves)

    return result