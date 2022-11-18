from typing import List, TypeVar

from .base_timer_importer import ITimerImporter
from .cstimer import CSTimerImporter
from .plus_timer import PlusTimerImporter
from .fmc_file import FMCFileImporter
from .sct_android_timer import SCTAndroidImporter
from .prisma import PrismaImporter


Importer = TypeVar('Importer', bound=ITimerImporter)


def get_all_importers() -> List[Importer]:
    return [
        CSTimerImporter(),
        PlusTimerImporter(),
        FMCFileImporter(),
        SCTAndroidImporter(),
        PrismaImporter()
    ]

