from ..base_reporter import BaseReporter

class CSVReporter(BaseReporter):

    def __init__(self) -> None:
        super().__init__()
        self.output_file: str = ''

    def generate(self) -> None:
        df = self.analysis.get_dataframe()
        with open(self.output_file, 'w', newline='') as file_stream:
            df.to_csv(file_stream, index=True, header=True)