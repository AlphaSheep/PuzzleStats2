from typing import Final, Tuple

import requests
from functools import cache
from datetime import datetime, timedelta

from solves import Statistic, StatisticCollection, Result


# Uses the Unofficial WCA API: https://wca-rest-api.robiningelbrecht.be/
WCA_PERSONS_API: Final[str] = "https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/master/api/persons/"
WCA_COMPETITIONS_API: Final[str] = "https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/master/api/competitions/"


@cache
def _fetch_raw_results_for_person(wca_id: str):
    url = f"{WCA_PERSONS_API}{wca_id}.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['results']


@cache
def _fetch_competition_date(comp_id: str) -> datetime:
    url = f"{WCA_COMPETITIONS_API}{comp_id}.json"
    response = requests.get(url)
    response.raise_for_status()

    comp = response.json()
    return datetime.fromisoformat(comp['date']['from'])



def _multi_solve_to_result(solve: int) -> Result:
    missed = solve % 100
    seconds = (solve // 100) % 100000
    difference = 99 - (solve // 10000000)
    solved = difference + missed
    attempted = solved + missed
    return Result((solved, attempted, timedelta(seconds=seconds)))


def _average_to_result(average_raw: int, event_id: str) -> Result:
    if event_id == '333fm':
        average = Result(average_raw/100)
    else:
        average = Result(timedelta(seconds=average_raw/100))
    return average


def _single_to_result(single_raw: int, event_id: str) -> Result:
    if event_id == '333fm':
        result = Result(single_raw)
    elif event_id == '333mbf':
        result = _multi_solve_to_result(single_raw)
    else:
        result = Result(timedelta(seconds=single_raw/100))
    return result


@cache
def get_official_results(wca_id: str) -> Tuple[StatisticCollection, StatisticCollection]:
    results = _fetch_raw_results_for_person(wca_id)
    singles: StatisticCollection = StatisticCollection()
    averages: StatisticCollection = StatisticCollection()

    for comp_id, comp_results in results.items():
        comp_date = _fetch_competition_date(comp_id)
        for event_id, event_results in comp_results.items():
            for round in event_results:

                for solve in round['solves']:
                    if solve <= 0:
                        continue

                    comp_date += timedelta(minutes=1)
                    result = _single_to_result(solve, event_id)
                    singles.append(Statistic(comp_date, result, event_id, 'WCA Single'))


                average_raw = round['average']
                if average_raw > 0:
                    average = _average_to_result(average_raw, event_id)
                    averages.append(Statistic(comp_date, average, event_id, 'WCA Average'))


    return singles, averages
