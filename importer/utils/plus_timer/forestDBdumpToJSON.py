#!/usr/bin/python3

import re
import json

from datetime import datetime


def readCouchFile():
    couchDumpFileName = 'androidPlusTimer.txt'
    
    data = {}
    
    thisBodyRaw = ''
    isBody = False
    
    with open(couchDumpFileName) as couchFile:
        for line in couchFile:
            line = line.rstrip()
            docId = re.search('(?<=Doc\\sID:\\s)[a-f\d\-]+', line)
            if docId is not None:
                thisID = docId.group(0)
                 
                thisBodyRaw = ''
                isBody = False
                 
            bodyHeader = re.search('Body:\\s\\(hex\\)', line)
            if isBody:
                # Check body first, then switch isBody flag - prevents body header lin from being included.
#                 thisBodyRaw += line[59:]
                thisBodyRaw += line[0:59].strip()+' '
                data[thisID] = thisBodyRaw
            if bodyHeader is not None:
                isBody = True    
            
            
    return data
            

def interpretData(elementRaw):
    try:
        element = re.search('(?<=00)\s*7b\s*(22.*?)??\s*7d\s*(?=00)', elementRaw).group(0).strip()
        element = bytearray.fromhex(element)
        element = element.decode()
        element = json.loads(element)
    except UnicodeDecodeError as err:
        print('\n\n -----     element: |', element, '|\n\n', sep='')
        raise err
    return element


def getTypes(data):
    types = []
    for key, element in data.items():
        if 'type' in element.keys():
            if not element['type'] in types:
                types.append(element['type'])
    print('--TYPES--')
    for t in sorted(types):
        print(t)
    print()
        
        
def isOfType(element, ttype):
    return 'type' in element.keys() and element['type'] == ttype
            
            

data = readCouchFile()
data = {key: interpretData(element) for key, element in data.items()}
     
getTypes(data)

puzzles = {key: element for key, element in data.items() if isOfType(element, 'puzzletype')}
sessions = {key: element for key, element in data.items() if isOfType(element, 'session')}
solves = {key: element for key, element in data.items() if isOfType(element, 'solve')}

print('Puzzles:',len(puzzles))
print('Sessions:',len(sessions))
print('Solves:',len(solves))
print()

allsolves = []

for puzzleKey, puzzle in puzzles.items():
    print(puzzle['name'])
    
    for sessionKey in puzzle['sessions']:
        session = sessions[sessionKey]
#         print('    ',session)
        
        for solveKey in session['solves']:
            solve = solves[solveKey]
            timestamp = datetime.fromtimestamp(solve['timestamp']/1000)  
            time = solve['time']/1e9         
            if solve['penalty'] == 0:
                penalty = ''
            elif solve['penalty'] == 1:
                penalty = '2'
            elif solve['penalty'] == 2:
                penalty = 'DNF'
            else:
                raise Exception('Unrecognised penalty')
            allsolves.append(','.join([puzzle['name'], timestamp.isoformat(' '), str(time), penalty])+'\n')
        
        
with open('../CSVDumps/PlusTimerResults.csv','w') as resultsFile:
    for line in sorted(allsolves):
        resultsFile.write(line)
        

