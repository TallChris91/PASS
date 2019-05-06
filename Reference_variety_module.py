import sys
sys.path.append(r'C:\\Users\\u1269857\\AppData\\Local\\Continuum\\Anaconda3\\Lib\\site-packages')
sys.path.append('C:\\Program Files\\Anaconda3\\Lib\\site-packages')
import xlrd
import re
import numpy

def PlayerReferenceModel(player, jsongamedata, homeaway, gap, **kwargs):
    previousgaps = kwargs['previousgaplist']
    previousreference = []
    #Get all the tuples, since these are the previous processed named entities
    for idx, previousgap in enumerate(previousgaps):
        if isinstance(previousgap, tuple):
            #If the named entity is the same as the player of the current event
            if previousgap[0] == player:
                previousreference.append(previousgap[1])
        else:
            try:
                if player in previousgap:
                    previousreference.append(player)
            except TypeError:
                ''
    #First find the player's information by looking up the player
    for person in jsongamedata['MatchLineup']:
        if (isinstance(player, str) and person['c_Person']==player) or (person==player):
            playerinfo = person
            break

    manager = playerinfo['n_FunctionCode']&16
    
    #If there is no previous mention of the player, or no recent mention, use one of the following references
    namepossibilities = []
    if (len(previousreference) == 0):
        fullname = playerinfo['c_Person']
        namepossibilities.append([fullname, 10])
        firstname = playerinfo['c_PersonFirstName']
        lastname = playerinfo['c_PersonLastName']
        namepossibilities.append([lastname, 10])
        if not manager:
            role = playerinfo['n_FunctionCode']
            if role&1: #keeper
                namepossibilities.append(['doelman ' + lastname, 5])
                namepossibilities.append(['doelman ' + fullname, 5])
            elif role&2: #defender
                namepossibilities.append(['verdediger ' + lastname, 5])
                namepossibilities.append(['verdediger ' + fullname, 5])
            elif role&4: #midfielder
                namepossibilities.append(['middenvelder ' + lastname, 5])
                namepossibilities.append(['middenvelder ' + fullname, 5])
            elif role&8: #attacker
                namepossibilities.append(['aanvaller ' + lastname, 5])
                namepossibilities.append(['aanvaller ' + fullname, 5])
        else:
            namepossibilities.append(['manager ' + lastname, 5])
            namepossibilities.append(['manager ' + fullname, 5])
    #If there was a recent mention of the player, make sure there is a variation to the reference
    if len(previousreference) > 0:
        fullname = playerinfo['c_Person']
        if fullname not in previousreference:
            namepossibilities.append([fullname, 10])
        splitname = str.split(fullname)
        firstname = playerinfo['c_PersonFirstName']
        lastname = playerinfo['c_PersonLastName']
        namepossibilities.append([lastname, 10])
        if not manager:
            role = playerinfo['n_FunctionCode']
            if role&1: #keeper
                if ('doelman ' + lastname) not in previousreference:
                    namepossibilities.append(['doelman ' + lastname, 5])
                if ('doelman ' + fullname) not in previousreference:
                    namepossibilities.append(['doelman ' + fullname, 5])
            elif role&2: #defender
                if ('verdediger ' + lastname) not in previousreference:
                    namepossibilities.append(['verdediger ' + lastname, 5])
                if ('verdediger ' + fullname) not in previousreference:
                    namepossibilities.append(['verdediger ' + fullname, 5])
            elif role&4: #midfielder
                if ('middenvelder ' + lastname) not in previousreference:
                    namepossibilities.append(['middenvelder ' + lastname, 5])
                if ('doelman ' + fullname) not in previousreference:
                    namepossibilities.append(['middenvelder ' + fullname, 5])
            elif role&8: #attacker
                if ('aanvaller ' + lastname) not in previousreference:
                    namepossibilities.append(['aanvaller ' + lastname, 5])
                if ('aanvaller ' + fullname) not in previousreference:
                    namepossibilities.append(['aanvaller ' + fullname, 5])
        else:
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

def ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs):
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
        if jsongamedata['MatchInfo'][0]['c_HomeTeam']==club:
            if 'de thuisploeg' not in previousreference:
                namepossibilities.append(['de thuisploeg', 10])
            for person in jsongamedata['MatchLineup']:
                if person['n_FunctionCode']&16 and person['n_HomeOrAway']==1:
                    manager = person['c_Person']
                    break
            if ('de ploeg van manager ' + manager) not in previousreference:
                namepossibilities.append(['de ploeg van manager ' + manager, 10])
        else:
            if ('de uitploeg') not in previousreference:
                namepossibilities.append(['de uitploeg', 10])
            for person in jsongamedata['MatchLineup']:
                if person['n_FunctionCode']&16 and person['n_HomeOrAway']==-1:
                    manager = person['c_Person']
                    break
            if ('de ploeg van manager ' + manager) not in previousreference:
                    namepossibilities.append(['de ploeg van manager ' + manager, 10])
            if ('de ploeg van manager ' + manager) not in previousreference:
                namepossibilities.append(['de ploeg van manager ' + manager, 10])

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

#print ClubReferenceModel('Ajax', jsongamedata, homeaway, gap, event=event, previousgaplist=previousgaplist)