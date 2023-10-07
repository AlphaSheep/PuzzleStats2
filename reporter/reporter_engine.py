from typing import List

import json
from jsonschema import validate

from analysis import AnalysisEngine

from .base_reporter import BaseReporter
from .reporters import CSVReporter, PBSummaryCSVReporter, JSONReporter, PlotDataCSVReporter


_DEFAULT_CONFIG_FILE = "report_config.json"
_CONFIG_SCHEMA_FILE = "reporter/report_config_schema.json"


def get_reporter(name: str) -> BaseReporter:
    match name:
        case "csv":
            return CSVReporter()
        case "pb_summary_csv":
            return PBSummaryCSVReporter()
        case "json":
            return JSONReporter()
        case "plot_data_csv":
            return PlotDataCSVReporter()
    raise ValueError(f"Unknown reporter name: {name}")


class ReportEngine:

    def __init__(self) -> None:
        self.reporters: List[BaseReporter] = []

    def load_configurations(self, config_file: str = _DEFAULT_CONFIG_FILE) -> None:
        with open(config_file) as file_stream:
            config = json.load(file_stream)
        _validate_config(config)

        reporters = config["reporters"]
        for reporter in reporters:
            self._configure_and_attach_reporter(reporter)

    def _configure_and_attach_reporter(self, reporter_config: dict) -> None:
        reporter: BaseReporter = get_reporter(reporter_config["engine"])

        match reporter_config["type"]:
            case "file":
                reporter.output_file = reporter_config["output_file"]
            case "folder":
                reporter.output_folder = reporter_config["output_folder"]

        self.reporters.append(reporter)

    def attach_analysis(self, analysis: AnalysisEngine) -> None:
        for reporter in self.reporters:
            reporter.attach_analysis(analysis)

    def generate_all(self):
        for reporter in self.reporters:
            reporter.generate()


def _validate_config(config: dict) -> None:
    with open(_CONFIG_SCHEMA_FILE) as file_stream:
        schema = json.load(file_stream)
    validate(instance=config, schema=schema)