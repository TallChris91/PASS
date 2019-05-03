import sys
import re
import json
from operator import itemgetter

def EventConnect(assists, regulargoals, missedpenalties, penaltygoals, redcards, yellowcards, yellowreds, owngoals):
	def CreateSmallEventSummary(event):
		minute = 0
		if 'c_ActionMinute' in event:
			minute = event['c_ActionMinute'].replace("'","")
		else: 
			minute = int(event['n_ActionTime']) // 60000 #milliseconds to minutes
		eventdict = {'minute': minute}
		#TODO: change this to PersonID
		eventdict.update({'player': event['c_Person']})
		homeaway = 'home'
		if event['n_HomeOrAway']==-1:
			homeaway = 'away'
		eventdict.update({'team':homeaway})
		return eventdict
	
	#sometimes event happen in overtime and the "minute" will be 45+1
	#this considers the "+" as a decimal separator to sort these events correctly
	def EventSorter(x):
		return float(x['minute'].replace('+',"."))
	
	#Connect the assists with the regular goals
	eventlist = []
	
	#First get the goal that was scored
	for goal in regulargoals:
		goaldict = CreateSmallEventSummary(goal)
		goaldict.update({'event': 'regular goal'})
		eventlist.append(goaldict.copy())

	for assist in assists:
		assistdict = CreateSmallEventSummary(assist)
		#TODO: change this to SubPersonID
		assistdict.update({'assist': assist['c_SubPerson']})
		assistdict.update({'event': 'regular goal'})
		eventlist.append(assistdict.copy())
		
	otherevents = [missedpenalties, penaltygoals, redcards, yellowcards, yellowreds, owngoals]
	eventdictlist = ['missed penalty', 'penalty goal', 'red card', 'yellow card', 'twice yellow', 'own goal']
	for idx, category in enumerate(otherevents):
		for event in category:
			eventdict = CreateSmallEventSummary(event)
			eventdict.update({'event': eventdictlist[idx]})
			eventlist.append(eventdict.copy())
	#Sort the list of all events by minutes so you get a chronological succession of events
	eventlist = sorted(eventlist, key=EventSorter)
	return eventlist

def GameCourseEvents(jsondata):
	assists = []
	regulargoals = []
	missedpenalties = []
	penaltygoals = []
	redcards = []
	yellowreds = []
	yellowcards = []
	owngoals = []
	for event in jsondata['MatchActions']:
		actionset = -1
		actioncode1 = -1
		actioncode2 = -1
		actioncode3 = -1
		if 'n_ActionSet' in event:
			actionset = event['n_ActionSet']==1 #goal
		if 'n_ActionCode' in event:
			actioncode1 = event['n_ActionCode']
		if 'n_ActionCode2' in event:
			actioncode2 = event['n_ActionCode2']
		if 'n_ActionCode3' in event:
			actioncode3 = event['n_ActionCode3']
		#actionset==1 is a goal. actioncode1 is a sum of the ActionCodes found in the Excel documentation
		#we need to check with a 'bitwise or' the result. For example, 
		#actionset = 68 => 64+4 = own + goal = own goal
		#actionset = 76 => 64+8+4 = own + penalty + goal = own goal on penalty shoot
		if actionset==1: #goal
			if actioncode1 & 64:
				owngoals.append(event)
				continue				
			if actioncode1 & 8:
				penaltygoals.append(event)
				continue
			#in nec_vvv_20100807 the assist is not reported as actioncode1
			#so let's add multiple checks for this
			if actioncode1 & 128 or ('n_ActionReasonID' in event and event['n_ActionReasonID'] == 37) or ('c_ActionReason' in event and event['c_ActionReason'].casefold() == "assist"):
				assists.append(event)
				continue
			if actioncode1 == 4: #the most boring goals are just "goals"
				regulargoals.append(event)

		
		if actionset==10: # Missed penalties. Same as before, could use ActionCodes to get more info
			missedpenalties.append(event)
		
		if actionset==3:
			if actioncode1 & 2048:
				yellowcards.append(event)
				
			if actioncode1 & 4096:
				yellowreds.append(event)
				
			if actioncode1 & 8192:
				redcards.append(event)
	eventdict = EventConnect(assists, regulargoals, missedpenalties, penaltygoals, redcards, yellowcards, yellowreds, owngoals)
	return eventdict

def TopicCollection(file):
	with open(file, 'rb') as f:
		jsondata = json.load(f)
	eventlist = GameCourseEvents(jsondata)
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

#import pprint
#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(TopicCollection('./JSONGameData/nec_vvv_20100807.json'))
