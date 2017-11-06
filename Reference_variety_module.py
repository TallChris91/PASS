import sys
sys.path.append(r'C:\\Users\\u1269857\\AppData\\Local\\Continuum\\Anaconda3\\Lib\\site-packages')
sys.path.append('C:\\Program Files\\Anaconda3\\Lib\\site-packages')
import xlrd
import re
import numpy

def PlayerReferenceModel(player, soup, homeaway, gap, **kwargs):
    previousgaps = kwargs['previousgaplist']
    previousreference = []
    #Get all the tuples, since these are the previous processed named entities
    for idx, previousgap in enumerate(previousgaps):
        if isinstance(previousgap, tuple):
            #If the named entity is the same as the player of the current event
            if previousgap[0] == player:
                previousreference.append(previousgap[1])
        else:
            #In some cases, the player name is mentioned among others (all the goal scorers, all the players that received a yellow card), this converts the player reference to the form used for these lists and checks if the player has been mentioned in this list
            try:
                fullplayer = soup.find('lineups').find(text=player).parent.parent
            except AttributeError:
                try:
                    fullplayer = soup.find('substitutes').find(text=player).parent.parent
                except AttributeError:
                    try:
                        fullplayer = soup.find('managers').find(text=player).parent.parent
                    except AttributeError:
                        try:
                            fullplayer = soup.find('lineups').find(text=re.compile(player.split()[-1])).parent.parent
                        except AttributeError:
                            try:
                                fullplayer = soup.find('substitutes').find(text=re.compile(player.split()[-1])).parent.parent
                            except AttributeError:
                                try:
                                    fullplayer = soup.find('managers').find(text=re.compile(player.split()[-1])).parent.parent
                                except AttributeError:
                                    print('Named Entity Problem for: ' + player)
                                    sys.exit(1)
            fullplayer = fullplayer.find('name').text
            try:
                if fullplayer in previousgap:
                    previousreference.append(fullplayer)
            except TypeError:
                ''
    #First find the player's information by looking up the player
    manager = 'n'
    try:
        name = soup.find('lineups').find(text=player).parent.parent
    except AttributeError:
        try:
            name = soup.find('substitutes').find(text=player).parent.parent
        except AttributeError:
            try:
                name = soup.find('managers').find(text=player).parent.parent
                manager = 'y'
            except AttributeError:
                try:
                    name = soup.find('lineups').find(['name', 'fullname', 'goalcomshownname'], text=re.compile(player.split()[-1], re.I)).parent.parent
                except AttributeError:
                    try:
                        name = soup.find('substitutes').find(['name', 'fullname', 'goalcomshownname'], text=re.compile(player.split()[-1], re.I)).parent.parent
                    except AttributeError:
                        try:
                            name = soup.find('managers').find(['name', 'fullname', 'goalcomshownname'], text=re.compile(player.split()[-1], re.I)).parent.parent
                            manager = 'y'
                        except AttributeError:
                            print('Named Entity Problem for: ' + player)
                            sys.exit(1)
    #If there is no previous mention of the player, or no recent mention, use one of the following references
    namepossibilities = []
    if (len(previousreference) == 0):
        fullname = name.find('name').text
        namepossibilities.append([fullname, 10])
        splitname = str.split(fullname)
        firstname = None
        lastname = None
        if len(splitname) > 1:
            firstname = splitname[0]
            lastname = ' '.join(splitname[1:])
            if lastname[0].islower():
                lastname = lastname[0].upper() + lastname[1:]
            namepossibilities.append([lastname, 10])
        if manager == 'n':
            position = name.find('wikiposition').text
            if re.search(r'\bgoal', position, re.I):
                if lastname != None:
                    namepossibilities.append(['doelman ' + lastname, 5])
                namepossibilities.append(['doelman ' + fullname, 5])
            elif (re.search(r'back', position, re.I)) or (re.search(r'defender', position, re.I)) or (re.search(r'sweeper', position, re.I)):
                if lastname != None:
                    namepossibilities.append(['verdediger ' + lastname, 5])
                namepossibilities.append(['verdediger ' + fullname, 5])
            elif (re.search(r'midfielder', position, re.I)) or (re.search(r'winger', position, re.I)):
                if lastname != None:
                    namepossibilities.append(['middenvelder ' + lastname, 5])
                namepossibilities.append(['middenvelder ' + fullname, 5])
            elif (re.search(r'forward', position, re.I)) or (re.search(r'striker', position, re.I)) or (re.search(r'attacker', position, re.I)):
                if lastname != None:
                    namepossibilities.append(['aanvaller ' + lastname, 5])
                namepossibilities.append(['aanvaller ' + fullname, 5])
        else:
            if lastname != None:
                namepossibilities.append(['manager ' + lastname, 5])
            namepossibilities.append(['manager ' + fullname, 5])
    #If there was a recent mention of the player, make sure there is a variation to the reference
    if len(previousreference) > 0:
        fullname = name.find('name').text
        if fullname not in previousreference:
            namepossibilities.append([fullname, 10])
        splitname = str.split(fullname)
        firstname = None
        lastname = None
        if len(splitname) > 1:
            firstname = splitname[0]
            lastname = ' '.join(splitname[1:])
            if lastname[0].islower():
                lastname = lastname[0].upper() + lastname[1:]
            if lastname not in previousreference:
                namepossibilities.append([lastname, 10])
        if manager == 'n':
            position = name.find('wikiposition').text
            if re.search(r'\bgoal', position, re.I):
                if lastname != None:
                    if ('doelman ' + lastname) not in previousreference:
                        namepossibilities.append(['doelman ' + lastname, 5])
                if ('doelman ' + fullname) not in previousreference:
                    namepossibilities.append(['doelman ' + fullname, 5])
            elif (re.search(r'back', position, re.I)) or (re.search(r'defender', position, re.I)) or (re.search(r'sweeper', position, re.I)):
                if lastname != None:
                    if ('verdediger ' + lastname) not in previousreference:
                        namepossibilities.append(['verdediger ' + lastname, 5])
                if ('verdediger ' + fullname) not in previousreference:
                    namepossibilities.append(['verdediger ' + fullname, 5])
            elif (re.search(r'midfielder', position, re.I)) or (re.search(r'winger', position, re.I)):
                if lastname != None:
                    if ('middenvelder ' + lastname) not in previousreference:
                        namepossibilities.append(['middenvelder ' + lastname, 5])
                if ('doelman ' + fullname) not in previousreference:
                    namepossibilities.append(['middenvelder ' + fullname, 5])
            elif (re.search(r'forward', position, re.I)) or (re.search(r'striker', position, re.I)) or (re.search(r'attacker', position, re.I)):
                if lastname != None:
                    if ('aanvaller ' + lastname) not in previousreference:
                        namepossibilities.append(['aanvaller ' + lastname, 5])
                if ('aanvaller ' + fullname) not in previousreference:
                    namepossibilities.append(['aanvaller ' + fullname, 5])
        else:
            if lastname != None:
                if ('manager ' + lastname) not in previousreference:
                    namepossibilities.append(['manager ' + lastname, 5])
            if ('manager ' + fullname) not in previousreference:
                namepossibilities.append(['manager ' + fullname, 5])

    elems = [i[0] for i in namepossibilities]
    probs = [i[1] for i in namepossibilities]
    norm = [float(i) / sum(probs) for i in probs]

    namechoice = numpy.random.choice(elems, p=norm)
    nametuple = (player, namechoice)
    return nametuple

