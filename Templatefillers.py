import sys
import os.path
from bs4 import BeautifulSoup
import xlrd
import re
import random
from operator import itemgetter
import Ruleset_module as Ruleset
from Ruleset_module import secondgoal
from Reference_variety_module import PlayerReferenceModel, ClubReferenceModel
from datetime import datetime

def templatefillers(soup, homeaway, gap, **kwargs):
    if gap == 'focus team':
        club = soup.find('highlights').find(homeaway).find('team').text
        clubtuple = ClubReferenceModel(club, soup, homeaway, gap, **kwargs)
        return clubtuple
    elif gap == 'other team':
        if homeaway == 'home':
            club = soup.find('highlights').find('away').find('team').text
            clubtuple = ClubReferenceModel(club, soup, homeaway, gap, **kwargs)
            return clubtuple
        if homeaway == 'away':
            club = soup.find('highlights').find('home').find('team').text
            clubtuple = ClubReferenceModel(club, soup, homeaway, gap, **kwargs)
            return clubtuple
    elif gap == 'final home goals':
        homegoals = soup.find('highlights').find('home').find('finalgoals').text
        return homegoals
    elif gap == 'final away goals':
        awaygoals = soup.find('highlights').find('away').find('finalgoals').text
        return awaygoals
    elif gap == 'stadium':
        stadium = soup.find('highlights').find('stadium').text
        stadium = stadium.replace(u"\u2022 ", "")
        return stadium
    elif gap == 'time':
        time = soup.find('highlights').find('starttime').text
        return time
    elif gap == 'referee':
        referee = soup.find('highlights').find('referee').text
        referee = re.sub(r'^(.*?)\.\s', '', referee)
        return referee
    elif gap == 'homeaway':
        return homeaway
    elif gap == 'city':
        city = soup.find('highlights').find('city').text
        return city
    elif gap == 'attendees':
        attendees = soup.find('highlights').find('attendees').text
        return attendees
    elif (gap == 'home goals') or (gap == 'away goals') or (gap == 'number of goals focus team') or (gap == 'number of goals other team') or (gap == 'number of goals'):
        eventlist = kwargs['eventlist']
        idx = kwargs['idx']
        untilevent = eventlist[:idx+1]
        homegoals = 0
        awaygoals = 0
        for event in untilevent:
            if type(event) == dict:
                if ((event['event'] == 'regular goal') and (event['team'] == 'home')) or ((event['event'] == 'penalty goal') and (event['team'] == 'home')) or ((event['event'] == 'own goal') and (event['team'] == 'away')):
                    if 'player' in event:
                        homegoals += 1
                    else:
                        homegoals += 2
                elif ((event['event'] == 'regular goal') and (event['team'] == 'away')) or ((event['event'] == 'penalty goal') and (event['team'] == 'away')) or ((event['event'] == 'own goal') and (event['team'] == 'home')):
                    if 'player' in event:
                        awaygoals += 1
                    else:
                        awaygoals += 2
        if gap == 'home goals':
            return str(homegoals)
        if gap == 'away goals':
            return str(awaygoals)
        if gap == 'number of goals focus team':
            team = event['team']
            if team == 'home':
                return 'goal ' + str(homegoals)
            else:
                return 'goal ' + str(awaygoals)
        if gap == 'number of goals other team':
            team = event['team']
            if team == 'home':
                return 'goal ' + str(awaygoals)
            else:
                return 'goal ' + str(homegoals)
        if gap == 'number of goals':
            totalgoals = awaygoals + homegoals
            return 'goal ' + str(totalgoals)
    elif (gap == 'goal scorer') or (gap == 'twice yellow player') or (gap == 'red player') or (gap == 'own goal scorer') or (gap == 'penalty taker') or (gap == 'yellow card player'):
        event = kwargs['event']
        try:
            player = event['player']
        except TypeError:
            print(event)
            print(gap)
            print(kwargs['gamestatisticslist'])
            sys.exit(1)
        playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'minute':
        event = kwargs['event']
        try:
            return str(event['minute'])
        except (KeyError, TypeError) as e:
            print(event)
            sys.exit(1)
    elif gap == 'minus minute':
        event = kwargs['event']
        minute = event['minute']
        minusminute = 90 - minute
        return str(minusminute)
    elif gap == 'assist giver':
        event = kwargs['event']
        try:
            player = event['assist']
        except KeyError:
            print(event)
        playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'goalkeeper focus team':
        try:
            gk = soup.find('lineups').find(homeaway).find('goalkeeper').find('name').text
        except AttributeError:
            gk = soup.find('lineups').find(homeaway).find('player', {"playerid": "1"}).find('name').text
        if gk:
            player = gk
            playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
            return playertuple
        else:
            player = soup.find('lineups').find(homeaway).find('goalkeeper').find('goalcomshownname').text
            playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
            return playertuple
    elif gap == 'goalkeeper other team':
        if homeaway == 'home':
            other = 'away'
        elif homeaway == 'away':
            other = 'home'
        try:
            gk = soup.find('lineups').find(other).find('goalkeeper').find('name')
        except AttributeError:
            gk = soup.find('lineups').find(other).find('player', {"playerid": "1"}).find('name')
        if gk.text:
            player = gk.text
        else:
            gk = soup.find('lineups').find(other).find('goalkeeper').find('goalcomshownname').text
            player = gk
        playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'focus team manager':
        try:
            manager = soup.find('managers').find(homeaway).find('manager').find('name')
            if manager.text:
                player = manager.text
        except AttributeError:
            try:
                manager = soup.find('managers').find(homeaway).find('manager').find('goalcomshownname').text
                player = manager
            except AttributeError:
                return 'de manager'
        playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'other team manager':
        if homeaway == 'home':
            other = 'away'
        if homeaway == 'away':
            other = 'home'
        manager = soup.find('managers').find(other).find('manager').find('name')
        if manager.text:
            player = manager.text
        else:
            manager = soup.find('managers').find(other).find('manager').find('goalcomshownname').text
            player = manager
        playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'time between goals':
        event = kwargs['event']
        tbg = str(abs(event['minute 1'] - event['minute 2']))
        return tbg
    elif gap == 'goal scorer 1':
        event = kwargs['event']
        player = event['player 1']
        playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'goal scorer 2':
        event = kwargs['event']
        player = event['player 2']
        playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'minute 1':
        event = kwargs['event']
        return str(event['minute 1'])
    elif gap == 'minute 2':
        event = kwargs['event']
        return str(event['minute 2'])
    elif gap == 'first/second half':
        event = kwargs['event']
        if event['minute'] > 45:
            return 'second half'
        else:
            return 'first half'
    elif gap == 'number of goals goal scorer':
        eventlist = kwargs['eventlist']
        idx = kwargs['idx']
        numbergoals = 0
        untilevent = eventlist[:idx + 1]
        for event in untilevent:
            if (type(event) == dict) and ((event['event'] == 'regular goal') or (event['event'] == 'penalty goal')):
                #Get all the values for keys containing 'player'
                players = [value for key, value in event.items() if 'player' in key]
                for player in players:
                    if player == eventlist[idx]['player']:
                        numbergoals += 1
        return 'goal ' + str(numbergoals)
    elif gap == 'number of yellow cards':
        #Get the yellow cards from the yellow card list
        yellowcards = soup.find('yellowcardlist').findChildren()
        #And get the players that got 2x yellow
        yellowreds = soup.find('yellowredlist').findChildren()
        for idx, val in enumerate(yellowreds):
            yellowreds[idx] = yellowreds[idx].text
        #If a player has gotten 2x yellow, remove him from the yellow card list
        yellowcards = [x for x in yellowcards if x.text not in yellowreds]

        return str(len(yellowcards))
    elif (gap == 'focus team yellow card players') or (gap == 'yellow card players') or (gap == 'other team yellow card players') or (gap == 'twice yellow players'):
        def playerlistcreate(event):
            playerlist = []
            homeawaylist = []
            for key in event:
                if ('player' in key) or ('team' in key):
                    try:
                        newkey = int(re.sub(r'[^0-9]', '', key))
                    except ValueError:
                        newkey = 1
                    t = (newkey, event[key],)
                    if 'player' in key:
                        playerlist.append(t)
                    else:
                        homeawaylist.append(t)
            playerlist = sorted(playerlist, key=lambda x: x[0])
            playerlist = [x[1] for x in playerlist]
            for idx, player in enumerate(playerlist):
                try:
                    name = soup.find('lineups').find(text=player).parent.parent
                except AttributeError:
                    try:
                        name = soup.find('substitutes').find(text=player).parent.parent
                    except AttributeError:
                        try:
                            name = soup.find('lineups').find(['name', 'fullname', 'goalcomshownname'], text=re.compile(player.split()[-1], re.I)).parent
                        except AttributeError:
                            try:
                                name = soup.find('substitutes').find(['name', 'fullname', 'goalcomshownname'], text=re.compile(player.split()[-1], re.I)).parent
                            except AttributeError:
                                print('Player not found: ' + player)
                                sys.exit(1)
                playerlist[idx] = name.find('name').text
            homeawaylist = sorted(homeawaylist, key=lambda x: x[0])
            homeawaylist = [x[1] for x in homeawaylist]
            return playerlist, homeawaylist

        event = kwargs['event']

        gamestatisticslist = kwargs['gamestatisticslist']

        playerlist, homeawaylist = playerlistcreate(event)

        if event['event'] == 'yellow card':
            for gamestat in gamestatisticslist:
                if gamestat['event'] == 'yellow card':
                    continue
                playerlistother, homeawaylistother = playerlistcreate(gamestat)
                for otherplayer in playerlistother:
                    try:
                        currentindex = playerlist.index(otherplayer)
                        del playerlist[currentindex]
                        del homeawaylist[currentindex]
                    except ValueError:
                        ''


        if (gap == 'yellow card players') or (gap == 'twice yellow players'):
            playerstring = ', '.join(playerlist[:-1]) + ' en ' + playerlist[-1]
            return playerstring
        if gap == 'focus team yellow card players':
            newplayerlist = [x for idx, x in enumerate(playerlist) if homeawaylist[idx] == homeaway]
        elif gap == 'other team yellow card players':
            newplayerlist = [x for idx, x in enumerate(playerlist) if homeawaylist[idx] != homeaway]
        if len(newplayerlist) > 1:
            newplayerstring = ', '.join(newplayerlist[:-1]) + ' en ' + newplayerlist[-1]
            return newplayerstring
        elif len(newplayerlist) == 1:
            return newplayerlist[0]
        else:
            return 'geen spelers'
    elif (gap == 'twice yellow team') or (gap == 'red team') or (gap == 'yellow team'):
        event = kwargs['event']
        team = event['team']
        if team == 'home':
            club = soup.find('highlights').find('home').find('team').text
            clubtuple = ClubReferenceModel(club, soup, homeaway, gap, **kwargs)
            return clubtuple
        if team == 'away':
            club = soup.find('highlights').find('away').find('team').text
            clubtuple = ClubReferenceModel(club, soup, homeaway, gap, **kwargs)
            return clubtuple
    elif gap == 'remaining players red team':
        event = kwargs['event']
        team = event['team']
        gamestatisticslist = kwargs['gamestatisticslist']
        idx = kwargs['idx']
        playernumber = 11
        for i in range(idx+1):
            try:
                if ((gamestatisticslist[i]['event'] == 'red card') or (gamestatisticslist[i]['event'] == 'twice yellow')) and (gamestatisticslist[i]['team'] == team):
                    playernumber -= 1
            except:
                pass
        return str(playernumber)
    elif gap == 'minutes since substitution':
        event = kwargs['event']
        player = event['player']
        minute = int(event['minute'])
        subs = soup.find('events').find('substitutionlist').find_all("substitution")
        for i in subs:
            if str(i['subin']) == player:
                minsub = minute - int(i['minute'])
                break
        return minsub
    elif gap == 'position own goal scorer':
        event = kwargs['event']
        eventplayer = event['player']
        playerlist = soup.find('lineups').find('home').find_all('name')
        playerlist.extend(soup.find('substitutes').find('home').find_all('name'))
        playerlist.extend(soup.find('lineups').find('home').find_all('goalcomshownname'))
        playerlist.extend(soup.find('substitutes').find('home').find_all('goalcomshownname'))
        playerlist.extend(soup.find('lineups').find('away').find_all('name'))
        playerlist.extend(soup.find('substitutes').find('away').find_all('name'))
        playerlist.extend(soup.find('lineups').find('away').find_all('goalcomshownname'))
        playerlist.extend(soup.find('substitutes').find('away').find_all('goalcomshownname'))
        for player in playerlist:
            if player.text == eventplayer:
                parent = player.parent.name
                relevantlines = player.parent
                break
        if parent != 'substitute':
            return parent
        else:
            if re.search(r'\bgoal', relevantlines.find('wikiposition').text, re.I):
                return 'goalkeeper'
            elif (re.search(r'back', relevantlines.find('wikiposition').text, re.I)) or (re.search(r'defender', relevantlines.find('wikiposition').text, re.I)) or (re.search(r'sweeper', relevantlines.find('wikiposition').text, re.I)):
                return 'defender'
            elif (re.search(r'midfielder', relevantlines.find('wikiposition').text, re.I)) or (re.search(r'winger', relevantlines.find('wikiposition').text, re.I)):
                return 'midfielder'
            elif (re.search(r'forward', relevantlines.find('wikiposition').text, re.I)) or (re.search(r'striker', relevantlines.find('wikiposition').text, re.I)) or (re.search(r'attacker', relevantlines.find('wikiposition').text, re.I)):
                return 'attacker'
            else:
                return None
    elif gap == 'goal scorers list focus team':
        gamecourselist = kwargs['gamecourselist']
        goalscorerslist = []
        for event in gamecourselist:
            if ((event['event'] == 'regular goal') and (event['team'] == homeaway)) or ((event['event'] == 'penalty goal') and (event['team'] == homeaway)) or ((event['event'] == 'own goal') and (event['team'] != homeaway)):
                playerlist = [value for key, value in event.items() if 'player' in key]
                for player in playerlist:
                    if player not in goalscorerslist:
                        goalscorerslist.append(player)
        for idx, player in enumerate(goalscorerslist):
            try:
                name = soup.find('lineups').find(text=player).parent.parent
            except AttributeError:
                try:
                    name = soup.find('substitutes').find(text=player).parent.parent
                except AttributeError:
                    try:
                        name = soup.find('lineups').find(text=re.compile(player.split()[-1])).parent.parent
                    except AttributeError:
                        try:
                            name = soup.find('substitutes').find(text=re.compile(player.split()[-1])).parent.parent
                        except AttributeError:
                            print('Player not found: ' + player)
                            sys.exit(1)
            goalscorerslist[idx] = name.find('name').text
        if len(goalscorerslist) > 1:
            gsstring = ', '.join(goalscorerslist[:-1]) + ' en ' + goalscorerslist[-1]
        else:
            gsstring = goalscorerslist[0]
        return gsstring
    elif gap == 'deciding goal scorer':
        #Since the ruleset has already found the final goal scorer made the decisive goal, the final goal scorer is also the deciding goal scorer
        #Combine the home and away goalscorerslist
        goalscorerslist = soup.find('highlights').find('home').find('goalscorerslist').find_all('goal')
        goalscorerslist.extend(soup.find('highlights').find('away').find('goalscorerslist').find_all('goal'))
        minute = 0
        for goalscorer in goalscorerslist:
            #If the minute scored is more than the minute scored of the previous found event, update the player value with the player name of the current event
            if int(goalscorer['minute']) > minute:
                minute = int(goalscorer['minute'])
                player = goalscorer.text
        playertuple = PlayerReferenceModel(player, soup, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'biggest goal difference home goals':
        gamecourselist = kwargs['gamecourselist']
        differencedict = {}
        homegoals = 0
        awaygoals = 0
        for event in gamecourselist:
            if ((event['event'] == 'regular goal') and (event['team'] == 'home')) or ((event['event'] == 'penalty goal') and (event['team'] == 'home')) or ((event['event'] == 'own goal') and (event['team'] == 'away')):
                homegoals += 1
            if ((event['event'] == 'regular goal') and (event['team'] == 'away')) or ((event['event'] == 'penalty goal') and (event['team'] == 'away')) or ((event['event'] == 'own goal') and (event['team'] == 'home')):
                awaygoals += 1
            differencedict.update({abs(homegoals-awaygoals): homegoals})
        maxdifference = max(differencedict)
        return str(differencedict[maxdifference])
    elif gap == 'biggest goal difference away goals':
        gamecourselist = kwargs['gamecourselist']
        differencedict = {}
        homegoals = 0
        awaygoals = 0
        for event in gamecourselist:
            if ((event['event'] == 'regular goal') and (event['team'] == 'home')) or ((event['event'] == 'penalty goal') and (event['team'] == 'home')) or ((event['event'] == 'own goal') and (event['team'] == 'away')):
                homegoals += 1
            if ((event['event'] == 'regular goal') and (event['team'] == 'away')) or ((event['event'] == 'penalty goal') and (event['team'] == 'away')) or ((event['event'] == 'own goal') and (event['team'] == 'home')):
                awaygoals += 1
            differencedict.update({abs(homegoals-awaygoals): awaygoals})
        maxdifference = max(differencedict)
        return str(differencedict[maxdifference])
    elif gap == 'biggest other team lead home goals':
        gamecourselist = kwargs['gamecourselist']
        differencedict = {}
        focusgoals = 0
        othergoals = 0
        for event in gamecourselist:
            if ((event['event'] == 'regular goal') and (event['team'] == homeaway)) or ((event['event'] == 'penalty goal') and (event['team'] == homeaway)) or ((event['event'] == 'own goal') and (event['team'] != homeaway)):
                focusgoals += 1
            if ((event['event'] == 'regular goal') and (event['team'] != homeaway)) or ((event['event'] == 'penalty goal') and (event['team'] != homeaway)) or ((event['event'] == 'own goal') and (event['team'] == homeaway)):
                othergoals += 1
            if othergoals > focusgoals:
                if homeaway == 'home':
                    differencedict.update({abs(focusgoals - othergoals): focusgoals})
                else:
                    differencedict.update({abs(focusgoals - othergoals): othergoals})
        maxdifference = max(differencedict)
        return str(differencedict[maxdifference])
    elif gap == 'biggest other team lead away goals':
        gamecourselist = kwargs['gamecourselist']
        differencedict = {}
        focusgoals = 0
        othergoals = 0
        for event in gamecourselist:
            if ((event['event'] == 'regular goal') and (event['team'] == homeaway)) or ((event['event'] == 'penalty goal') and (event['team'] == homeaway)) or ((event['event'] == 'own goal') and (event['team'] != homeaway)):
                focusgoals += 1
            if ((event['event'] == 'regular goal') and (event['team'] != homeaway)) or ((event['event'] == 'penalty goal') and (event['team'] != homeaway)) or ((event['event'] == 'own goal') and (event['team'] == homeaway)):
                othergoals += 1
            if othergoals > focusgoals:
                if homeaway != 'home':
                    differencedict.update({abs(focusgoals - othergoals): focusgoals})
                else:
                    differencedict.update({abs(focusgoals - othergoals): othergoals})
        maxdifference = max(differencedict)
        return str(differencedict[maxdifference])
    elif gap == 'day':
        date = soup.find('highlights').find('startdate').text
        date = datetime.strptime(date, '%B %d, %Y')
        weekday = date.weekday()
        weeklist = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']
        weekday = weeklist[weekday]
        return weekday
    elif gap == 'daytime':
        time = soup.find('highlights').find('starttime').text
        time = time.replace(u"\u2022 ", "")
        time = datetime.strptime(time, '%H:%M')
        if time.hour < 11:
            return 'morning'
        if time.hour > 16:
            return 'evening'
        else:
            return 'afternoon'
    elif gap == 'focus team clubname':
        club = soup.find('highlights').find(homeaway).find('team').text
        return club
    elif gap == 'other team clubname':
        if homeaway == 'home':
            club = soup.find('highlights').find('away').find('team').text
            return club
        if homeaway == 'away':
            club = soup.find('highlights').find('home').find('team').text
            return club
    elif gap == 'final remaining players focus team':
        gamestatisticslist = kwargs['gamestatisticslist']
        focusteamplayers = 11
        for idx, event in enumerate(gamestatisticslist):
            if (type(event == dict)) and ((event['event'] == 'red card') or (event['event'] == 'twice yellow')):
                teamlist = [value for key, value in event.items() if 'team' in event]
                for t in teamlist:
                    if t == homeaway:
                        focusteamplayers -= 1
        return str(focusteamplayers)
    elif gap == 'final remaining players other team':
        gamestatisticslist = kwargs['gamestatisticslist']
        otherteamplayers = 11
        for event in gamestatisticslist:
            if (type(event == dict)) and ((event['event'] == 'red card') or (event['event'] == 'twice yellow')):
                teamlist = [value for key, value in event.items() if 'team' in event]
                for t in teamlist:
                    if t != homeaway:
                        otherteamplayers -= 1
        return str(otherteamplayers)
    else:
        print(gap)






        

