import sys
sys.path.append(r'C:\\Users\\u1269857\\AppData\\Local\\Continuum\\Anaconda3\\Lib\\site-packages')
sys.path.append('C:\\Program Files\\Anaconda3\\Lib\\site-packages')
import xlrd
import re
import numpy
from enum import Enum, auto
import pdb

class ReferenceType(Enum):
    PRONOUN = auto()
    DEFINITE = auto()
    SEMIDEF = auto()
  

debug = True

def PlayerReferenceModelWithPronouns(playerinfo, jsongamedata, homeaway, gap, **kwargs):
	# Previousmentions is a dict with all the entities that were already mentioned
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
	manager = playerinfo['n_FunctionCode']&16
	
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
				TEMPallgapsthissent  = [mentionedentities[entity] for entity in mentionedentities for mention in mentionedentities[entity]['mentions'] if mention['sentidx']==currentsentidx]
				previousgapsthissent = [mentionedentities[entity] for entity in mentionedentities for mention in mentionedentities[entity]['mentions'] if mention['sentidx']==currentsentidx and mention['gapidx']<currentgapidx and 'c_Person' in mentionedentities[entity]['entityinfo']]
				prev_mentions_this_player_this_sent = [entity for entity in previousgapsthissent if entity['entityinfo']==playerinfo]
				first_occur_this_player_this_sent = len(prev_mentions_this_player_this_sent)==0
				#if previous gaps are not mentions of this player, it is a competing antecedent in same sentence
				if len(previousgapsthissent)!=len(prev_mentions_this_player_this_sent):
					competing_antecedent_same_sent = True
			
			#is there maybe an entity mentioned in a previous sentence?
			TEMPallpreviousmentions = [mention for entity in mentionedentities for mention in mentionedentities[entity]['mentions']]
			previousgaps = [mention for entity in mentionedentities for mention in mentionedentities[entity]['mentions'] if mention['sentidx']<currentsentidx and mention['sentidx']>(currentsentidx-2) and mentionedentities[entity]['entityinfo'] != playerinfo]
			if len(previousgaps)>0:
				competing_antecedent_prev_sent = True
			#else:
			#	pdb.set_trace()
			
			if debug:
				if currentgapidx>0:
					print('Gaps in this sent: '+str(TEMPallgapsthissent))
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
					namepossibilities = PlayerDefiniteDescription(playerinfo)	
					mentiontype = ReferenceType.DEFINITE
				if competing_antecedent_same_sent and currentgapidx>0:
					#2.1 (b)
					#TODO: look at the content of previousgapsthissent
					#is it reasonable to resolve to the same pronoun?
					namepossibilities = PlayerDefiniteDescription(playerinfo)	
					mentiontype = ReferenceType.DEFINITE
			#Figure 2, 2. 
			else:
				if competing_antecedent_same_sent:
					#2.2(a):
					namepossibilities = PlayerDefiniteDescription(playerinfo)	
					mentiontype = ReferenceType.DEFINITE
				else:					
					#2.2(b):
					pdb.set_trace()
					pronoun = 'hem'
					if 'case' in kwargs and kwargs['case'] == GrammaticalCase.NOMINAL:
						pronoun = 'hij'
					if debug:
						namepossibilities = [[pronoun+' ['+playerfullname+']'], [1]]
					else:
						namepossibilities = [[pronoun], [1]]
					mentiontype = ReferenceType.PRONOUN
	
	#this should be Figure 3.5
	if len(namepossibilities)==0:
		pronoun = 'hem'
		pdb.set_trace()
		if 'case' in kwargs and kwargs['case'] == GrammaticalCase.NOMINAL:
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
	
	
def PlayerDefiniteDescription(playerinfo):
	manager = playerinfo['n_FunctionCode']&16
	
	#these references all contain the proper name
	namepossibilities = []
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

	elems = [i[0] for i in namepossibilities]
	probs = [i[1] for i in namepossibilities]
	norm = [float(i) / sum(probs) for i in probs]

	return (elems, norm)
	
	
def PlayerReferenceIndefinite(playerinfo):
	manager = playerinfo['n_FunctionCode']&16
	
	#these references are more than a pronoun, but do not contain a proper name
	referentpossibilities = []
	if not manager:
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
		nationality = playerinfo['c_PersonNatio']
		
	else:
		referentpossibilities.append(['de manager', 10])
		referentpossibilities.append(['de trainer', 10])
		referentpossibilities.append(['de keuzeheer', 1]) #this is from Merijn :) 

	elems = [i[0] for i in referentpossibilities]
	probs = [i[1] for i in referentpossibilities]
	norm = [float(i) / sum(probs) for i in probs]

	return (elems, norm)
	
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