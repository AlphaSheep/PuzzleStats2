import json
from typing import List, TypeVar, Union, Set, Dict, Any
from jsonschema import validate

from result import Result
from .base_timer_importer import ITimerImporter
from .cstimer import CSTimerImporter
from .plus_timer import PlusTimerImporter
from .fmc_file import FMCFileImporter
from .sct_android import SCTAndroidImporter
from .prisma import PrismaImporter


Importer = TypeVar('Importer', bound=ITimerImporter)


DEFAULT_CONFIG_FILE = "import_config.json"
CONFIG_SCHEMA_FILE = "importer/config_schema.json"


def get_importer(name: str) -> Importer:
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


def validate_config(config: Dict[str, Any]):
    with open(CONFIG_SCHEMA_FILE) as file_stream:
        schema = json.load(file_stream)
    validate(instance=config, schema=schema)


class ImportEngine:
    def __init__(self):
        self._importers: List[Importer] = []

    def load_configurations(self, config_file: str = DEFAULT_CONFIG_FILE) -> None:
        with open(config_file) as file_stream:
            config = json.load(file_stream)
        validate_config(config)

        if "imports" in config.keys():
            importers = config["imports"]
            for importer in importers:
                self._configure_and_attach_importer(importer)

    def _configure_and_attach_importer(self, importer_config: Dict[str, Any]) -> None:
        importer: Importer = get_importer(importer_config["engine"])

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

        self.attach(importer)

    def attach(self, importers: Union[Importer, List[Importer]]) -> None:
        if type(importers) is list:
            self._importers += importers
        else:
            self._importers.append(importers)

    def import_all(self):
        for imp in self._importers:
            imp.import_all()

    @property
    def results(self) -> List[Result]:
        all_results: List[Result] = []
        imp: Importer
        for imp in self._importers:
            all_results += imp.results
        return all_results

    @property
    def categories(self) -> Set[str]:
        categories: Set[str] = set()
        imp: Importer
        for imp in self._importers:
            categories = categories.union(imp.categories)
        return categories

    @property
    def dnf_counts(self) -> Dict[str, int]:
        dnf_counts: Dict[str, int] = {}
        imp: Importer
        for imp in self._importers:
            for category in imp.dnf_counts:
                if category in dnf_counts.keys():
                    dnf_counts[category] += imp.dnf_counts[category]
                else:
                    dnf_counts[category] = imp.dnf_counts[category]
        return dnf_counts