def ClubReferenceModel(club, soup, homeaway, gap, **kwargs):
    previousgaps = kwargs['previousgaplist']
    previousreference = []
    # Get all the tuples, since these are the previous processed named entities
    for idx, previousgap in enumerate(previousgaps):
        if isinstance(previousgap, tuple):
            # If the named entity is the same as the club of the current event, save the named entity and how far back the reference was
            if previousgap[0] == club:
                previousreference.append(previousgap[1])
    # If there is no mention of the club in the last sentence, just use the name of the club
    namepossibilities = []
    if (len(previousreference) == 0):
        namepossibilities.append([club, 10])
    else:
        if club not in previousreference:
            namepossibilities.append([club, 50])
        if soup.find('highlights').find('home').find(text=club):
            if 'de thuisploeg' not in previousreference:
                namepossibilities.append(['de thuisploeg', 10])
            try:
                manager = soup.find('managers').find('home').find('name').text
                if ('de ploeg van manager ' + manager) not in previousreference:
                    namepossibilities.append(['de ploeg van manager ' + manager, 10])
            except AttributeError:
                ''
        else:
            if ('de uitploeg') not in previousreference:
                namepossibilities.append(['de uitploeg', 10])
            try:
                manager = soup.find('managers').find('away').find('name').text
                if ('de ploeg van manager ' + manager) not in previousreference:
                    namepossibilities.append(['de ploeg van manager ' + manager, 10])
            except AttributeError:
                ''

        citydict = {}
        workbook = xlrd.open_workbook(r'Clubs and Nicknames.xlsx')
        worksheets = workbook.sheet_names()[0]
        worksheet = workbook.sheet_by_name(worksheets)
        for curr_row in range(worksheet.nrows):
            curr_cell = 1
            excelclub = worksheet.cell_value(curr_row, curr_cell)
            curr_cell = 3
            excelcity = worksheet.cell_value(curr_row, curr_cell)
            citydict.update({excelclub: excelcity})
        if club in citydict:
            if ('de club uit ' + citydict[club]) not in previousreference:
                namepossibilities.append(['de club uit ' + citydict[club], 10])

    elems = [i[0] for i in namepossibilities]
    probs = [i[1] for i in namepossibilities]
    norm = [float(i) / sum(probs) for i in probs]

    namechoice = numpy.random.choice(elems, p=norm)
    nametuple = (club, namechoice)
    return nametuple

#print ClubReferenceModel('Ajax', soup, homeaway, gap, event=event, previousgaplist=previousgaplist)