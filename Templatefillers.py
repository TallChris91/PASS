import sys
import os.path
import xlrd
import re
import random
from math import ceil
from operator import itemgetter
import Ruleset_module as Ruleset
from Ruleset_module import secondgoal
from Reference_variety_module import PlayerReferenceModel, ClubReferenceModel
from datetime import datetime,timedelta

#This is used to convert MS JSON/MS AJAX datetime format into a datetime
def json_date_as_datetime(jd):
    sign = jd[-7]
    if sign not in '-+' or len(jd) == 13:
        millisecs = int(jd[6:-2])
    else:
        millisecs = int(jd[6:-7])
        hh = int(jd[-7:-4])
        mm = int(jd[-4:-2])
        if sign == '-': mm = -mm
        millisecs += (hh * 60 + mm) * 60000
    return datetime(1970, 1, 1) + timedelta(microseconds=millisecs * 1000)


def templatefillers(jsongamedata, homeaway, gap, **kwargs):
    if gap == 'focus team':
        club = jsongamedata['MatchInfo'][0]['c_'+homeaway.capitalize()+'Team']
        clubtuple = ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs)
        return clubtuple
    elif gap == 'other team':
        if homeaway == 'home':
            club = jsongamedata['MatchInfo'][0]['c_AwayTeam']
            clubtuple = ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs)
            return clubtuple
        if homeaway == 'away':
            club = jsongamedata['MatchInfo'][0]['c_HomeTeam']
            clubtuple = ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs)
            return clubtuple
    elif gap == 'home team':
        club = jsongamedata['MatchInfo'][0]['c_HomeTeam']
        clubtuple = ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs)
        return clubtuple
    elif gap == 'away team':
        club = jsongamedata['MatchInfo'][0]['c_AwayTeam']
        clubtuple = ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs)
        return clubtuple
    elif gap == 'tieing team':
        #Since the ruleset has already found the final goal scorer made the decisive goal, the final goal scorer is also the deciding goal scorer
        #a for a in list_a for b in list_b if a == 
        goals = [event for event in jsongamedata['MatchActions'] if event['n_ActionSet']==1]
        goalshomelist = [event for event in goals if event['n_HomeOrAway']==1]
        goalsawaylist = [event for event in goals if event['n_HomeOrAway']==-1]

        minute = 0
        for goal in goalshomelist:
            #If the minute scored is more than the minute scored of the previous found event, update the player value with the player name of the current event
            newminute = goal['n_ActionTime']
            if newminute > minute:
                minute = goal['n_ActionTime']

        for goal in goalsawaylist:
            #If the minute scored is more than the minute scored of the previous found event, update the player value with the player name of the current event
            newminute = goal['n_ActionTime']
            if newminute > minute:
                return jsongamedata['MatchInfo'][0]['c_AwayTeam']
        return jsongamedata['MatchInfo'][0]['c_HomeTeam']
    elif gap == 'winning team':
        homegoals = jsongamedata['MatchInfo'][0]['n_HomeGoals']
        awaygoals = jsongamedata['MatchInfo'][0]['n_AwayGoals']

        if homegoals > awaygoals:
            return jsongamedata['MatchInfo'][0]['c_HomeTeam']
        else:
            return jsongamedata['MatchInfo'][0]['c_AwayTeam']
    elif gap == 'losing team':
        homegoals = jsongamedata['MatchInfo'][0]['n_HomeGoals']
        awaygoals = jsongamedata['MatchInfo'][0]['n_AwayGoals']

        if awaygoals > homegoals:
            return jsongamedata['MatchInfo'][0]['c_HomeTeam']
        else:
            return jsongamedata['MatchInfo'][0]['c_AwayTeam']
    elif gap == 'final home goals':
        return jsongamedata['MatchInfo'][0]['n_HomeGoals']
    elif gap == 'final away goals':
        return jsongamedata['MatchInfo'][0]['n_AwayGoals']
    elif gap == 'stadium':
        return jsongamedata['MatchInfo'][0]['c_Stadium']
    elif gap == 'league':
        return jsongamedata['MatchInfo'][0]['c_Competition']
    elif gap == 'time':
        #d_DateLocal contains the "scheduled start time", while d_MatchStartTimeLocal is the actual time
        #e.g. 18:45 vs 18:46:47
        msjsontime = jsongamedata['MatchInfo'][0]['d_DateLocal']
        d = json_date_as_datetime(msjsontime) 
        return d.strftime("%H:%M")
    elif gap == 'referee':
        #TODO: use n_RefereeID
        return jsongamedata['MatchInfo'][0]['c_Referee']
    elif gap == 'homeaway':
        return homeaway
    elif gap == 'city':
        city = jsongamedata['MatchInfo'][0]['c_City']
        return city
    elif gap == 'attendees':
        attendees = jsongamedata['MatchInfo'][0]['n_Spectators']
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
        playertuple = PlayerReferenceModel(player, jsongamedata, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'scoring team':
        event = kwargs['event']
        try:
            team = event['team']
            #club = jsongamedata.find('highlights').find(team).find('team').text
            clubtuple = ClubReferenceModel(team, jsongamedata, homeaway, gap, **kwargs)
            return clubtuple
        except TypeError:
            print(event)
            print(gap)
            print(kwargs['gamestatisticslist'])
            sys.exit(1)
    elif gap == 'not scoring team':
        event = kwargs['event']
        try:
            team = event['team']
            if team == 'home':
                club = jsongamedata['MatchInfo'][0]['c_AwayTeam']
                clubtuple = ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs)
                return clubtuple
            if team == 'away':
                club = jsongamedata['MatchInfo'][0]['c_HomeTeam']
                clubtuple = ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs)
                return clubtuple
        except TypeError:
            print(event)
            print(gap)
            print(kwargs['gamestatisticslist'])
            sys.exit(1)
    elif gap == 'minute':
        event = kwargs['event']
        try:
            return str(event['minute'])
        except (KeyError, TypeError) as e:
            print(event)
            sys.exit(1)
    elif gap == 'minus minute':
        event = kwargs['event']
        minute = event['minute_asFloat']
        minusminute = ceil(90 - minute)
        return str(minusminute)
    elif gap == 'assist giver':
        event = kwargs['event']
        try:
            player = event['assist']
        except KeyError:
            print(event)
        playertuple = PlayerReferenceModel(player, jsongamedata, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'goalkeeper focus team':
        teamnumber = 1
        if homeaway=="away":
            teamnumber = -1
        #TODO: use person ID
        for person in jsongamedata['MatchLineup']:
            #this would fail if goalkeeper is also the coach... but it rules out the bench goalkeeper
            if person['n_FunctionCode']==1 and person['n_HomeOrAway']==teamnumber:
                gk = person
                break
        playertuple = PlayerReferenceModel(gk, jsongamedata, homeaway, gap, **kwargs)
    elif gap == 'goalkeeper other team':
        teamnumber = 1
        if homeaway == 'home':
            teamnumber = -1
        for person in jsongamedata['MatchLineup']:
            if person['n_FunctionCode']==1 and person['n_HomeOrAway']==teamnumber:
                gk = person
                break
        playertuple = PlayerReferenceModel(gk, jsongamedata, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'focus team manager':
        teamnumber = 1
        if homeaway=="away":
            teamnumber = -1
        for person in jsongamedata['MatchLineup']:
            if person['n_FunctionCode']&16 and person['n_HomeOrAway']==teamnumber:
                manager = person
                break
        playertuple = PlayerReferenceModel(manager, jsongamedata, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'other team manager':
        teamnumber = 1
        if homeaway == 'home':
            teamnumber = -1
        for person in jsongamedata['MatchLineup']:
            if person['n_FunctionCode']&16 and person['n_HomeOrAway']==teamnumber:
                manager = person
                break            
        playertuple = PlayerReferenceModel(manager, jsongamedata, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'time between goals':
        event = kwargs['event']
        tbg = str(abs(ceil(event['minute_asFloat 1'] - event['minute_asFloat 2'])))
        return tbg
    elif gap == 'goal scorer 1':
        event = kwargs['event']
        player = event['player 1']
        playertuple = PlayerReferenceModel(player, jsongamedata, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'goal scorer 2':
        event = kwargs['event']
        player = event['player 2']
        playertuple = PlayerReferenceModel(player, jsongamedata, homeaway, gap, **kwargs)
        return playertuple
    elif gap == 'minute 1':
        event = kwargs['event']
        return str(event['minute 1'])
    elif gap == 'minute 2':
        event = kwargs['event']
        return str(event['minute 2'])
    elif gap == 'first/second half':
        event = kwargs['event']
        if int(event['minute'].split("+")[0]) > 45:
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
        yellowcards = [event for event in jsongamedata['MatchActions'] if event['n_ActionSet'] == 3 and event['n_ActionCode']&2048]
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
#           for idx, player in enumerate(playerlist):
#               try:
#                   name = jsongamedata.find('lineups').find(text=player).parent.parent
#               except AttributeError:
#                   try:
#                       name = jsongamedata.find('substitutes').find(text=player).parent.parent
#                   except AttributeError:
#                       try:
#                           name = jsongamedata.find('lineups').find(['name', 'fullname', 'goalcomshownname'], text=re.compile(player.split()[-1], re.I)).parent
#                       except AttributeError:
#                           try:
#                               name = jsongamedata.find('substitutes').find(['name', 'fullname', 'goalcomshownname'], text=re.compile(player.split()[-1], re.I)).parent
#                           except AttributeError:
#                               print('Player not found: ' + player)
#                               sys.exit(1)
#               try:
#                   playerlist[idx] = name.find('name').text
#               except AttributeError:
#                   playerlist[idx] = name.find('fullname').text
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
            club = jsongamedata['MatchInfo'][0]['c_HomeTeam']
            clubtuple = ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs)
            return clubtuple
        if team == 'away':
            club = jsongamedata['MatchInfo'][0]['c_AwayTeam']
            clubtuple = ClubReferenceModel(club, jsongamedata, homeaway, gap, **kwargs)
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
        minute = float(event['minute'].replace("+","."))
        subs = [event for event in jsongamedata['MatchActions'] if event['n_ActionSet']==5]
        for sub_event in subs:
            if sub_event['c_Person'] == player:
                sub_minute = float(c_ActionMinute['minute'].replace("+",".").strip("'"))
                minsub = math.ceil(minute - sub_minute)
                break
        return minsub
    elif gap == 'position own goal scorer':
        event = kwargs['event']
        eventplayer = event['player']
        print(event)
        playerlist = jsongamedata.find('lineups').find('home').find_all('name')
        playerlist.extend(jsongamedata.find('substitutes').find('home').find_all('name'))
        playerlist.extend(jsongamedata.find('lineups').find('home').find_all('goalcomshownname'))
        playerlist.extend(jsongamedata.find('substitutes').find('home').find_all('goalcomshownname'))
        playerlist.extend(jsongamedata.find('lineups').find('away').find_all('name'))
        playerlist.extend(jsongamedata.find('substitutes').find('away').find_all('name'))
        playerlist.extend(jsongamedata.find('lineups').find('away').find_all('goalcomshownname'))
        playerlist.extend(jsongamedata.find('substitutes').find('away').find_all('goalcomshownname'))
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
        if len(goalscorerslist) > 1:
            gsstring = ', '.join(goalscorerslist[:-1]) + ' en ' + goalscorerslist[-1]
        else:
            gsstring = goalscorerslist[0]
        return gsstring
    elif gap == 'deciding goal scorer':
        #Since the ruleset has already found the final goal scorer made the decisive goal, the final goal scorer is also the deciding goal scorer
        #Combine the home and away goalscorerslist
        goals = [event for event in jsongamedata['MatchActions'] if event['n_ActionSet']==1]
        minute = 0
        for goalevent in goals:
            #If the minute scored is more than the minute scored of the previous found event, update the player value with the player name of the current event
            newminute = goalevent['n_ActionTime']
            if int(newminute) > minute:
                minute = goalevent['n_ActionTime']
                player = goalevent['c_Person']
        playertuple = PlayerReferenceModel(player, jsongamedata, homeaway, gap, **kwargs)
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
        msjsontime = jsongamedata['MatchInfo'][0]['d_DateLocal']
        date = json_date_as_datetime(msjsontime) 
        weekday = date.weekday()
        weeklist = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']
        weekday = weeklist[weekday]
        return weekday
    elif gap == 'daytime':
        msjsontime = jsongamedata['MatchInfo'][0]['d_DateLocal']
        time = json_date_as_datetime(msjsontime) 
        if time.hour < 11:
            return 'morning'
        if time.hour > 16:
            return 'evening'
        else:
            return 'afternoon'
    elif gap == 'focus team clubname':
        club = jsongamedata['MatchInfo'][0]['c_'+homeaway.capitalize()+'Team']
        return club
    elif gap == 'other team clubname':
        if homeaway == 'home':
            club = jsongamedata['MatchInfo'][0]['c_AwayTeam']
            return club
        if homeaway == 'away':
            club = jsongamedata['MatchInfo'][0]['c_HomeTeam']
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






        

