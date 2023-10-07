from time import time

from importer import ImportEngine
from analysis import AnalysisEngine
from reporter import ReportEngine


if __name__ == "__main__":
    start = time()

    imp = ImportEngine()
    imp.load_configurations()
    imp.import_all()
    solves = imp.results

    print(f"Read in {len(solves)} solves in {time() - start:.2f} seconds.")
    print(f"  First solve: {min(t.date for t in solves).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Last solve: {max(t.date for t in solves).strftime('%Y-%m-%d %H:%M:%S')}")

    start = time()
    analysis = AnalysisEngine()
    analysis.load_configurations()
    analysis.attach_results(solves)
    analysis.import_wca_results()
    print(f"Configured analysis in {time() - start:.2f} seconds.")

    start = time()
    analysis.calculate_statistics()
    print(f"Calculated averages in {time() - start:.2f} seconds.")

    start = time()
    rep = ReportEngine()
    rep.load_configurations()
    rep.attach_analysis(analysis)
    rep.generate_all()
    print(f"Generated reports in {time() - start:.2f} seconds.")

    print("Done.")
