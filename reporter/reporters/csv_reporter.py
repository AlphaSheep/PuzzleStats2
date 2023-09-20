
from pandas import DataFrame, concat

from ..base_reporter import BaseReporter

class CSVReporter(BaseReporter):
    def __init__(self) -> None:
        self.output_file: str = ''

    def generate(self):

        df: DataFrame = DataFrame()

        for category in self.analysis.get_categories():
            df = concat([df, self.analysis.get_dataframe(category)], axis=0)

        with open(self.output_file, 'w', newline='') as file_stream:
            df.to_csv(file_stream, index=True, header=True, index_label='timestamp')