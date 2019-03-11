import lzma, json, os

def parseJson(jsonData):
    for line in jsonData:
        case = json.loads(str(line, 'utf8'))
        court_name = case['court']['name']
        state_abbrev = case['jurisdiction']['name']
        if state_abbrev == 'Md.' or state_abbrev == 'N.Y.':
            if 'Court of Appeals' not in court_name:
                continue
        elif state_abbrev == 'Okla.' or state_abbrev == 'Tex.':
            if 'Court of Criminal Appeals' not in court_name:
                continue
        else:
            if 'Supreme' not in case['court']['name']:
                continue
        state_name = case['jurisdiction']['name_long']
        court_abbrev = case['court']['name_abbreviation']
        x.add((state_name, court_name, court_abbrev))
    print(x)

def main():
    directoryPath = "/Volumes/Research/Bulk Case Law/"
    directory = os.fsencode(directoryPath)

    x = set([])
    counter = 0
    for dir in os.listdir(directory):
        if counter < 54:
            counter += 1
            continue
        print(dir.decode())
        if dir.decode() == '.DS_Store':
            continue
        subdir = os.fsencode(directoryPath+dir.decode()+'/data/')
        for file in os.listdir(subdir.decode()):
            filename = os.fsdecode(file)
            if not filename.endswith(".xz"):
                continue
            jsonData = lzma.open(subdir.decode() + filename)
            parseJson(jsonData)

main()
