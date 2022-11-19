from typing import List, TypeVar, Union, Set, Dict

from result import Result
from .base_timer_importer import ITimerImporter
from .cstimer import CSTimerImporter
from .plus_timer import PlusTimerImporter
from .fmc_file import FMCFileImporter
from .sct_android_timer import SCTAndroidImporter
from .prisma import PrismaImporter


Importer = TypeVar('Importer', bound=ITimerImporter)


class ImportEngine:
    def __init__(self):
        self._importers: List[Importer] = []

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


def get_all_importers() -> List[Importer]:
    return [
        CSTimerImporter(),
        PlusTimerImporter(),
        FMCFileImporter(),
        SCTAndroidImporter(),
        PrismaImporter()
    ]

