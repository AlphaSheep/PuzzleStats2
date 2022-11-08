#!/usr/bin/python3

#=======================================================================================================================
# Constants
#=======================================================================================================================

mysqlConnectionDetails = {
    "host": "localhost",
    "user": "root",
    "passwd": "root", 
    "db": "mysql"}

eventConfigFile = 'prismastatconfig.csv'

prismaCsvFiles = [
    'CSVDumps/Prisma_Titan.csv',
    'CSVDumps/Prisma_Iapetus.csv',
    'CSVDumps/Prisma_Encaladus.csv']
androidCSVFiles = [
    'CSVDumps/3 x 3 x 3 Cube - S 11, 2014 - 09.22.25 PM.csv',
    'CSVDumps/2 x 2 x 2 Cube - A 01, 2014 - 11.53.51 AM.csv']
plusTimerCSVFiles = [
    'CSVDumps/PlusTimerResults.csv']
fmcResultsCsvFiles = [
    'CSVDumps/FMCResults.csv']
csTimerResultsFiles = [
    'CSVDumps/CSTimerResults.json']

androidMonthstart = [9,8]
androidcategories = ["Rubik's cube", "2x2x2 cube"] # Correspond to the files in androidCSVFiles

fmcCategories = ['3x3 Fewest Moves'] # Correspond to the files in fmcRsultsCsvFiles

plusTimerCategories = {
    '3x3': "Rubik's cube",
    '3x3-OH': "Rubik's cube one-handed",
    '3x3-Feet': "Rubik's cube with feet",
    '4x4': '4x4x4 cube',
    '5x5': '5x5x5 cube',
    '6x6': '6x6x6 cube',
    '7x7': '7x7x7 cube',
    'Pyraminx': 'Pyraminx',
    'Megaminx': 'Megaminx',
    'Skewb': 'Skewb',
    '3x3-BLD': "Rubik's cube blindfolded",
    'Square-1': 'Square-1',
    'Clock': "Rubik's clock"}


csTimerCategories = {
    '3x3x3 Cube': "Rubik's cube",
    '2x2x2': "2x2x2 cube",
    '4x4x4': "4x4x4 cube",
    '5x5x5': "5x5x5 cube",
    '6x6x6': "6x6x6 cube",
    '7x7x7': "7x7x7 cube",
    'Skewb': "Skewb",
    'Pyraminx': "Pyraminx",
    'Megaminx': "Megaminx",
    'Square-1': "Square-1",
    'FTO': "FTO",
    '3x3 Blindfolded': "Rubik's cube blindfolded",
    'Clock': "Rubik's clock",
    'ZZ One handed': "Rubik's cube one-handed",
    'Roux Practice': "Roux Practice"}




pbSummaryFile = 'PBSummary.csv'
doPBFile = True;

select = "5x5x5 cube"
eventId = '555'

personId = '2014GRAY03'

maxTime = "3:00.00"
minTime = "1:00.00"
secondSpacingMajor = 20
secondSpacingMinor = 2

meanCounts = [1,3,10,25,50,100,250,500,1000,2500,5000,10000,20000,25000]
averageCounts = [5,12,50,100,500,1000,5000,10000]


#=======================================================================================================================
# Imports
#=======================================================================================================================

import sys
import csv
import math
import datetime
import json

import subprocess
import mysql.connector

from bisect import bisect_left, insort
from collections import deque

import matplotlib
matplotlib.use('Agg') # Allows rendering of plots without a running X server (e.g. over ssh)
import pylab

# from mpld3 import fig_to_html

from pbsummaryhtml import generatePbHTML

#=======================================================================================================================
# Loading data from files
#=======================================================================================================================


print('Reading')


allSolutions = []
categories = []
DNFcounts = {} # Dictionary of format {category1: count1, ...}

for csvFile in prismaCsvFiles:
    print('Reading',csvFile)
    source = 'Prisma: ' + csvFile

    with open(csvFile) as thisFile:
        thisCSVFile = csv.reader(thisFile)

        for solution in thisCSVFile:

            if solution[0] == 'SOLUTION_ID':
                continue # Skip header line

            category = solution[10].strip()
            categories.append(category)

            start = datetime.datetime.strptime(solution[4], '%Y-%m-%d %H:%M:%S.%f')
            end = datetime.datetime.strptime(solution[5], '%Y-%m-%d %H:%M:%S.%f')
            try:
                penalty = datetime.timedelta(seconds=int(solution[6]))
            except:
                penalty = datetime.timedelta(seconds=0)

            if solution[6] == 'DNF':
                # Handle DNF penalty
                if category in DNFcounts.keys():
                    DNFcounts[category] += 1
                else:
                    DNFcounts[category] = 1
                # Ignore DNFs in the results, just keep a count
                continue

            time = (end - start) + penalty

            allSolutions.append([start, time, category, penalty, source])


