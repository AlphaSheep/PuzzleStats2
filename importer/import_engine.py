from typing import List, Union, Set, Dict, Any

import json
from jsonschema import validate

from solves import StatisticCollection
from .base_timer_importer import BaseTimerImporter

from .external.cstimer import CSTimerImporter
from .external.plus_timer import PlusTimerImporter
from .external.fmc_file import FMCFileImporter
from .external.sct_android import SCTAndroidImporter
from .external.prisma import PrismaImporter
from .external.cubeast import CubeastImporter


_DEFAULT_CONFIG_FILE = "import_config.json"
_CONFIG_SCHEMA_FILE = "importer/import_config_schema.json"


def get_importer(name: str) -> BaseTimerImporter:
    match name:
        case "cstimer":
            return CSTimerImporter()
        case "prisma":
            return PrismaImporter()
        case "plus_timer":
            return PlusTimerImporter()
        case "sct_android":
            return SCTAndroidImporter()
        case "fmc_file":
            return FMCFileImporter()
        case "cubeast":
            return CubeastImporter()
        case _:
            raise ValueError(f"Unknown importer name: {name}")


class ImportEngine:
    def __init__(self) -> None:
        self._importers: List[BaseTimerImporter] = []

    def load_configurations(self, config_file: str = _DEFAULT_CONFIG_FILE) -> None:
        with open(config_file) as file_stream:
            config = json.load(file_stream)
        _validate_config(config)

        if "imports" in config.keys():
            importers = config["imports"]
            for importer in importers:
                self._configure_and_attach_importer(importer)

    def _configure_and_attach_importer(self, importer_config: Dict[str, Any]) -> None:
        importer: BaseTimerImporter = get_importer(importer_config["engine"])

        match importer_config["type"]:
            case "latest":
                importer.folder = importer_config["folder"]
                importer.pattern = importer_config["pattern"]
            case "files":
                importer.files = importer_config["files"]
        if "categories" in importer_config.keys():
            importer.category_config = importer_config["categories"]
        if "category_map" in importer_config.keys():
            importer.category_config = importer_config["category_map"]
        if "interpret_as_movecount" in importer_config.keys():
            importer.move_categories = importer_config["interpret_as_movecount"]
        if "interpret_as_multi" in importer_config.keys():
            importer.multi_categories = importer_config["interpret_as_multi"]
        if "additional_data" in importer_config.keys():
            importer.additional_data = importer_config["additional_data"]

        self.attach(importer)

    def attach(self, importers: Union[BaseTimerImporter, List[BaseTimerImporter]]) -> None:
        if isinstance(importers, BaseTimerImporter):
            self._importers.append(importers)
        else:
            self._importers += importers

    def import_all(self):
        for imp in self._importers:
            imp.import_all()

    @property
    def results(self) -> StatisticCollection:
        all_solves: StatisticCollection = StatisticCollection()
        imp: BaseTimerImporter
        for imp in self._importers:
            all_solves += imp.solves
        all_solves.sort()
        return all_solves

    @property
    def categories(self) -> Set[str]:
        categories: Set[str] = set()
        imp: BaseTimerImporter
        for imp in self._importers:
            categories = categories.union(imp.categories)
        return categories

    @property
    def dnf_counts(self) -> Dict[str, int]:
        dnf_counts: Dict[str, int] = {}
        imp: BaseTimerImporter
        for imp in self._importers:
            for category in imp.dnf_counts:
                if category in dnf_counts.keys():
                    dnf_counts[category] += imp.dnf_counts[category]
                else:
                    dnf_counts[category] = imp.dnf_counts[category]
        return dnf_counts


def _validate_config(config: Dict[str, Any]):
    with open(_CONFIG_SCHEMA_FILE) as file_stream:
        schema = json.load(file_stream)
    validate(instance=config, schema=schema)
