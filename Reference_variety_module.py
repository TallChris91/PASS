import sys
import xlrd
import re
import numpy
from enum import Enum, auto
import pdb
import json
import pprint

class ReferenceType(Enum):
    PRONOUN = auto()
    DEFINITE = auto()
    SEMIDEF = auto()
  

debug = False
pp = pprint.PrettyPrinter(indent=4)

def PlayerReferenceModelWithPronouns(playerinfo, jsongamedata, homeaway, gap, **kwargs):
	# mentionedentities is a dict with all the entities that were already mentioned
	# Name (TODO: ID) is the key 
	# The value is an array, and every time I mention an entity I add to this array
	# a dict such that :
	# {
	#  sentidx : sentence idx of this mention
	#  gapidx : which gap of the sentence
	#  mention : string of the current mention (e.g. 'Francesco Totti')
	#  entityinfo : information about the club or player mentioned
	#  mentiontype : ReferenceType ('definite'|'semi'|'pronoun')
	# }
	mentionedentities = kwargs['mentionedentities']
	currentsentidx = kwargs['idx']
	currentgapidx = kwargs['gapidx']
	#First find the player's information by looking up the player

	playerfullname = playerinfo['c_Person']

	namepossibilities = []

	if debug:
		print('\n###Pronoun generation algo:###')
		print('Current template: '+kwargs['templatetext'])
		print('Current player: '+playerfullname)
		print('Current event: '+str(kwargs['event']))

	
	if (playerfullname not in mentionedentities):
		if debug:
			print("First mention of this player")
		#If there is no previous mention of the player, use a definite description
		namepossibilities = PlayerDefiniteDescription(playerinfo)
		#mentionedentities[playerfullname] is an array of each time the player is mentioned
		mentionedentities[playerfullname] = {'mentions':[], 'entityinfo':playerinfo}
		mentiontype = ReferenceType.DEFINITE
	else:
		#otherwise check WHEN it was mentioned last time as a definite entity
		previousmentions = mentionedentities[playerfullname]['mentions']
		idxlastmention = previousmentions[-1]['sentidx']
		
		#Adapted from McCoy and Strube 2002, page 68
		#Figure 3, 1. :
		if abs(idxlastmention-currentsentidx)>2:
			namepossibilities = PlayerDefiniteDescription(playerinfo)	
			mentiontype = ReferenceType.DEFINITE
		#Figure 3, 2. never happens in PASS so not implemented			
		#Figure 3, 3. thread change = different "topic" (title/stuff) - not implemented
		#Figure 3, 4:
		else:
			#find if there is a competing antecedent
			competing_antecedent_same_sent = False
			competing_antecedent_prev_sent = False
			first_occur_this_player_this_sent = True
			if currentgapidx>0:
				#this is not the first gap in this sentence. Is the previous gap also a person?
				previousgapsthissent = [mentionedentities[entity] for entity in mentionedentities for mention in mentionedentities[entity]['mentions'] if mention['sentidx']==currentsentidx and mention['gapidx']<currentgapidx and 'c_Person' in mentionedentities[entity]['entityinfo']]
				prev_mentions_this_player_this_sent = [entity for entity in previousgapsthissent if entity['entityinfo']==playerinfo]
				first_occur_this_player_this_sent = len(prev_mentions_this_player_this_sent)==0
				#if previous gaps are not mentions of this player, it is a competing antecedent in same sentence
				if len(previousgapsthissent)!=len(prev_mentions_this_player_this_sent):
					competing_antecedent_same_sent = True
			
			#is there maybe an entity mentioned in a previous sentence?
			previousgaps = [mention for entity in mentionedentities for mention in mentionedentities[entity]['mentions'] if mention['sentidx']<currentsentidx and mention['sentidx']>(currentsentidx-2) and mentionedentities[entity]['entityinfo'] != playerinfo]
			if len(previousgaps)>0:
				competing_antecedent_prev_sent = True
			#else:
			#	pdb.set_trace()
			
			if debug:
				if currentgapidx>0:
					print('prev_mentions_this_player_this_sent: '+str(prev_mentions_this_player_this_sent))
				print('Index of this gap:'+str(currentgapidx))
				if 'previousgaps' in locals():
					print('Previous gaps this sent'+str(previousgaps))
				print('Previous mentions in general: '+str(mentionedentities))
				print("Is player's first mention in this sent? "+str(first_occur_this_player_this_sent))
				print("Is there a competing antecedent in this sent? "+str(competing_antecedent_same_sent))
				print("Is there a competing antecedent in previous sent? "+str(competing_antecedent_prev_sent))
			
			#Figure 2, 1. 
			if first_occur_this_player_this_sent:
				if competing_antecedent_prev_sent:
					#2.1 (a)
					#TODO: try to use referring expression generation here
					namepossibilities = PlayerDefiniteDescription(playerinfo)	
					mentiontype = ReferenceType.DEFINITE
				if competing_antecedent_same_sent and currentgapidx>0:
					#2.1 (b)
					#TODO: look at the content of previousgapsthissent
					#is it reasonable to resolve to the same pronoun?
					namepossibilities = PlayerReferringExpression(playerinfo, jsongamedata, homeaway, gap, **kwargs)
					
					#namepossibilities = PlayerDefiniteDescription(playerinfo)	
					mentiontype = ReferenceType.DEFINITE
			#Figure 2, 2. 
			else:
				if competing_antecedent_same_sent:
					#2.2(a):
					namepossibilities = PlayerReferringExpression(playerinfo, jsongamedata, homeaway, gap, **kwargs)
					
					#namepossibilities = PlayerDefiniteDescription(playerinfo)	
					mentiontype = ReferenceType.DEFINITE
				else:					
					#2.2(b):
					#TODO: check that the template just before the gap does not contain "het"?
					#example: Na 47 minuten spelen was het hij die op aangeven van Atiba Hutchinson
					pronoun = 'hem'
					if 'case' in kwargs and kwargs['case'] == 'nominal':
						pronoun = 'hij'
					if debug:
						namepossibilities = [[pronoun+' ['+playerfullname+']'], [1]]
					else:
						namepossibilities = [[pronoun], [1]]
					mentiontype = ReferenceType.PRONOUN
	
	#this should be Figure 3.5
	if len(namepossibilities)==0:
		pronoun = 'hem'
		#pdb.set_trace()
		#TODO: check that the template just before the gap does not contain "het"?
		if 'case' in kwargs and kwargs['case'] == 'nominal':
			pronoun = 'hij'
		if debug:
			namepossibilities = [[pronoun+' ['+playerfullname+']'], [1]]
		else:
			namepossibilities = [[pronoun], [1]]
		mentiontype = ReferenceType.PRONOUN
	namechoice = numpy.random.choice(namepossibilities[0], p=namepossibilities[1])
	nametuple = (playerfullname, namechoice)
	mentionedentities[playerfullname]['mentions'].append({ 'sentidx': currentsentidx,
									   'gapidx': currentgapidx,
									   'mention': namechoice,
									   'mentiontype': mentiontype})
	if debug:
		print ('I will use: '+str(nametuple))
	return nametuple


