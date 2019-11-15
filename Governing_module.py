from Topic_collection_module import TopicCollection
from Lookup_module import ArrangeDatabase, ReadTemplates, GeneralTemplates, GameCourseTemplates, GameStatisticsTemplates
from Template_selection_module import GeneralTemplateSelection, GameCourseTemplateSelection, GameStatisticsTemplateSelection
from Template_filler_module import TemplateReplacement, TemplateReplacementWithPronouns
from Text_collection_module import TextCollection
import pickle
import json

def GeneralEvents():
	#General events in the current system consist of three sentences: a title, a general sentence describing whether the focus team won/tied/lost,
	#A general sentence detailing the final score.
	return ['title', 'general', 'final_score']

def TopicWalk(file):
	# The game data is important for many rules in the RuleSet, for getting the right databases, and much more
	with open(file, 'rb') as f:
		jsongamedata = json.load(f)	   

	topics = TopicCollection(jsongamedata)
	# Get three lists for the three paragraphs the current system uses: General, Game Course and Game Statistics
	general, gamecourse, gamestatistics = (GeneralEvents(),) + topics
	if len(gamestatistics) == 0:
		gamestatistics = [{'event': None}]

	# Get the right databases files for all report targets
	dbtuples = ArrangeDatabase(jsongamedata)
	reporttargets = [tuple[1] for tuple in dbtuples]
	legends = {}
	templates = {}
	
	# Get all the templates and categories
	# legends and templates are now dictionaries, and the keys are 'home', 'away' and 'neutral'
	# (or whatever is contained in reporttargets)
	for tuple in dbtuples:
		reporttarget = tuple[1]
		legends[reporttarget], templates[reporttarget] = ReadTemplates(tuple[0])
	
	
	# Collect all the home, away and neutral templates
	templatedicts = {}
	templatetexts = {}
	for reporttarget in reporttargets:
		templatelist = []
		# Get all possible topics for general first
		for generaltopic in general:		
			possiblelegend, possibletemplates = GeneralTemplates(generaltopic, legends[reporttarget], templates[reporttarget])
			#ToDo: is this correct? it passes "home" to GeneralTEmplateSelection for neutral teams, but... isn't home and away the same also for neutral templates?
			homeaway = reporttarget
			if homeaway == "neutral":
				homeaway = "home"
			template = GeneralTemplateSelection(generaltopic, possiblelegend, possibletemplates, gamecourse, gamestatistics, jsongamedata, homeaway)
			templatelist.append(template)
		
		# Get separate gamecourses since the gamecourselist can be modified
		individualgamecourse = gamecourse.copy()
		homeaway = reporttarget
		if homeaway == "neutral":
			homeaway = "home"	
		# And then for the gamecourse
		for idx, gamecoursetopic in enumerate(gamecourse):
	
			#The subsequent goals template merges events and shortens the gamecourse, so only look for a template if there is the need for it in the gamecourselist
			if idx < len(individualgamecourse):
				possiblelegend, possibletemplates = GameCourseTemplates(individualgamecourse[idx], legends[reporttarget], templates[reporttarget],reporttarget)
				individualgamecourse, template = GameCourseTemplateSelection(individualgamecourse[idx], possiblelegend, possibletemplates, individualgamecourse, jsongamedata, homeaway, idx, templatelist)
				templatelist.append(template)
		#And then for the game statistics
		for idx, gamestatisticstopic in enumerate(gamestatistics):
			#If this is not the first yellow card/twice yellow card in the list, than the event is already covered and altered by the previous event
			#So, if the eventtype is not a dict, skip it
			if type(gamestatistics[idx]) == dict:
				possiblelegend, possibletemplates = GameStatisticsTemplates(gamestatisticstopic, legends[reporttarget], templates[reporttarget])
				template = GameStatisticsTemplateSelection(gamestatistics[idx], possiblelegend, possibletemplates, gamestatistics, jsongamedata, homeaway, idx, templates[reporttarget])
				templates[reporttarget].append(template)

		# Save the templatelist, which you can use to get new templates every iteration
		with open('templates'+reporttarget+'.p', 'wb') as f:
			pickle.dump(templatelist, f)
		
		# Filter out all the empty strings from gamestatistics	
		gamestatistics = list(filter(None, gamestatistics))
		allevents = general + individualgamecourse + gamestatistics
		previousgaplist = [''] * len(templatelist)
		mentionedentities = {}
		
		for idx, val in enumerate(templatelist):
			if idx <= 1:
				lastgap = []
			else:
				lastgap = previousgaplist[idx - 1]
			templatelist[idx], previousgaplist[idx] = TemplateReplacementWithPronouns(jsongamedata, homeaway, templatelist[idx], event=allevents[idx], gamecourselist=individualgamecourse, previousgaplist=lastgap, gamestatisticslist=gamestatistics, eventlist=allevents, idx=idx, previous_gaps=previousgaplist, mentionedentities=mentionedentities)
		templatetext, templatedict = TextCollection(templatelist, jsongamedata, reporttarget, len(general), len(individualgamecourse), len(gamestatistics))

		templatedicts[reporttarget] = templatedict.copy()
		templatetexts[reporttarget] = templatetext
		
	return templatetexts['home'], templatetexts['away'], templatetexts['neutral'], templatedicts, jsongamedata
