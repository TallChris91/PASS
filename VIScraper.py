from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import os.path
import time
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import regex as re
from datetime import date
from lxml import etree
import sys


def query(query, currentpath):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-infobars")
    try:
        driver = webdriver.Chrome(currentpath + '/chromedriver')
    except OSError:
        driver = webdriver.Chrome(currentpath + '/chromedriver.exe')
    while True:
        try:
            driver.get(query)
            break
        except:
            ''
    driver.find_element_by_xpath('//form').click()
    page_source = driver.page_source
    driver.close()
    root = BeautifulSoup(page_source, "lxml")
    return root

def findmatches(root):
    datedict = {'jan': 1, 'feb': 2, 'mrt': 3, 'apr': 4, 'mei': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'dec': 12}
    soccermatches = root.find_all('div', {"class": "c-match-overview"})
    differencelist = []
    for soccermatch in soccermatches:
        datepart = soccermatch.find('h4', {"class": "c-match-overview__title"})
        matchdate = re.sub(r'^(.*?)\s', '', datepart.text)
        matchdate = matchdate.split(' ')
        matchdate[1] = datedict[matchdate[1]]
        currentdate = time.strftime("%d/%m/%Y")
        currentdate = currentdate.split('/')
        curr = date(int(currentdate[2]), int(currentdate[1]), int(currentdate[0]))
        match = date(int(currentdate[2]), int(matchdate[1]), int(matchdate[0]))

        difference = curr - match
        difference = difference.days
        if difference < 0:
            match = date(int(currentdate[2])-1, int(matchdate[1]), int(matchdate[0]))
            difference = curr - match
            difference = difference.days

        differencelist.append(difference)

    sortedindexes = sorted(range(len(differencelist)), key=lambda i: differencelist[i])
    matcheslist = []
    for sortedindex in sortedindexes:
        matchparts = soccermatches[sortedindex].find_all('li', {"class": "c-striped-list__item c-bordered-list__item c-match-overview__item o-faux-link"})
        for matchpart in matchparts:
            if matchpart.find('div', {"class": "c-fixture__score c-fixture__score--home"}).text == '-':
                continue
            weblink = matchpart.find('a', {"class": "o-faux-link__item c-match-overview__link"})
            weblink = 'https://www.vi.nl' + weblink['href']
            matcheslist.append(weblink)
        if len(matcheslist) >= 10:
            break
    return matcheslist

def isowngoal(player, minute, matchroot):
    events = matchroot.find('ul', {"class": "c-events-list c-events-list--large"})
    eventslist = events.find_all('li')
    for event in eventslist:
        eventplayer = event.find('div', {"class": "c-events-list__player-name"}).text.strip()
        eventminute = event.find('div', {"class": "c-events-list__time"}).text.strip()
        eventminute = re.search(r'\d+', eventminute).group()
        if (player == eventplayer) and (minute == eventminute):
            if event.find('svg')['class'][2] == 'icon-goal':
                return 'n'
            if event.find('svg')['class'][2] == 'icon-goal--own':
                return 'y'