def RefereeReferenceModel(refereeinfo, jsongamedata, homeaway, gap, **kwargs):
	# mentionedentities is a dict with all the entities that were already mentioned
	# Name (TODO: ID) is the key 
	# The value is an array, and every time I mention an entity I add to this array
	# a dict such that :
	# {
	#  sentidx : sentence idx of this mention
	#  gapidx : which gap of the sentence
	#  mention : string of the current mention (e.g. 'Francesco Totti')
	#  entityinfo : information about the club or player mentioned
	#  mentiontype : ReferenceType ('definite'|'semi'|'pronoun')
	# }
	mentionedentities = kwargs['mentionedentities']
	currentsentidx = kwargs['idx']
	currentgapidx = kwargs['gapidx']

	refereefullname = refereeinfo['c_Person']
	
	namepossibilities = []

	if debug:
		print('\n###Referee naming algo:###')
		print('Current template: '+kwargs['templatetext'])
		print('Referee: '+refereefullname)
	
	if (refereefullname not in mentionedentities):
		if debug:
			print("First mention of the referee")
		#If there is no previous mention of the player, use a definite description
		namepossibilities = [['arbiter '+refereefullname, 'scheidsrechter '+refereefullname], [0.5, 0.5]]
		mentionedentities[refereefullname] = {'mentions':[], 'entityinfo':refereeinfo}
	else:
		lastname = refereeinfo['PersonLastName']
		namepossibilities = [['arbiter '+lastname, 'scheidsrechter '+lastname, lastname, 'de arbiter', 'de scheidsrechter'], [0.2, 0.2, 0.2, 0.2, 0.2]]
	mentiontype = ReferenceType.DEFINITE
	namechoice = numpy.random.choice(namepossibilities[0], p=namepossibilities[1])
	nametuple = (refereefullname, namechoice)
	mentionedentities[refereefullname]['mentions'].append({ 'sentidx': currentsentidx,
									   'gapidx': currentgapidx,
									   'mention': namechoice,
									   'mentiontype': mentiontype})
	if debug:
		print ('I will use: '+str(nametuple))
	return nametuple
	
