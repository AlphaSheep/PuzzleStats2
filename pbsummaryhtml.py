#!/usr/bin/python3

import re

pbFileName = 'PBSummary.csv'
outputFileName = 'PBSummary/index.html'

openingFile = 'PBSummary/Open.html'
closingFile = 'PBSummary/Close.html'


def readHTML(htmlfilename):
    with open(htmlfilename) as htmlfile:
        html = htmlfile.read();
    return html   
    

def indent(html):
    xxxx = ''
    indentSize = 2
    
    def add():
        nonlocal xxxx
        xxxx += ' '*indentSize
        
    def sub():
        nonlocal xxxx
        xxxx = xxxx[:-indentSize]        
        
    def nullLine(i):
        while i > 0:
            i -= 1
            if html[i] in ' \r':
                pass 
            elif html[i] in '\n':
                return True
            else:
                return False
        return True
        
    intagdef = False
    inendtag = False
        
    i = 0
    while i < len(html):
        if html[i] == '<':
            intagdef = True
            if html[i+1] == '/': # Note - will error if last element is "<"
                inendtag = True
                sub()
                newline = '' if nullLine(i) else '\n'+xxxx+''
                html = html[:i] + newline + html[i:]                
                i += len(newline)
            else:
                newline = '' if nullLine(i) else '\n'+xxxx+''
                html = html[:i] + newline + html[i:]
                i += len(newline)
                add();
                
        elif intagdef and html[i] == '>':
            if inendtag:
                i += 1
                newline = ''
                html = html[:i] + newline + html[i:]
                i += len(newline)-1
            else:
                i += 1
                newline = '\n'+xxxx
                html = html[:i] + newline + html[i:]
                i += len(newline)-1
            intag = False
            inendtag = False
           
        else:
            pass
        i += 1
    return html
            
        

def tag(tagName, attributes, string):
    if type(string) is list:
        string = ''.join(string)
    return '<'+tagName+' '+attributes+'>'+string+'</'+tagName+'>'

def div(string, attributes=''):
    return tag('div', attributes, string)

def table(string, attributes='class="pb-table"'):
    return tag('table', attributes, string)

def thead(string, attributes='class="pb-table-header"'):
    return tag('thead', attributes, string)

def tbody(string, attributes='class="pb-table-body"'):
    return tag('tbody', attributes, string)

def tr(string, attributes='class="pb-table-row pb-table-row-odd"'):
    return tag('tr', attributes, string)

def tr2(string, attributes='class="pb-table-row pb-table-row-even"'):
    return tag('tr', attributes, string)

def th(string, attributes='class="pb-table-header-cell"'):
    return tag('th', attributes, string)

def td(string, attributes='class="pb-table-cell"', extraClasses = None):
    if extraClasses is not None:
        attributes = attributes[:-1] + ' ' + extraClasses + attributes[-1]
    return tag('td', attributes, string)


def generatePbHTML(lastSolveDate=None):
    header = ''
    body = ''

    altrows = 0;

    with open(pbFileName) as pbFile:
        for line in pbFile:
            tra = [tr, tr2]
            row = [cell.strip() for cell in line.split('\t')]
            if row[0] == 'Event':
                header += tra[altrows]([th(cell) for cell in row])
            elif row[0] == 'event':
                columnClassNames = row
            else:
                body += tra[altrows]([td(row[i], extraClasses=columnClassNames[i]) for i in range(len(row))])
            altrows = (altrows+1)%2
    
    
    
    html = table(thead(header) + tbody(body))
    if lastSolveDate is not None:
        datestamp = '<br/>'+div('Last solve date: '+lastSolveDate)
    else:
        datestamp = ''

    opening = readHTML(openingFile)
    closing = readHTML(closingFile)

    with open(outputFileName, 'w') as output:
        regex = re.compile(r"\s+")
        html = regex.sub(' ', opening + html + datestamp + closing)
        output.write(indent(html))


if __name__ == '__main__':
    generatePbHTML()
    
