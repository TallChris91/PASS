import sys
from bs4 import BeautifulSoup
import re
from operator import itemgetter

def EventConnect(soup, assists, regulargoals, missedpenalties, penaltygoals, redcards, yellowcards, yellowreds, owngoals):
    def getteam(soup, player):
        homelist = soup.find('lineups').find('home').find_all('name')
        homelist.extend(soup.find('substitutes').find('home').find_all('name'))
        homelist.extend(soup.find('lineups').find('home').find_all('goalcomshownname'))
        homelist.extend(soup.find('substitutes').find('home').find_all('goalcomshownname'))

        homelistfullname = soup.find('lineups').find('home').find_all('fullname')
        homelistfullname.extend(soup.find('substitutes').find('home').find_all('fullname'))
        for idx, val in enumerate(homelistfullname):
            homelistfullname[idx] = homelistfullname[idx].text
        awaylistfullname = soup.find('lineups').find('away').find_all('fullname')
        awaylistfullname.extend(soup.find('substitutes').find('away').find_all('fullname'))
        for idx, val in enumerate(awaylistfullname):
            awaylistfullname[idx] = awaylistfullname[idx].text

        for idx, val in enumerate(homelist):
            homelist[idx] = homelist[idx].text
        if player in homelist:
            return {'team': 'home'}
        awaylist = soup.find('lineups').find('away').find_all('name')
        awaylist.extend(soup.find('substitutes').find('away').find_all('name'))
        awaylist.extend(soup.find('lineups').find('away').find_all('goalcomshownname'))
        awaylist.extend(soup.find('substitutes').find('away').find_all('goalcomshownname'))
        for idx, val in enumerate(awaylist):
            awaylist[idx] = awaylist[idx].text
        if player in awaylist:
            return {'team': 'away'}
        #If nothing is found, search for the last name
        lastname = player.split()[-1]
        lastnamehomelist = []
        lastnameawaylist = []
        for name in homelist:
            try:
                lastnamehomelist.append(name.split()[-1])
            except IndexError:
                continue
        for name in awaylist:
            try:
                lastnameawaylist.append(name.split()[-1])
            except IndexError:
                continue
        if lastname in lastnamehomelist:
            return {'team': 'home'}
        if lastname in lastnameawaylist:
            return {'team': 'away'}
        else:
            for fullname in homelistfullname:
                if lastname in fullname:
                    return {'team': 'home'}
            for fullname in awaylistfullname:
                if lastname in fullname:
                    return {'team': 'away'}
            else:
                print(lastname)
                sys.exit(1)
    #Connect the assists with the regular goals
    eventlist = []
    #First get the goal that was scored
    for goal in regulargoals:
        minute = goal['minute']
        try:
            minute = int(minute)
        except ValueError:
            minute = re.findall(r'\d+', minute)
            minute = map(int, minute)
            minute = sum(minute)
        #Make a dict with the minute and goalscorer
        goaldict = {'minute': minute}
        goalscorer = goal.text
        goaldict.update({'player': goalscorer})
        #See if there is a matching assist
        for assist in assists:
            minute2 = assist['minute']
            try:
                minute2 = int(minute2)
            except ValueError:
                minute2 = re.findall(r'\d+', minute2)
                minute2 = map(int, minute2)
                minute2 = sum(minute2)
            if minute2 == minute:
                goaldict.update({'assist': assist.text})
        try:
            goaldict.update(getteam(soup, goalscorer))
        except TypeError:
            print(goalscorer)
            sys.exit(1)
        goaldict.update({'event': 'regular goal'})
        eventlist.append(goaldict.copy())
    otherevents = [missedpenalties, penaltygoals, redcards, yellowcards, yellowreds, owngoals]
    eventdictlist = ['missed penalty', 'penalty goal', 'red card', 'yellow card', 'twice yellow', 'own goal']
    for idx, category in enumerate(otherevents):
        for event in category:
            minute = event['minute']
            try:
                minute = int(minute)
            except ValueError:
                minute = re.findall(r'\d+', minute)
                minute = map(int, minute)
                minute = sum(minute)
            eventdict = {'minute': minute}
            eventplayer = event.text
            try:
                eventdict.update(getteam(soup, eventplayer))
            except TypeError:
                print('Player not found: ' + eventplayer)
                sys.exit(1)
            eventdict.update({'player': eventplayer})
            eventdict.update({'event': eventdictlist[idx]})
            eventlist.append(eventdict.copy())
    #Sort the list of all events by minutes so you get a chronological succession of events
    eventlist = sorted(eventlist, key=itemgetter('minute'))
    return eventlist

def GameCourseEvents(soup):
    owngoals2 = []
    assists = soup.find('events').find('assistlist').findChildren()
    regulargoals = soup.find('events').find('goallist').findChildren()
    if len(regulargoals) == 0:
        regulargoalshome = soup.find('highlights').find('home').find('goalscorerslist').findChildren()
        regulargoalsaway = soup.find('highlights').find('away').find('goalscorerslist').findChildren()
        regulargoals = regulargoalshome + regulargoalsaway
        #Delete all goals that are own goals (these are appended to a backup owngoals list)
        num = len(regulargoals)-1
        while num >= 0:
            if regulargoals[num]['owngoal'] == 'y':
                owngoals2.append(regulargoals[num])
                del regulargoals[num]
            num -= 1

    missedpenalties = soup.find('events').find('missedpenaltylist').findChildren()
    penaltygoals = soup.find('events').find('penaltygoallist').findChildren()
    redcards = soup.find('events').find('redcardlist').findChildren()
    yellowcards = soup.find('events').find('yellowcardlist').findChildren()
    yellowreds = soup.find('events').find('yellowredlist').findChildren()
    owngoals = soup.find('events').find('owngoallist').findChildren()
    if (len(owngoals) == 0) and (len(owngoals2) != 0):
        owngoals = owngoals2
    eventdict = EventConnect(soup, assists, regulargoals, missedpenalties, penaltygoals, redcards, yellowcards, yellowreds, owngoals)
    return eventdict

def TopicCollection(file):
    print('file name/location:')
    print(file)
    with open(file, 'rb') as f:
        soup = BeautifulSoup(f, "lxml")
    eventlist = GameCourseEvents(soup)
    gamecourselist = []
    gamestatisticslist = []
    twiceyellowlist = []
    for eventdict in eventlist:
        if (eventdict['event'] == 'regular goal') or (eventdict['event'] == 'missed penalty') or (eventdict['event'] == 'penalty goal') or (eventdict['event'] == 'own goal'):
            gamecourselist.append(eventdict)
        elif (eventdict['event'] == 'red card') or (eventdict['event'] == 'yellow card') or (eventdict['event'] == 'twice yellow'):
            gamestatisticslist.append(eventdict)
            if eventdict['event'] == 'twice yellow':
                twiceyellowlist.append(eventdict['player'])
    return gamecourselist, gamestatisticslist

#print(TopicCollection('C:/Syncmap/Promotie/MASC Newspaper/GoalStats/InfoXMLs/DG_NEC_27112015_goal.xml'))

#print(TopicCollection('/Users/stasiuz/PASS/InfoXMLs/DG_NEC_27112015_goal.xml'))