def PlayerDefiniteDescription(playerinfo):
	#these references all contain the proper name
	namepossibilities = []
	fullname = playerinfo['c_Person']
	namepossibilities.append([fullname, 10])
	firstname = playerinfo['c_PersonFirstName']
	lastname = playerinfo['c_PersonLastName']
	namepossibilities.append([lastname, 10])
	if not isManager(playerinfo):
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

	elems = [i[0] for i in namepossibilities]
	probs = [i[1] for i in namepossibilities]
	norm = [float(i) / sum(probs) for i in probs]

	return (elems, norm)
	

def PlayerReferenceIndefinite(playerinfo):
	
	#these references are more than a pronoun, but do not contain a proper name
	referentpossibilities = []
	if not isManager(playerinfo):
		role = playerinfo['n_FunctionCode']
		if role&1: #keeper
			referentpossibilities.append(['de doelman', 5])
			referentpossibilities.append(['de keeper', 5])
		elif role&2: #defender
			referentpossibilities.append(['de verdediger', 5])
		elif role&4: #midfielder
			referentpossibilities.append(['de middenvelder', 5])
		elif role&8: #attacker
			referentpossibilities.append(['de aanvaller', 5])
			referentpossibilities.append(['de spits', 5])
	else:
		referentpossibilities.append(['de manager', 10])
		referentpossibilities.append(['de trainer', 10])
		referentpossibilities.append(['de keuzeheer', 1]) #this is from Merijn :) 

	return referentpossibilities
	
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
			homeOrAway = 1
			if 'de thuisploeg' not in previousreference:
				namepossibilities.append(['de thuisploeg', 10])
		else:
			homeOrAway = -1
			if ('de uitploeg') not in previousreference:
				namepossibilities.append(['de uitploeg', 10])

		for person in jsongamedata['MatchLineup']:
			if isManager(person) and person['n_HomeOrAway']==homeOrAway:
				manager = person['c_Person']
				managerinfo = person
				break
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
	
	#add manager to mentioned entities to avoid ambiguous pronouns
	if "van manager" in namechoice:
		mentionedentities = kwargs['mentionedentities']
		if manager not in mentionedentities:
			mentionedentities[manager] = {'mentions':[], 'entityinfo':managerinfo}
		mentionedentities[manager]['mentions'].append(
									{ 'sentidx': kwargs['idx'],
									   'gapidx': kwargs['gapidx'],
									   'mention': namechoice,
									   'mentiontype': ReferenceType.DEFINITE}
								)		
	
	nametuple = (club, namechoice)
	return nametuple
	
