from ..base_reporter import BaseReporter

class PBSummaryCSVReporter(BaseReporter):

    def __init__(self):
        super().__init__()
        self.output_file: str = ''

    def generate(self) -> None:
        df = self.analysis.get_dataframe()
        summary = df.groupby('category').min()

        with open(self.output_file, 'w', newline='') as file_stream:
            summary.to_csv(file_stream, index=True, header=True)
