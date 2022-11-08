#!/usr/bin/python3

import os
import re
import json
from datetime import datetime


CSTIMER_EXPORT_FILE_PATTERN = re.compile('^cstimer_')
DATABASE_FOLDER = 'Databases/'
CSVDUMPS_FOLDER = 'CSVDumps/'
RESULTS_FILENAME = 'CSTimerResults.json'


def get_latest_cstimer_export():
    files = os.listdir(DATABASE_FOLDER)
    cstimer_files = [f for f in files if re.match(CSTIMER_EXPORT_FILE_PATTERN, f) is not None]
    cstimer_files.sort()
    return cstimer_files[-1]


def read_cstimer_export(filename):
    with open(filename) as export_file:
        raw_times = json.load(export_file)
    session_properties = json.loads(raw_times['properties']['sessionData'])
    return raw_times, session_properties


def process_raw_results_to_list(raw_data, session_properties):
    all_results = []

    for session in session_properties.keys():
        category = session_properties[session]['name']
        results = raw_data['session' + session]
        if len(results) > 0:
            for result in results:
                penalty = result[0][0]
                time = result[0][1] / 1000
                scramble = result[1]
                timestamp = datetime.utcfromtimestamp(result[3])

                all_results.append([timestamp.isoformat(), category, time, penalty, scramble])
    return all_results


def save_results(all_results, output_filename):
    with open(output_filename, 'w') as output_file:
        json.dump(all_results, output_file)


def load_convert_and_dump_latest_cstimer_export():
    cstimer_export = './' + DATABASE_FOLDER + get_latest_cstimer_export()
    print("Loaded ", cstimer_export)
    
    raw_data, session_properties = read_cstimer_export(cstimer_export)
    all_results = process_raw_results_to_list(raw_data, session_properties)
    
    output_filename = CSVDUMPS_FOLDER + RESULTS_FILENAME
    save_results(all_results, output_filename)
    print("Saved to ", output_filename)


if __name__ == "__main__":
    load_convert_and_dump_latest_cstimer_export()