for i in range(len(androidCSVFiles)):
    csvFile = androidCSVFiles[i]
    print('Reading',csvFile)
    source = 'SpeedCube Timer Android: ' + csvFile

    with open(csvFile) as thisFile:
        thisCSVFile = csv.reader(thisFile)

        # Dates from SpeedCube Timer on Android are ambiguous
        # This assumes dates are in reverse chronological order starting from September,
        # all in the same year, and with no months missing, and with the first day of
        # each month less than the last day of the previous month.

        month = androidMonthstart[i]+1

        last = 0
        zerotime = datetime.datetime.strptime('00:00.00', '%M:%S.%f')

        for solution in thisCSVFile:
            if solution[0] == 'Date & Time':
                continue # Skip header line

            if int(solution[0][2:4]) > last:
                month -= 1
            last = int(solution[0][2:4])

            date = solution[0][5:9]+'-'+'{:02d}'.format(month)+'-'+solution[0][2:4]+' '+solution[0][10:]
            start = datetime.datetime.strptime(date, '%Y-%m-%d %I:%M:%S %p')

            time = (datetime.datetime.strptime(solution[1], '%M:%S.%f') - zerotime)

            penalty = datetime.timedelta(seconds=0)

            allSolutions.append([start, time, androidcategories[i].strip(), penalty, source])
            categories.append(androidcategories[i].strip())


