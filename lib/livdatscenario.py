import os,sys

sys.path.append("/opt/livingdata/lib")

from livdatbender import *
from libsoma import *
import pygsheets
from bs4 import BeautifulSoup

def get_color_json(dictionary):
	formatted_json=get_formatted_json(dictionary)
	colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
	return colorful_json

def get_formatted_json(dictionary):
	formatted_json=json.dumps(dictionary,sort_keys=True, indent=4)
	return formatted_json

class ScenarioGenerator(DataBender):
	def __init__(self,*args, **kwargs):
		super(ScenarioGenerator,self).__init__(*args, **kwargs)
		self.scenariobookkey=self.config.get("Scenario","bookkey")
		try:
			print "Trying to get scenario book..."
			self.scenariobook=self.gc.open_by_key(self.scenariobookkey)
			self.scenariodef=self.scenariobook.worksheet_by_title("Scenario").get_as_df()
			self.runsheet=self.scenariobook.worksheet_by_title("RunSheet")
			self.scenariossheet=self.scenariobook.worksheet_by_title("Scenarios")
			self.scenariosdf=self.scenariobook.worksheet_by_title("Scenarios").get_as_df()
			self.name=self.config.get("Scenario","name")
			print sorted(list(self.scenariodef.Name))	
			self.scenariossheet.update_row(1,sorted(list(self.scenariodef.Name)))	
			
		except:
			print "Failed to open scenario book by key " + self.scenariobookkey
		
		
	def blank_scenario(self):
		scenario={}
		for row in self.scenariodef.itertuples():
			if row.Type=="read":
				print "Reading cell " + str(row.Cell) + " from RunSheet for field " + row.Name
				scenario[row.Name]=self.scenariobook.worksheet_by_title("RunSheet").cell(str(row.Cell)).value
			if row.Type=="variable":
				print row.Name + " is a variable to be put in " + row.Cell
				scenario[row.Name]=None
			if row.Type=="result":
				print row.Name + " is a result to be put in " + row.Cell
				scenario[row.Name]=None
		return scenario
	def get_scenario(self):
		scenario={}
		for row in self.scenariodef.itertuples():
			print "Reading cell " + str(row.Cell) + " from RunSheet for field " + row.Name +"..."
			scenario[row.Name]=self.scenariobook.worksheet_by_title("RunSheet").cell(str(row.Cell)).value
			print scenario[row.Name]
		return scenario
	def lookup_cell_for_key(self,key):
		return str(self.scenariodef[self.scenariodef.Name==key].Cell.iloc[0])
	def lookup_type_for_key(self,key):
		return str(self.scenariodef[self.scenariodef.Name==key].Type.iloc[0])
	def lookup_unit_for_key(self,key):
		return str(self.scenariodef[self.scenariodef.Name==key].Unit.iloc[0])
	
	def put_scenario(self,scenario):
		for key in scenario.keys():
			if self.lookup_type_for_key(key)=="variable":
				print "Setting variable "+ key + " in cell " + self.lookup_cell_for_key(key) + "to " +str(scenario[key])
				self.runsheet.update_cell(self.lookup_cell_for_key(key),scenario[key])
								
	def append_scenarios(self,scenarios):
		self.scenariosdf=self.scenariosdf.append(scenarios,ignore_index=True).drop_duplicates()
	def put_scenarios(self):
		self.scenariossheet.set_dataframe(self.scenariosdf,(1,1))
	def get_scenarios(self):
		self.scenariosdf=self.scenariossheet.get_as_df()
