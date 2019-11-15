import xlrd
import json

def ConvertWorkbookToDict(db):
	workbook = xlrd.open_workbook(db)
	worksheets = workbook.sheet_names()[0]
	outputdict = {}
	# Open the excel file
	worksheet = workbook.sheet_by_name(worksheets)
	#Get all the columns
	for col in range(worksheet.ncols):
		#Append the first value to get the type of template
		template_name = worksheet.cell_value(0, col)
		#Append the non-empty values after the first value to get the templates
		newcol = worksheet.col_values(col)
		templates = []
		for idx, val in enumerate(newcol):
			if (idx != 0) and (val != ''):
				templates.append(val)
			if val == '':
				break
		outputdict[template_name] = templates
	return outputdict

files = ['Templates GoalgetterLoss.xlsx', 'Templates GoalgetterNeutral.xlsx', 'Templates GoalgetterTie.xlsx', 'Templates GoalgetterWin.xlsx']

for excelfilename in files:
	dict = ConvertWorkbookToDict(excelfilename)
	jsonfilename = excelfilename.replace(' Goalgetter','').replace('xlsx','json')
	with open(jsonfilename, 'w', encoding="utf-8") as f:
		json.dump(dict, f, indent=4)