def highlightspart(matchroot):
    datedict = {'januari': 'January', 'februari': 'February', 'maart': 'March', 'april': 'April', 'mei': 'May', 'juni': 'June', 'juli': 'July', 'augustus': 'August', 'september': 'September', 'oktober': 'October', 'november': 'November', 'december': 'December'}
    league = matchroot.find('li', {"class": "o-list-inline__item c-label-list__item"}).text.strip()
    time = matchroot.find('time').text.strip()
    date = re.search(r'^(.*?),', time).group(1)
    date = date.split(' ')
    date[1] = datedict[date[1]]
    datestring = date[1] + ' ' + date[0] + ', ' + date[2]
    clocktime = re.search(r',(.*?)$', time).group(1)
    clocktime = re.sub(r'uur', '', clocktime).strip()
    clocktime = re.sub(r'\.', ':', clocktime)
    city = ''
    stadiumrefattendees = matchroot.find('dl', {"class": "o-layout o-layout--flush c-definition-list"}).text.strip()
    stadiumrefattendees = re.sub(r':\s+', ': ', stadiumrefattendees)
    stadiumrefattendees = re.sub(r'\s{2,}', '; ', stadiumrefattendees)
    stadium = re.search(r"Stadion: (.*?)(;|$)", stadiumrefattendees).group(1)
    if stadium == 'Niet beschikbaar':
        stadium = ''
    ref = re.search(r"Scheidsrechter: (.*?)(;|$)", stadiumrefattendees).group(1)
    if ref == 'Niet beschikbaar':
        ref = ''
    attendees = re.search(r"Toeschouwers: (.*?)(;|$)", stadiumrefattendees).group(1)
    if attendees == 'Niet beschikbaar':
        attendees = ''
    fulltimescore = matchroot.find('div', {"class": "c-match-header__score"}).text.strip()
    fulltimescore = re.sub(r' - ', '-', fulltimescore)
    hometeam = matchroot.find('div', {"class": "c-match-header__team c-match-header__team--home"}).text.strip()
    finalhomegoals, finalawaygoals = fulltimescore.split('-')
    awayteam = matchroot.find('div', {"class": "c-match-header__team c-match-header__team--away"}).text.strip()
    matchevents = matchroot.find('div', {"class": "c-match-events c-match-events--box"})
    homegoalscorerslist = []
    homegoalslist = matchevents.find_all('li', {"class": "c-events-list__item c-events-list__item--home"})[::-1]
    for idx, homegoal in enumerate(homegoalslist):
        player = homegoal.find('a').text.strip()
        goalid = str(idx+1)
        minute = homegoal.find('div', {"class": "c-events-list__time"}).text.strip()
        minute = re.search('\d+', minute).group()
        playerlink = homegoal.find('a')['href']
        playerlink = 'https://www.vi.nl' + playerlink
        owngoal = isowngoal(player, minute, matchroot)
        homegoalscorerslist.append((goalid, minute, playerlink, owngoal, player))

    awaygoalscorerslist = []
    awaygoalslist = matchevents.find_all('li', {"class": "c-events-list__item c-events-list__item--away"})[::-1]
    for idx, awaygoal in enumerate(awaygoalslist):
        player = awaygoal.find('a').text.strip()
        goalid = str(idx+1)
        minute = awaygoal.find('div', {"class": "c-events-list__time"}).text.strip()
        minute = re.search('\d+', minute).group()
        playerlink = awaygoal.find('a')['href']
        playerlink = 'https://www.vi.nl' + playerlink
        owngoal = isowngoal(player, minute, matchroot)
        awaygoalscorerslist.append((goalid, minute, playerlink, owngoal, player))

    return league, datestring, clocktime, stadium, city, ref, attendees, fulltimescore, hometeam, homegoalscorerslist, finalhomegoals, awayteam, awaygoalscorerslist, finalawaygoals