#TODO: seems like PlayerReferringExpression and disambiguatingReferringExpression could
#      either be joined or at least renamed to be more clear
def PlayerReferringExpression(playerinfo, jsongamedata, homeaway, gap, **kwargs):
	mentionedentities = kwargs['mentionedentities']
	currentsentidx = kwargs['idx']
	currentgapidx = kwargs['gapidx']

	playerfullname = playerinfo['c_Person']

	#Format: [(Possibility1, ChoiceProb), (Possibility2, ChoiceProb) 
	namepossibilities = []

	if debug:
		print('\n###Referring expression generation:###')
		print('Current template: '+kwargs['templatetext'])
		print('Current player: '+playerfullname)

	#find the competing antecedent
	competing_antecedent_same_sent = False
	competing_antecedent_prev_sent = False
	first_occur_this_player_this_sent = True
	if currentgapidx>0:
		#this is not the first gap in this sentence. Is the previous gap also a person (and not this player)?
		previousgapsthissent = [mentionedentities[entity] for entity in mentionedentities for mention in mentionedentities[entity]['mentions'] if mention['sentidx']==currentsentidx and mention['gapidx']<currentgapidx and 'c_Person' in mentionedentities[entity]['entityinfo'] and  mentionedentities[entity]['entityinfo']!=playerinfo]
		prev_mentions_this_player_this_sent = [entity for entity in previousgapsthissent if entity['entityinfo']==playerinfo]
		first_occur_this_player_this_sent = len(prev_mentions_this_player_this_sent)==0
		#if previous gaps are not mentions of this player, it is a competing antecedent in same sentence
		if len(previousgapsthissent)>0:
			competing_antecedent_same_sent = True
	
	#TODO: If this is NOT the first occurrence of this player in this sent, 
	#      and there is a competing antecedent, I can disambiguate these two players
	
	#Is there maybe an entity mentioned in a previous sentence?
	previoussentgaps = [mentionedentities[entity] for entity in mentionedentities for mention in mentionedentities[entity]['mentions'] if mention['sentidx']<currentsentidx and mention['sentidx']>(currentsentidx-2) and mentionedentities[entity]['entityinfo'] != playerinfo]
	if len(previoussentgaps)>0:
		competing_antecedent_prev_sent = True
	
	if debug:
		if currentgapidx>0:
			print('prev_mentions_this_player_this_sent: '+str(prev_mentions_this_player_this_sent))
		print('Index of this gap:'+str(currentgapidx))
		print('Prev gaps in the current sentence: ')
		pp.pprint(previousgapsthissent)
#		if 'previoussentgaps' in locals():
		print('Gaps in the previous sentence: ')
		pp.pprint(previoussentgaps)
		#print('Previous mentions in general: ')
		#pp.pprint([{player: mentionedentities[player]['mentions']} for player in mentionedentities])
		print("Is player's first mention in this sent? "+str(first_occur_this_player_this_sent))
		print("Is there a competing antecedent in this sent? "+str(competing_antecedent_same_sent))
		print("Is there a competing antecedent in previous sent? "+str(competing_antecedent_prev_sent))
	otherplayersinfo = previousgapsthissent + previoussentgaps
	return disambiguatingReferringExpression(playerinfo,otherplayersinfo)
	
	
def isManager(playerinfo):
	return playerinfo['n_FunctionCode']&16

