import lzma, json, os
import string
import xlsxwriter
import re
from highCourts import courts

def initSheet(sheet):
    sheet.write('A1','citing state') # case['jurisdiction']['name']
    sheet.write('B1','cited state') # court['name']
    sheet.write('C1','citing state case citation') # case['citations'][0]['cite'] # maybe find official one 'type'='official'
    sheet.write('D1','citing state case name') # case['name']
    sheet.write('E1','cited state opinion citation')
    sheet.write('F1','cited state case name')
    sheet.write('G1','citing case court name')  #case['court']['name_abbreviation']
    sheet.write('H1','cited case court name') # court["acronym"]
    sheet.write('I1','citing state case decision year') #case['decision_date'] # formatted 2000-02-10
    sheet.write('J1','cited state case decision year') # how?
    return sheet

def getCitation(opinion, index):
    endIndex = index
    while not opinion[endIndex].isdigit():
        endIndex += 1
    while opinion[endIndex].isdigit():
        endIndex += 1
    startIndex = index
    while not opinion[startIndex].isdigit():
        startIndex -= 1
    while opinion[startIndex].isdigit():
        startIndex -= 1
    return opinion[startIndex+1:endIndex]

def getName(opinion, index):
    endIndex = index
    while opinion[endIndex] != ',':
        endIndex -= 1
    startIndex = endIndex
    while opinion[startIndex:startIndex+2] != 'v.':
        if index - startIndex > 100:
            return ''
        startIndex -= 1
    lastCapital = startIndex;
    while True:
        if index - startIndex > 200:
            return ''
        startIndex -=1
        if opinion[startIndex].isupper():
            lastCapital = startIndex
        if opinion[startIndex].islower() and opinion[startIndex-1] == ' ' or opinion[startIndex] in string.punctuation:
            break;
    return opinion[lastCapital:endIndex].strip()

def fastFindIndices(pattern, text):
    matches = []
    reMatches = re.finditer(pattern, text)
    if reMatches:

        for match in reMatches:
            matches.append(match[0])
    return matches

def findCitations(count, sheet, case, opinion):
    for court in courts:
        acr = court['name']
        matches = fastFindIndices(acr, opinion)
        for match in matches:
            if opinion[match].isdigit() and not opinion[match - 1] == '.':
                jurisdiction = case['jurisdiction']['name']
                print(f'Parsing citation {count} from {jurisdiction}')
                sheet.write(f'A{count}', jurisdiction)
                sheet.write(f'B{count}', acr)
                sheet.write(f'C{count}', case['citations'][0]['cite'])
                sheet.write(f'D{count}', case['name'])
                sheet.write(f'E{count}', getName(opinion, match))
                sheet.write(f'F{count}', getCitation(opinion, match))
                sheet.write(f'G{count}', case['court']['name_abbreviation'])
                sheet.write(f'H{count}', court["acronym"])
                sheet.write(f'I{count}', case['decision_date'].split('-')[0])
                count += 1
                if count > 20:
                    return count
    return count

def parseCases(sheet, jsonData):
    count = 2
    for line in jsonData:
        if count > 20:
            return
       # if count % 10 == 0:
        case = json.loads(str(line, 'utf8'))
        state = case['jurisdiction']['name']
        for opinion in case['casebody']['data']['opinions']:
            count = findCitations(count, sheet, case, str(opinion))

def main():
    wb = xlsxwriter.Workbook('data.xlsx')
    directoryPath = "/Volumes/Research/Bulk Case Law/"
    directory = os.fsencode(directoryPath)
    for dir in os.listdir(directory):
        if dir.decode() == '.DS_Store':
            continue
        subdir = os.fsencode(directoryPath+dir.decode()+'/data/')
        for file in os.listdir(subdir.decode()):
            filename = os.fsdecode(file)
            if not filename.endswith(".xz"):
                continue
            jsonData = lzma.open(subdir.decode() + filename)
            sheet = wb.add_worksheet(dir.decode())
            initSheet(sheet)
            parseCases(sheet, jsonData)
    wb.close()
    return

main()
