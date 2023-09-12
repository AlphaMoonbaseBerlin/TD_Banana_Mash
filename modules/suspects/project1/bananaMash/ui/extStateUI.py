'''Info Header Start
Name : extStateUI
Author : Wieland@AMB-ZEPH15
Saveorigin : bananaMash.toe
Saveversion : 2022.28040
Info Header End'''
from TDStoreTools import StorageManager
import TDFunctions as TDF

class extStateUI:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		# properties
		TDF.createProperty(self, 'SelectedState', value='', dependable=True,
						   readOnly=False)

		TDF.createProperty(self, 'NextConnection', value='', dependable=True,
						   readOnly=False)

		TDF.createProperty(self, 'SelectedConnection', value='', dependable=True,
						   readOnly=False)
	@property 
	def Statemashine(self):
		return self.ownerComp.par.Statemashine.eval()

	def Select_State(self, component):
		self.SelectedState = component.name

	def Reset_Selected_State(self):
		self.SelectedState = ''

	def Delete_Selected_State(self):
		self.Statemashine.DeleteState( self.SelectedState )
		self.Reset_Selected_State()

	def New_State(self):
		self.ownerComp.op('new_state_prompt').Open()
		return
	
	def _New_State(self, name):
		self.SelectedState = self.Statemashine.NewState( name ).name

	def Go_To_Selected(self):
		self.Statemashine.GoTo( self.SelectState )


	def Delete_Connection(self, path):
		self.Statemashine.DeleteConnection( path.split("/")[-2], path.split("/")[-1])

	def Select_Connection(self, path):
		
		self.SelectedConnection = op(path)

	def Interact_Connection(self, component):
		if self.NextConnection == component.name: return
		if self.NextConnection:
			self.Statemashine.NewConnection( self.NextConnection,
											  component.name ) 
			self.Reset_Next_Connection()
			return
		 
		self.NextConnection = component.name
		return

	def Reset_Next_Connection(self):
		self.NextConnection = ''
		return

	def Add_Condition(self):
		path = self.SelectedConnection.path
		self.Statemashine.AddCondition( path.split("/")[-2], path.split("/")[-1])

	def Delete_Condition(self, name):
		path = self.SelectedConnection.path
		self.Statemashine.DeleteCondition( path.split("/")[-2], path.split("/")[-1], name)


	def Go_To(self):
		self.Statemashine.GoToState( self.SelectedState )