for plusTimerCSV in plusTimerCSVFiles:
    print('Reading',plusTimerCSV)
    source = 'Plus Timer Android: ' + plusTimerCSV

    with open(plusTimerCSV) as thisFile:
        thisCSVFile = csv.reader(thisFile)
        for solution in thisCSVFile:
            try:
                start = datetime.datetime.strptime(solution[1], '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                # If the decimal place is .00, then it is left off during the data export, causing a format mismatch
                # Try converting again, but without the decimal.
                start = datetime.datetime.strptime(solution[1], '%Y-%m-%d %H:%M:%S')

            time = datetime.timedelta(seconds=float(solution[2]))
            category = plusTimerCategories[solution[0]].strip()
            if solution[3] == 'DNF':
                # Handle DNF penalty
                if category in DNFcounts.keys():
                    DNFcounts[category] += 1
                else:
                    DNFcounts[category] = 1
                # Ignore DNFs in the results, just keep a count
                continue

            try:
                penalty = datetime.timedelta(seconds=float(solution[3]))
            except:
                penalty = datetime.timedelta(seconds=0)

            allSolutions.append([start, time, category, penalty, source])
            categories.append(category)

for iFile in range(len(fmcResultsCsvFiles)):
    fmcCSV = fmcResultsCsvFiles[iFile]
    category = fmcCategories[iFile].strip()
    categories.append(category)
    print('Reading',fmcCSV)
    source = 'Manual FMC Results: ' + fmcCSV

    with open(fmcCSV) as thisFile:
        thisCSVFile = csv.reader(thisFile)
        for solution in thisCSVFile:
            start = datetime.datetime.strptime(solution[0], '%Y-%m-%d')
            time = datetime.timedelta(seconds=float(solution[1]))
            penalty = datetime.timedelta(seconds=0)
            allSolutions.append([start, time, category, penalty, source])
            categories.append(category)


for cstimerFile in csTimerResultsFiles:
    print('Reading',cstimerFile)
    source = 'cstimer: ' + cstimerFile
    
    with open(cstimerFile) as thisCSTimerFile:
        csTimerResults = json.load(thisCSTimerFile)
    for solution in csTimerResults:
        # [timestamp.isoformat(), category, time, penalty, scramble]
        start = datetime.datetime.strptime(solution[0], '%Y-%m-%dT%H:%M:%S')
        time = datetime.timedelta(seconds=float(solution[2]))
        category = solution[1].strip()
        if category in csTimerCategories:
            category = csTimerCategories[category]
        
        dnf = solution[3]
        if dnf == -1:
            if category in DNFcounts.keys():
                DNFcounts[category] += 1
            else:
                DNFcounts[category] = 1

        penalty = datetime.timedelta(seconds=0)

        allSolutions.append([start, time, category, penalty, source])
        categories.append(category)


#=======================================================================================================================
# Summary
#=======================================================================================================================


uniqueCategories = sorted(list(set(categories)))
print('\nCategories:\n----------\n    '+'\n    '.join(uniqueCategories),'\n')

print('Read in', len(allSolutions), 'solutions\n')

totalTime = datetime.timedelta(seconds=sum([t[1].total_seconds() for t in allSolutions]))
print('Total solve time', str(totalTime), '\n')

firstSolveDate = min([t[0] for t in allSolutions]).strftime('%Y-%m-%d %H:%M:%S')
lastSolveDate = max([t[0] for t in allSolutions]).strftime('%Y-%m-%d %H:%M:%S')

print('First solve:', firstSolveDate)
print('Last solve:', lastSolveDate)

print('\n')

if doPBFile:
    avgColumns = [[ao,'Average of '+str(ao)] for ao in sorted(averageCounts)]
    meanColumns = [[mo, 'Mean of '+str(mo) if mo>1 else 'Single'] for mo in sorted(meanCounts)]
    columns = avgColumns + meanColumns
    avgCodes = ['ao'+str(ao) for ao in sorted(averageCounts)]
    meanCodes = ['mo'+str(mo) if mo>1 else 'single' for mo in sorted(meanCounts)]
    codes = avgCodes + meanCodes

    columnOrder = sorted(list(range(len(columns))), key = lambda x: columns[x][0])
    homeColumns = [columns[i][1] for i in columnOrder]
    codeColumns = [codes[i] for i in columnOrder]

    officialColumns = ['Official Single', 'Official Average']
    officialCodes = ['official-single', 'official-average']

    with open(pbSummaryFile, 'w') as pbFile:
        pbFile.write('\t'.join(['Event', 'Number of Solves'] + officialColumns + homeColumns + ['Total Solve Time']) + '\n')
        pbFile.write('\t'.join(['event', 'numsolves'] + officialCodes + codeColumns + ['total-solve-time']) + '\n')


connection = mysql.connector.connect(**mysqlConnectionDetails)
cursor = connection.cursor()

cursor.execute('SELECT DISTINCT eventId FROM Results;')
allOfficialEvents = [elem for row in cursor.fetchall() for elem in row]
print('Official Category IDs\n---------------------\n    '+'\n    '.join(sorted(allOfficialEvents)),'\n\n')

connection.close()


#=======================================================================================================================
# Save all times to a file
#=======================================================================================================================

def saveSolutions(solutions, categories=None):
    with open('solvetimes.csv', 'w') as solvesFile:
        for solve in solutions:

            start = datetime.datetime.strftime(solve[0], '%Y-%m-%d %H:%M:%S.%f')
            time = str(solve[1].total_seconds())
            category = solve[2]
            penalty = str(solve[3].total_seconds())
            source = solve[4]

            if categories is None or category in categories:
                solvesFile.write(','.join([start, time, category, penalty, source]) + '\n')

        solvesFile.close()


#=======================================================================================================================
# Extract and process times
#=======================================================================================================================

def extractandplot(select, eventId, maxTime, minTime, secondSpacingMajor, secondSpacingMinor, monthSpacingMajor, monthSpacingMinor, officialFormat):

    #=============================================================================================================
    # Exctract data for current event
    #=============================================================================================================

    theseSolutions = [sol for sol in allSolutions if sol[2] == select]
    print('Selected',len(theseSolutions),'solutions for',select)

    theseSolutions.sort(key=lambda x: x[0])

    totalSolveTime = datetime.timedelta(seconds=sum([t[1].total_seconds() for t in theseSolutions]))
    print('Solve time for', select, ':', str(totalSolveTime), '\n')
    #=============================================================================================================
    # Calculate averages
    #=============================================================================================================


    print('Calculating averages for',select)

    def blankListPair():
        return [[None for _ in range(len(theseSolutions))] for _ in range(2)]

    averages = {key:blankListPair() for key in averageCounts}
    means = {key:blankListPair() for key in meanCounts}


    def sumt(times):
        # Special sum for handling timeDeltas
        total = datetime.timedelta(seconds=0)
        for t in times:
            total += t
        return total


    def average(times):
        return (sumt(times)-max(times)-min(times)) / (len(times)-2)


    class MovingMean:
        def __init__(self, size):
            assert type(size) is int and size > 0

            from collections import deque

            self.size = size
            self.values = deque()
            self.sum = None

        def __add__(self, new):
            self.values.append(new)
            if self.sum is None:
                self.sum = new
            else:
                self.sum += new

            if len(self.values) > self.size:
                self.sum -= self.values.popleft()
                return self
            elif len(self.values) == self.size:
                return self
            else:
                return self

        def getMean(self):
            if len(self.values) == self.size:
                return self.sum/self.size
            else:
                return None


    class MovingAverage:

        def __init__(self, size):
            assert type(size) is int and size > 0

            self.size = size

            # Maintain two lists:
            #    values: a queue, in the order that elements are added
            #    sortedValues: a sorted list
            self.values = deque()
            self.sortedValues= []

            self.sum = None

            self.cutoffSize = math.ceil(size / 20) # Ignore top and bottom 5%


        def __add__(self, new):

            self.values.append(new)
            insort(self.sortedValues, new)

            # Add to the sum
            if self.sum is None:
                self.sum = new
            else:
                self.sum += new

            # Manage list size
            if len(self.values) > self.size:
                # List too big

                old = self.values.popleft()
                pos = bisect_left(self.sortedValues, old)
                del self.sortedValues[pos]

                self.sum -= old
            return self


        def getAvg(self):
            if len(self.values) == self.size:
                lower = sumt(self.sortedValues[:self.cutoffSize])
                upper = sumt(self.sortedValues[-self.cutoffSize:])
                middleSum =  (self.sum - lower - upper)
                divisor = (self.size - (2 * self.cutoffSize))
                return middleSum/divisor
            else:
                return None


    meanCounters = {mo:MovingMean(mo) for mo in means.keys()}
    avgCounters = {ao:MovingAverage(ao) for ao in averages.keys()}

    def mean(times):
        return sumt(times) / len(times)

    def pbhist(data):
        pb = [[],[]]
        for i in range(len(data[0])):
            if i>0:
                if data[1][i] > pb[1][-1]:
                    pb[0].append(data[0][i])
                    pb[1].append(pb[1][-1])
                else:
                    pb[0].append(data[0][i])
                    pb[1].append(pb[1][-1])
                    pb[0].append(data[0][i])
                    pb[1].append(data[1][i])
            else:
                pb = [[data[0][i]], [data[1][i]]]
        return pb


    def time2str(time, decimals = 3):
        if decimals == 2:
            time += datetime.timedelta(microseconds=4999)
        timestr = (time + datetime.datetime.strptime('00:00.00', '%M:%S.%f')).strftime('%M:%S.%f')[:-(6-decimals)]
        return timestr.lstrip('0:')


    for i in range(len(theseSolutions)):
        if not i%1000:
            sys.stdout.write('\r        Processed {:.0f}% of solves for '.format(i/len(theseSolutions)*100) + select)
            sys.stdout.flush()
        for ao in averages.keys():
            avgCounters[ao] += theseSolutions[i][1]
            if i+1 >= ao:
                averages[ao][0][i] = theseSolutions[i][0]
                averages[ao][1][i] = avgCounters[ao].getAvg()
        for mo in means.keys():
            meanCounters[mo] += theseSolutions[i][1]
            if i+1 >= mo:
                #times = [sol[1] for sol in theseSolutions[i-mo+1:i+1]]
                means[mo][0][i] = theseSolutions[i][0]
                means[mo][1][i] = meanCounters[mo].getMean()


    sys.stdout.write('\r        Processed 100% of solves for '+select)
    print('\n')

    # Remove padding from beginning
    for ao in averages.keys():
        del(averages[ao][0][:(ao-1)])
        del(averages[ao][1][:(ao-1)])
    for mo in means.keys():
        del(means[mo][0][:(mo-1)])
        del(means[mo][1][:(mo-1)])

    summaryTimeValues = []

    for ao in sorted(averages.keys()):
        if len(averages[ao][1]) > 0:
            thistime = time2str(min(averages[ao][1]))
            print('Best average of {:.0f}: '.format(ao) + thistime)
            summaryTimeValues.append(thistime)
        else:
            summaryTimeValues.append('')
    for mo in sorted(means.keys()):
        if len(means[mo][1]) > 0:
            thistime = time2str(min(means[mo][1]))
            print('Best mean of {:.0f}: '.format(mo) + thistime)
            summaryTimeValues.append(thistime)
        else:
            summaryTimeValues.append('')

    print('\n')

    #=============================================================================================================
    # Fetch Official times
    #=============================================================================================================

    if eventId in allOfficialEvents:
        print('Reading official competition times for',select)

        connection = mysql.connector.connect(**mysqlConnectionDetails)
        cursor = connection.cursor()


        cursor.execute('SELECT DISTINCT eventId FROM Results;')
        allEvents = [elem for row in cursor.fetchall() for elem in row]
        #print('Official Category IDs\n---------------------\n    '+'\n    '.join(sorted(allEvents)),'\n\n')

        sqlQuery = """
        SELECT
            year, month, day, value1, value2, value3, value4, value5
        FROM Results
            LEFT JOIN Competitions
            ON Results.competitionId=Competitions.id
        WHERE personId="1234ABCD01" AND eventId="xxxxx";
        """

        cursor.execute(sqlQuery.replace('1234ABCD01', personId).replace('xxxxx', eventId))
        wcaResults = cursor.fetchall()

        connection.close()
    else:
        print(select, 'is not an official event')
        wcaResults = []


    compdata = [[],[]]
    compAverages = [[],[]]

    for result in wcaResults:
        start = 3
        stop = 8
        if officialFormat in ['mo3', 'mo3fm']:
            stop = 6

        dnfCount = 0

        for i in range(start, stop):
            if result[i]<0:
                dnfCount += 1
            else:
                date = datetime.datetime(result[0],result[1],result[2])
                if officialFormat == 'mo3fm':
                    time = datetime.timedelta(seconds = result[i])
                else:
                    time = datetime.timedelta(seconds = result[i]/100)
                compdata[0].append(date)
                compdata[1].append(time)

        if officialFormat == 'ao5' and dnfCount < 2:
            compAverages[0].append(compdata[0][-1])
            dnfTimes = [datetime.timedelta(seconds = 999999) for _ in range(dnfCount)]
            compAverages[1].append(average(compdata[1][-(5-dnfCount):] + dnfTimes))

        elif officialFormat in ['mo3', 'mo3fm'] and dnfCount < 1:
            compAverages[0].append(compdata[0][-1])
            compAverages[1].append(sumt(compdata[1][-3:])/3)

    if len(compdata[1]) > 0:
        officialPBSingle = time2str(min(compdata[1]), 2)
    else:
        officialPBSingle = ''

    if len(compAverages[1]) > 0:
        officialPBAverage = time2str(min(compAverages[1]), 2)
    else:
        officialPBAverage = ''



    #=============================================================================================================
    # Write to summary file
    #=============================================================================================================

    if doPBFile:
        with open(pbSummaryFile, 'a') as pbFile:
            officialTimes = [officialPBSingle, officialPBAverage]
            homeTimes = [summaryTimeValues[i] for i in columnOrder]
            number = str(len(theseSolutions))
            if select in DNFcounts.keys() and DNFcounts[select] > 0:
                number += ' (DNFs:{:.0f})'.format(DNFcounts[select])
            summaryLine = [select, number] + officialTimes + homeTimes + [str(totalSolveTime)]
            pbFile.write('\t'.join(summaryLine)+'\n')


    #=============================================================================================================
    # Plot the graph
    #=============================================================================================================

    print('Plotting graph for',select)

    def d(datestr):
        return datetime.datetime.strptime(datestr, "%Y-%m-%d")

    def t(timestr):
        return datetime.datetime.strptime(timestr, "%M:%S.%f")

    def val(times):
        zerotime = datetime.datetime.strptime('00:00.00', '%M:%S.%f')
        return list(map(lambda x: zerotime+x, times))


    fig = pylab.figure(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor([.1,.1,.1])

    graylevel = 0.5
    singlecol = [0,1,0]


    # Plot data

    if len(means[1][1])>10000:
        alpha = 0.2
    elif len(means[1][1])>1000:
        alpha = 0.3
    else:
        alpha = 0.8


    pylab.plot(means[1][0], val(means[1][1]),'.',mfc=singlecol, mec=[0,0,0], label="Single times", alpha=alpha)
    pylab.plot(means[100][0], val(means[100][1]),'-', color=[0,1,0], linewidth=3, label="Mean of 100")
    pylab.plot(means[1000][0], val(means[1000][1]),'-', color=[1,0.5,0], linewidth=2, label="Mean of 1000")

    single = pbhist(means[1])
    pylab.plot(single[0], val(single[1]), '-', color=[0,1,.5], linewidth=1, label="Best Single")

    ao5 = pbhist(averages[5])
    pylab.plot(ao5[0], val(ao5[1]), 'b-', linewidth=1, label="PB Avg of 5")

    pylab.plot(compAverages[0], val(compAverages[1]),'s',mfc=[1,0,0], mec="black", markersize=7, label="Official competition averages")
    pylab.plot(compdata[0], val(compdata[1]),'o',mfc=[1,1,0], mec="black", markersize=5, label="Official competition singles")

    # Graph appearance

    pylab.grid('on')
    leg = pylab.legend(loc="upper right", fontsize=9)#, fancybox=True)
    leg.get_frame().set_facecolor([.3,.3,.3])
    leg.get_frame().set_alpha(0.5)
    for text in leg.get_texts():
        text.set_color("white")

    pylab.grid(b=True, which='major', color=[.3,.3,.3], linestyle='-', linewidth=1)
    pylab.grid(b=True, which='minor', color=[.3,.3,.3], linestyle=':')

    ax1 = pylab.gca()
    ax1.set_facecolor([0.05,0.05,0.05])

    ax1.xaxis.set_major_formatter(pylab.DateFormatter('%b %Y'))
    ax1.xaxis.set_major_locator(pylab.MonthLocator(interval=monthSpacingMajor))
    ax1.xaxis.set_minor_formatter(pylab.DateFormatter(''))
    ax1.xaxis.set_minor_locator(pylab.MonthLocator(interval=monthSpacingMinor))

    ax1.yaxis.set_major_formatter(pylab.DateFormatter('%M:%S.00'))
    ax1.yaxis.set_major_locator(pylab.SecondLocator(interval=secondSpacingMajor))
    ax1.yaxis.set_minor_formatter(pylab.DateFormatter(''))
    ax1.yaxis.set_minor_locator(pylab.SecondLocator(interval=secondSpacingMinor))

    dates = single[0] + compdata[0]
    minDate = min(dates) - datetime.timedelta(days=14)
    maxDate = max(dates) + datetime.timedelta(days=14)
    pylab.xlim([minDate, maxDate])

    pylab.ylim([t(minTime),t(maxTime)])


    ax2 = pylab.gcf().add_subplot(111, sharey=ax1, frameon=False)

    ax2.yaxis.tick_right()
    ax2.xaxis.set_ticks([])

    ax1.tick_params(axis='both', which='major', labelsize=9, colors="white")
    ax1.tick_params(axis='both', which='minor', labelsize=9, colors="white")
    ax2.tick_params(axis='both', which='major', labelsize=9, colors="white")
    ax2.tick_params(axis='both', which='minor', labelsize=9, colors="white")


    pylab.title(select+' progress ('+str(len(means[1][1]))+' solves)', color="white")


    print('Saving and displaying graph')
    # fig.savefig('Images/times-'+eventId+'-'+datetime.date.today().strftime('%Y-%m-%d')+'.png', facecolor=fig.get_facecolor(), edgecolor='none')
    fig.savefig('Images/times-'+eventId+'.png', facecolor=fig.get_facecolor(), edgecolor='none')
    # figHtml = fig_to_html(fig);
    
    # with open('Images/times-'+eventId+'.html', 'w') as figHtmlFile:
    #     figHtmlFile.write(figHtml)
    
    # pylab.show()

    pylab.close()
    print('Done.')


def readConfig():
    print('Reading event config from file:', eventConfigFile)
    with open(eventConfigFile) as configFile:
        configCSV = csv.reader(configFile)
        next(configCSV)  # Skip header line.
        inputs = []
        for line in configCSV:
            for i in range(len(line)):
                line[i] = line[i].strip()
                if i in [4,5,6,7]:
                    line[i] = int(line[i])
            inputs.append(line)

        configFile.close()

    print('Read', len(inputs), 'event configurations:')
    for event in inputs:
        print('   ',event)
    print('\n')

    return inputs


def printMissingCategories(allCategories, configuredCategories):
    print('\nCategories missing configuration:')
    for category in allCategories:
        if category not in configuredCategories:
            count = sum([1 for sol in allSolutions if sol[2] == category])
            print('\t'+category, '\t('+str(count)+')')
    

#=======================================================================================================================
# Loop and plot all
#=======================================================================================================================

eventConfig = readConfig()

for args in eventConfig:
    extractandplot(*args)

categories = [event[0] for event in eventConfig]
saveSolutions(allSolutions, categories)

printMissingCategories(uniqueCategories, categories)

generatePbHTML(lastSolveDate)