def disambiguatingReferringExpression(targetplayerinfo,otherplayersinfo, **kwargs):
	#captain, role, shirt number, nationality
	listoffeatures = ['b_Captain', 'c_Function', 'n_ShirtNr', 'c_PersonNatioShort']
	featureisdisambiguating = [True, True, True, True]
	prevteamdisambiguates = True
	formerteamtarget = ""
	
	targetplayerdata = getPlayerData(targetplayerinfo,**kwargs)
	#get the last team of the player
	currentteamtarget = targetplayerinfo['c_Team']
	for season in reversed(targetplayerdata['PlayerLeague']):
		if season['c_Team'] != currentteamtarget:
			formerteamtarget = season['c_Team']
			break
	#if we have no info...
	if formerteamtarget == '':
		prevteamdisambiguates = False
	
	#if our targetplayer is not a captain, this is not a good feature
	if targetplayerinfo['b_Captain']==False:
		listoffeatures.pop(0)
		featureisdisambiguating.pop(0)
	
	for player in otherplayersinfo:
		for idx,feature in enumerate(listoffeatures):
			if targetplayerinfo[listoffeatures[idx]]==player['entityinfo'][listoffeatures[idx]]:
				featureisdisambiguating[idx] = False
		playerdata = getPlayerData(player['entityinfo'],**kwargs)
		previousteams = [season['c_Team'] for seasons in targetplayerdata['PlayerLeague']]
		if formerteamtarget in previousteams:
			prevteamdisambiguates = False
	
	#Format: [(Referent1, ChoiceProbWeight), ...]
	disambiguatedReferents = []
	roles = [reference[0] for reference in PlayerReferenceIndefinite(targetplayerinfo)]
	for idx,featureworks in enumerate(featureisdisambiguating):
		if featureworks:
			featurename = listoffeatures[idx]
			if featurename=='b_Captain':
				disambiguatedReferents.append(['de aanvoerder', 10])
			if featurename=='n_ShirtNr':
				disambiguatedReferents.append(['nummer '+str(targetplayerinfo['n_ShirtNr'])+'',2])
			if featurename=='c_Function':
				disambiguatedReferents = disambiguatedReferents + PlayerReferenceIndefinite(targetplayerinfo)
			if featurename=='c_PersonNatioShort':
				countryInfo = getCountryNames(targetplayerinfo[featurename],**kwargs)
				if countryInfo:
					disambiguatedReferents.append(['de '+countryInfo['Demonym'], 10]) #de Duits
					disambiguatedReferents.append(['de '+countryInfo['Adjective']+'e speler', 8])
					#TODO: This is actually disambiguating on TWO characteristics
					#de Duitse middenvelder
					for role in roles:
						disambiguatedReferents.append([role.replace('de ','de '+countryInfo['Adjective']+'e ',1), 7])
	if prevteamdisambiguates:
		disambiguatedReferents.append(['de voormalig '+formerteamtarget+' speler', 5])
		disambiguatedReferents.append(['de voormalig speler van ' +formerteamtarget, 5])
		for role in roles:
			role = role.replace('de ','',1)
			disambiguatedReferents.append(['de voormalig '+role+' van ' +formerteamtarget, 5])
			disambiguatedReferents.append(['de voormalig '+formerteamtarget+' '+role, 5])
	
	elems = [i[0] for i in disambiguatedReferents]
	probs = [i[1] for i in disambiguatedReferents]
	norm = [float(i) / sum(probs) for i in probs]
	
	if debug:
		for idx,elem in enumerate(elems):
			elems[idx] = "|"+elem+"| ["+targetplayerinfo['c_Person']+"]"
	
	return (elems, norm)


#loads the player data (former clubs and previous seasons) from file if not already in kwargs
#otherwise just returns it
def getPlayerData(playerinfo,**kwargs):
	if 'jsonplayerdata' not in kwargs:
			kwargs['jsonplayerdata'] = {}
	if playerinfo['n_PersonID'] not in kwargs['jsonplayerdata']:
		#read file and put it in there
		playerfile = "./JSONPlayerData/player_"+str(playerinfo['n_PersonID'])+".json"
		try:
			with open(playerfile, 'rb') as f:
				jsonplayerdata = json.load(f)
				#remove duplicate info
				del jsonplayerdata['PlayerInfo'] 
				kwargs['jsonplayerdata']['n_PersonID'] = jsonplayerdata
		except:
			print ("Error while opening "+playerfile+" ", sys.exc_info()[0])
			kwargs['jsonplayerdata']['n_PersonID'] = {  "PlayerCup": [],
												        "PlayerInternational": [],
														"PlayerInternationalclub": [],
														"PlayerLeague": []
													 }
	return kwargs['jsonplayerdata']['n_PersonID']
	
	
def getCountryNames(countryShortForm,**kwargs):
	if 'countryData' not in kwargs:
		kwargs['countryData'] = {}
		try:
			with open('./Databases/Nationalities.tsv','r') as f:
				for line in f:
					ShortForm,CountryName,Adjective,Demonym = line.strip().split('\t')
					info = { 	'CountryName': CountryName, 
						'Adjective': Adjective,
						'Demonym': Demonym
					}
					kwargs['countryData'][ShortForm] = info
		except:
			print("Error while opening ./Databases/Nationalities.tsv", sys.exc_info()[1])
	if countryShortForm not in kwargs['countryData']:
		kwargs['countryData'][countryShortForm] = {}
	return kwargs['countryData'][countryShortForm]
	