def eventspart(matchroot):
    events = matchroot.find('ul', {"class": "c-events-list c-events-list--large"})
    eventslist = events.find_all('li')[::-1]
    assistlist = []
    goallist = []
    missedpenaltylist = []
    penaltygoallist = []
    redcardlist = []
    yellowcardlist = []
    yellowredlist = []
    owngoallist = []
    substitutionlist = []
    for event in eventslist:
        eventminute = event.find('div', {"class": "c-events-list__time"}).text.strip()
        eventminute = re.search('\d+', eventminute).group()
        if event.find('svg')['class'][2] == 'icon-goal':
            try:
                assistplayer = event.find('div', {"class": "c-events-list__player-name c-events-list__player-name--related"}).find('a').text.strip()
                assistlist.append((str(len(assistlist)+1), eventminute, assistplayer))
            except AttributeError:
                ''
            eventplayer = event.find('div', {"class": "c-events-list__player-name"}).text.strip()
            goallist.append((str(len(goallist)+1), eventminute, eventplayer))
        if event.find('svg')['class'][2] == 'icon-penalty--missed':
            eventplayer = event.find('div', {"class": "c-events-list__player-name"}).text.strip()
            missedpenaltylist.append((str(len(missedpenaltylist) + 1), eventminute, eventplayer))
        if event.find('svg')['class'][2] == 'icon-penalty':
            eventplayer = event.find('div', {"class": "c-events-list__player-name"}).text.strip()
            penaltygoallist.append((str(len(penaltygoallist) + 1), eventminute, eventplayer))
        if event.find('svg')['class'][2] == 'icon-card--red':
            eventplayer = event.find('div', {"class": "c-events-list__player-name"}).text.strip()
            redcardlist.append((str(len(redcardlist) + 1), eventminute, eventplayer))
        if event.find('svg')['class'][2] == 'icon-card--yellow':
            eventplayer = event.find('div', {"class": "c-events-list__player-name"}).text.strip()
            yellowcardlist.append((str(len(yellowcardlist) + 1), eventminute, eventplayer))
        if event.find('svg')['class'][2] == 'icon-card--yellow-red':
            eventplayer = event.find('div', {"class": "c-events-list__player-name"}).text.strip()
            yellowredlist.append((str(len(yellowredlist) + 1), eventminute, eventplayer))
        if event.find('svg')['class'][2] == 'icon-goal--own':
            eventplayer = event.find('div', {"class": "c-events-list__player-name"}).text.strip()
            owngoallist.append((str(len(owngoallist) + 1), eventminute, eventplayer))
        if event.find('svg')['class'][2] == 'icon-substitution':
            suboutplayer = event.find('div', {"class": "c-events-list__player-name c-events-list__player-name--related"}).find('a').text.strip()
            subinplayer = event.find('div', {"class": "c-events-list__player-name"}).text.strip()
            substitutionlist.append((str(len(owngoallist) + 1), eventminute, suboutplayer, subinplayer))
    return assistlist, goallist, missedpenaltylist, penaltygoallist, redcardlist, yellowcardlist, yellowredlist, owngoallist, substitutionlist

def playerinfo(playerlink, currentpath):
    playerroot = query(playerlink, currentpath)
    time.sleep(1)
    #infile = open(currentpath + '/PlayerTest.xml', "rb")
    #contents = infile.read()
    #infile.close()
    #playerroot = BeautifulSoup(contents, "xml")
    playerinfopart = playerroot.find('div', {"class": "o-layout__item u-9/12@md u-9/12@lg"}).text.strip()
    playerinfopart = re.sub(r':\s+', ': ', playerinfopart)
    playerinfopart = re.sub(r'\s{2,}', '; ', playerinfopart)
    playerinfopart = re.sub(r'\n', '; ', playerinfopart)
    playerinfopart = playerinfopart.split('; ')
    for idx, pip in enumerate(playerinfopart):
        if not (':' in playerinfopart[idx]) and not (':' in playerinfopart[idx+1]):
            playerinfopart[idx] = playerinfopart[idx] + ': ' + playerinfopart[idx+1]
            playerinfopart[idx + 1] = ''
    playerinfopart = '; '.join(playerinfopart)
    playerinfopart = re.sub(r'\n', '; ', playerinfopart)
    try:
        firstname = re.search(r"Voornaam: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        firstname = ''
    try:
        lastname = re.search(r"Achternaam: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        lastname = ''

    fullname = firstname + " " + lastname
    try:
        birthdate = re.search(r"Geboortedatum: (.*?)(;|$)", playerinfopart).group(1)
        datedict = {'januari': 'January', 'februari': 'February', 'maart': 'March', 'april': 'April', 'mei': 'May', 'juni': 'June', 'juli': 'July',
                    'augustus': 'August', 'september': 'September', 'oktober': 'October', 'november': 'November', 'december': 'December'}
        birthdate = birthdate.split(' ')
        birthdate[1] = datedict[birthdate[1]]
        birthdate = birthdate[1] + ' ' + birthdate[0] + ', ' + birthdate[2]
    except AttributeError:
        birthdate = ''
    try:
        age = re.search(r"Leeftijd: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        age = ''
    try:
        birthplace = re.search(r"Geboorteplaats: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        birthplace = ''
    try:
        nationality = re.search(r"Nationaliteit: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        nationality = ''
    try:
        height = re.search(r"Lengte: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        height = ''
    try:
        weight = re.search(r"Gewicht: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        weight = ''
    try:
        preferredfoot = re.search(r"Voet: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        preferredfoot = ''
    try:
        currentclub = re.search(r"Huidige club: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        currentclub = ''
    try:
        yearswithclub = re.search(r"Actief bij club: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        yearswithclub = ''
    yearswithclub = re.sub(r" - nu", "-", yearswithclub)
    try:
        currentleague = re.search(r"Actief in: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        currentleague = ''
    try:
        position = re.search(r"Positie: (.*?)(;|$)", playerinfopart).group(1)
        if position == 'Keeper':
            position = 'Goalkeeper'
        if position == 'Verdediger':
            position = 'Defender'
        if position == 'Middenvelder':
            position = 'Midfielder'
        if position == 'Aanvaller':
            position = 'Attacker'
    except AttributeError:
        position = ''
    try:
        kitnumber = re.search(r"Shirtnummer: (.*?)(;|$)", playerinfopart).group(1)
    except AttributeError:
        kitnumber = ''

    return fullname, firstname, lastname, birthdate, age, birthplace, nationality, height, weight, preferredfoot, currentclub, yearswithclub, currentleague, position, kitnumber


def playerlinkgetter(playerrootlist):
    playerslist = []
    for player in playerrootlist:
        playername = player.find('a').text.strip()
        playerlink = player.find('a')['href']
        playerlink = 'https://www.vi.nl' + playerlink
        playerslist.append((playername, playerlink))
    return playerslist

def lineupspart(matchroot, currentpath):
    homeplayers = matchroot.find('div', {"class": "c-line-up__team c-line-up__team--home o-layout__item u-6/12"})
    homestarters = homeplayers.find('ul', {"class": "c-line-up__list"}).find_all('li', {"class": "c-line-up__player"})
    homestarters = [x for x in homestarters if len(x['class']) == 1]
    homestarterslist = playerlinkgetter(homestarters)
    for idx, homestarter in enumerate(homestarterslist):
        playerinfolist = playerinfo(homestarter[1], currentpath)
        homestarterslist[idx] = (str(idx+1),) + homestarterslist[idx] + playerinfolist

    homesubs = homeplayers.find('ul', {"class": "c-line-up__list c-line-up__list--sub"}).find_all('li', {"class": "c-line-up__player c-line-up__player--sub"})
    homesubslist = playerlinkgetter(homesubs)
    for idx, homesub in enumerate(homesubslist):
        playerinfolist = playerinfo(homesub[1], currentpath)
        homesubslist[idx] = (str(idx+1),) + homesubslist[idx] + playerinfolist

    awayplayers = matchroot.find('div', {"class": "c-line-up__team c-line-up__team--away o-layout__item u-6/12"})
    awaystarters = awayplayers.find('ul', {"class": "c-line-up__list"}).find_all('li', {"class": "c-line-up__player"})
    awaystarters = [x for x in awaystarters if len(x['class']) == 1]
    awaystarterslist = playerlinkgetter(awaystarters)
    for idx, awaystarter in enumerate(awaystarterslist):
        playerinfolist = playerinfo(awaystarter[1], currentpath)
        awaystarterslist[idx] = (str(idx+1),) + awaystarterslist[idx] + playerinfolist

    awaysubs = awayplayers.find('ul', {"class": "c-line-up__list c-line-up__list--sub"}).find_all('li', {
        "class": "c-line-up__player c-line-up__player--sub"})
    awaysubslist = playerlinkgetter(awaysubs)
    for idx, awaysub in enumerate(awaysubslist):
        playerinfolist = playerinfo(awaysub[1], currentpath)
        awaysubslist[idx] = (str(idx+1),) + awaysubslist[idx] + playerinfolist
    return homestarterslist, homesubslist, awaystarterslist, awaysubslist

def highlightsxml(highlightstuple):
    # Get all tuple elements
    league, startdate, starttime, stadium, city, referee, attendees, fulltimescore, hometeam, homegoalscorers, homescore, awayteam, awaygoalscorers, awayscore = highlightstuple
    # And add the elements 1 by 1 to the tuple, first the highlights
    highlights = etree.Element("Highlights")
    leaguexml = etree.SubElement(highlights, "League")
    leaguexml.text = league
    startdatexml = etree.SubElement(highlights, "StartDate")
    startdatexml.text = startdate
    starttimexml = etree.SubElement(highlights, "StartTime")
    starttimexml.text = starttime
    stadiumxml = etree.SubElement(highlights, "Stadium")
    stadiumxml.text = stadium
    cityxml = etree.SubElement(highlights, "City")
    cityxml.text = city
    refereexml = etree.SubElement(highlights, "Referee")
    refereexml.text = referee
    attendeesxml = etree.SubElement(highlights, "Attendees")
    attendeesxml.text = attendees
    finalscorexml = etree.SubElement(highlights, "FullTimeScore")
    finalscorexml.text = fulltimescore
    homexml = etree.SubElement(highlights, "Home")
    hometeamxml = etree.SubElement(homexml, "Team")
    hometeamxml.text = hometeam

    homegoalscorersxml = etree.SubElement(homexml, "GoalScorersList")
    # For every home goal scored make a subelement for the homegoalscorerslist
    for idx, val in enumerate(homegoalscorers):
        goalid, minute, playerlink, owngoal, player = val
        homegoalxml = etree.SubElement(homegoalscorersxml, "Goal")
        # Make it the form of <Goal GoalId="1" Minute="55" PlayerLink="http://www.goal.com/en/people/netherlands/35246/bryan-smeets">B. Smeets</HomeGoal>
        homegoalxml.set('GoalId', goalid)
        homegoalxml.set('Minute', minute)
        homegoalxml.set('PlayerLink', playerlink)
        homegoalxml.set('OwnGoal', owngoal)
        homegoalxml.text = player

    finalscorehomexml = etree.SubElement(homexml, "FinalGoals")
    finalscorehomexml.text = homescore

    awayxml = etree.SubElement(highlights, "Away")
    awayteamxml = etree.SubElement(awayxml, "Team")
    awayteamxml.text = awayteam

    awaygoalscorersxml = etree.SubElement(awayxml, "GoalScorersList")
    for idx, val in enumerate(awaygoalscorers):
        goalid, minute, playerlink, owngoal, player = val
        awaygoalxml = etree.SubElement(awaygoalscorersxml, "Goal")
        awaygoalxml.set('GoalId', goalid)
        awaygoalxml.set('Minute', minute)
        awaygoalxml.set('PlayerLink', playerlink)
        awaygoalxml.set('OwnGoal', owngoal)
        awaygoalxml.text = player

    finalscoreawayxml = etree.SubElement(awayxml, "FinalGoals")
    finalscoreawayxml.text = awayscore

    return highlights

def eventsxml(eventstuple):
    # Get all tuple elements
    assistlist, goallist, missedpenaltylist, penaltygoallist, redcardlist, yellowcardlist, yellowredlist, owngoallist, substitutionlist = eventstuple
    events = etree.Element("Events")
    assistlistxml = etree.SubElement(events, "AssistList")
    for idx, val in enumerate(assistlist):
        id, minute, player = val
        assistxml = etree.SubElement(assistlistxml, "Assist")
        assistxml.set('AssistId', id)
        assistxml.set('Minute', minute)
        assistxml.text = player
    goallistxml = etree.SubElement(events, "GoalList")
    for idx, val in enumerate(goallist):
        id, minute, player = val
        goalxml = etree.SubElement(goallistxml, "Goal")
        goalxml.set('GoalId', id)
        goalxml.set('Minute', minute)
        goalxml.text = player
    missedpenaltylistxml = etree.SubElement(events, "MissedPenaltyList")
    for idx, val in enumerate(missedpenaltylist):
        id, minute, player = val
        missedpenaltyxml = etree.SubElement(missedpenaltylistxml, "MissedPenalty")
        missedpenaltyxml.set('MissedPenaltyId', id)
        missedpenaltyxml.set('Minute', minute)
        missedpenaltyxml.text = player
    penaltygoallistxml = etree.SubElement(events, "PenaltyGoalList")
    for idx, val in enumerate(penaltygoallist):
        id, minute, player = val
        penaltygoalxml = etree.SubElement(penaltygoallistxml, "PenaltyGoal")
        penaltygoalxml.set('PenaltyGoalId', id)
        penaltygoalxml.set('Minute', minute)
        penaltygoalxml.text = player
    redcardlistxml = etree.SubElement(events, "RedCardList")
    for idx, val in enumerate(redcardlist):
        id, minute, player = val
        redcardxml = etree.SubElement(redcardlistxml, "RedCard")
        redcardxml.set('RedCardId', id)
        redcardxml.set('Minute', minute)
        redcardxml.text = player
    yellowcardlistxml = etree.SubElement(events, "YellowCardList")
    for idx, val in enumerate(yellowcardlist):
        id, minute, player = val
        yellowcardxml = etree.SubElement(yellowcardlistxml, "YellowCard")
        yellowcardxml.set('YellowCardId', id)
        yellowcardxml.set('Minute', minute)
        yellowcardxml.text = player
    yellowredlistxml = etree.SubElement(events, "YellowRedList")
    for idx, val in enumerate(yellowredlist):
        id, minute, player = val
        yellowredxml = etree.SubElement(yellowredlistxml, "YellowRed")
        yellowredxml.set('YellowRedId', id)
        yellowredxml.set('Minute', minute)
        yellowredxml.text = player
    owngoallistxml = etree.SubElement(events, "OwnGoalList")
    for idx, val in enumerate(owngoallist):
        id, minute, player = val
        owngoalxml = etree.SubElement(owngoallistxml, "OwnGoal")
        owngoalxml.set('OwnGoalId', id)
        owngoalxml.set('Minute', minute)
        owngoalxml.text = player

    # Substitutionlist has the form of [('minute', ['player out', 'player in']), ('minute2', ['player out2', 'player in2']), ... ('minuteN', ['player outN', 'player inN'])]
    # This is given the form of <Substitution SubstitutionId="1" Minute="12" SubOut="player out" SubIn="player in">
    substitutionlistxml = etree.SubElement(events, "SubstitutionList")
    for idx, val in enumerate(substitutionlist):
        id, minute, suboutplayer, subinplayer = val
        substitutionxml = etree.SubElement(substitutionlistxml, "Substitution")
        substitutionxml.set('SubstitutionId', id)
        substitutionxml.set('Minute', minute)
        substitutionxml.set('SubOut', suboutplayer)
        substitutionxml.set('SubIn', subinplayer)
    return events


def PlayerXML(player):
    id, viname, vilink, fullname, firstname, lastname, birthdate, age, birthplace, nationality, height, weight, preferredfoot, currentclub, activeatclub, currentdivision, position, kitnumber = player
    playerelement = etree.Element("Player")
    playerelement.set("PlayerId", id)
    firstnameelement = etree.SubElement(playerelement, "FirstName")
    firstnameelement.text = firstname
    lastnameelement = etree.SubElement(playerelement, "LastName")
    lastnameelement.text = lastname
    fullnameelement = etree.SubElement(playerelement, "Fullname")
    fullnameelement.text = fullname
    birthdateelement = etree.SubElement(playerelement, "BirthDate")
    birthdateelement.text = birthdate
    ageelement = etree.SubElement(playerelement, "Age")
    ageelement.text = age
    birthplaceelement = etree.SubElement(playerelement, "BirthPlace")
    birthplaceelement.set("BirthPlace", birthplace)
    birthplaceelement.set("Nationality", nationality)
    heightelement = etree.SubElement(playerelement, "Height")
    heightelement.text = height
    weightelement = etree.SubElement(playerelement, "Weight")
    weightelement.text = weight
    preferredfootelement = etree.SubElement(playerelement, "PreferredFoot")
    preferredfootelement.text = preferredfoot
    positionelement = etree.SubElement(playerelement, "WikiPosition")
    positionelement.text = position
    goalplayernumber = etree.SubElement(playerelement, "GoalComPlayerNumber")
    goalplayernumber.text = kitnumber
    goalshownname = etree.SubElement(playerelement, "GoalComShownName")
    goalshownname.text = viname
    goalwebsite = etree.SubElement(playerelement, "GoalComWebsite")
    goalwebsite.text = vilink
    currentteamelement = etree.SubElement(playerelement, "CurrentTeam")
    currentteamelement.text = currentclub
    yearsatcurrentteamelement = etree.SubElement(playerelement, "YearsAtCurrentTeam")
    yearsatcurrentteamelement.text = activeatclub
    currentdivisionelement = etree.SubElement(playerelement, "CurrentDivision")
    currentdivisionelement.text = currentdivision
    currentnumber = etree.SubElement(playerelement, "CurrentNumber")
    currentnumber.text = kitnumber

    return playerelement

def lineupsxml(lineupstuple):
    homestarterslist, homesubslist, awaystarterslist, awaysubslist = lineupstuple
    lineups = etree.Element("Lineups")
    lineupshome = etree.SubElement(lineups, "Home")
    for player in homestarterslist:
        playerxml = PlayerXML(player)
        lineupshome.append(playerxml)
    lineupsaway = etree.SubElement(lineups, "Away")
    for player in awaystarterslist:
        playerxml = PlayerXML(player)
        lineupsaway.append(playerxml)

    substitutes = etree.Element("Substitutes")
    subshome = etree.SubElement(substitutes, "Home")
    for player in homesubslist:
        playerxml = PlayerXML(player)
        subshome.append(playerxml)
    subsaway = etree.SubElement(substitutes, "Away")
    for player in awaysubslist:
        playerxml = PlayerXML(player)
        subsaway.append(playerxml)

    return lineups, substitutes


def matchxml(matchlink, currentpath):
    matchroot = query(matchlink, currentpath)
    highlightstuple = highlightspart(matchroot)
    eventstuple = eventspart(matchroot)
    lineupstuple = lineupspart(matchroot, currentpath)

    highlights = highlightsxml(highlightstuple)
    events = eventsxml(eventstuple)
    lineups, substitutes = lineupsxml(lineupstuple)

    goaltree = etree.Element("Goal")
    goaltree.append(highlights)
    goaltree.append(events)
    goaltree.append(lineups)
    goaltree.append(substitutes)

    goaltree = etree.tostring(goaltree, encoding="utf-8", xml_declaration=False, pretty_print=True)
    for number in range(0,999):
        if os.path.isfile(currentpath + '/NewInfoXMLs/MatchTest' + str(number) + '.xml'):
            continue
        with open(currentpath + '/NewInfoXMLs/MatchTest' + str(number) + '.xml', 'wb') as f:
            print('XML file written')
            f.write(goaltree)

    '''
    s2 = matchroot.prettify()
    with open(currentpath + '/Test.xml', 'wb') as f:
        f.write(bytes(s2, 'UTF-8'))
    print(currentpath + '/Test.xml has been written')
    '''

def mainscraper():
    currentpath = os.getcwd()
    root = query("https://www.vi.nl/competities/nederland/tweede-divisie/2017-2018/wedstrijden", currentpath)
    matcheslist = findmatches(root)
    for matchlink in matcheslist:
        matchxml(matchlink, currentpath)
'''
infile = open(currentpath + '/Test.xml',"rb")
contents = infile.read()
infile.close()
matchroot = BeautifulSoup(contents, "xml")
'''
