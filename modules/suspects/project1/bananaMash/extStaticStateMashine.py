'''Info Header Start
Name : extStaticStateMashine
Author : Wieland@AMB-ZEPH15
Version : 0
Build : 2
Savetimestamp : 2023-07-24T22:33:17.832315
Saveorigin : staticStateMashine.14.toe
Saveversion : 2022.28040
Info Header End'''
from sqlite3 import connect
import TDFunctions as TDF
def false_callback(*args, **kwargs):
	return False


class extStaticStateMashine:
	"""
	extStaticStateMashine description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		# properties
		TDF.createProperty(self, 	'Current_State', 
									value = self.ownerComp.par.Defaultstate.eval() , 
									dependable=True,
						   			readOnly=False )
		self.state_timer = self.ownerComp.op('stateTimer')
		self.ownerComp.op("Emitter").Attach_Emitter(self)
		self.GoToState = self.Go_To_State
		self.callback = self.ownerComp.op('callbackManager')
		self.Check = self.Update_State
		self.states = self.Get_States_Dict()
		if self.ownerComp.par.Autocontinueonstateenter.eval(): self.Update_State()		

	def Do_Callback(self, name, *args, **kwargs):
		self.callback.Do_Callback( f"On{name}", *args, **kwargs)
		self.Emit( name, *args, **kwargs)

	@property
	def stateholder(self):
		return self.ownerComp.op("state_repo_maker").Repo

	def Get_States_Dict( self ):
		return { state.name : self.parse_state(state) for state in self.stateholder.findChildren(depth = 1) }
		
	def parse_state(self, state):
		return { connection.name : self.read_connection(connection) for connection in state.findChildren(depth = 1) }

	def Update_Connection(self, connection):
		self.states[ connection.parent().name ][ connection.name ] = self.read_connection(connection)
	
	def read_connection(self, connection):
		return connection

	def evaluate_cell(self, value):
		try:
			return eval( value )
		except:
			return value


	def execute_statechange_callbacks(self, new_state):
		self.Do_Callback( "StateExit", self.Current_State, new_state)
		self.Do_Callback( "StateEnter", self.Current_State, new_state, self.Get_State_Time( new_state ) )

		self.Do_Callback( f"{self.Current_State}Exit", self.Current_State, new_state )
		self.Do_Callback( f"{new_state}Enter", self.Current_State, new_state, self.Get_State_Time( new_state ) )

	def execute_statecycle_callback(self):
		self.Do_Callback( "StateCycle", self.Current_State, self.Get_State_Time( self.Current_State) )
		self.Do_Callback( f"{self.Current_State}Cycle", self.Get_State_Time( self.Current_State) )

	def Get_State_Time(self, state):
		return self.stateholder.op(state).par.Length.eval() if self.stateholder.op(state) else 0

	def start_timer(self, state):
		self.state_timer.par.length = self.Get_State_Time ( state )
		self.state_timer.par.start.pulse()

	def Reset_Timer(self):
		self.start_timer( self.Current_State )

	def Go_To_State(self, new_state):
		if self.Current_State == new_state: return self.Reset_Timer()
		self.execute_statechange_callbacks( new_state )
		self.Current_State = new_state
		if self.ownerComp.par.Timeactive.eval(): return self.start_timer( new_state )
		if self.ownerComp.par.Autocontinueonstateenter.eval(): self.Update_State()
		return

	def Update_State( self ):
		new_state = self.Check_Conditions()
		if not new_state: return self.execute_statecycle_callback()
		self.GoToState(new_state)
		return new_state

	def New_State(self, name):
		new_state = self.stateholder.copy( self.ownerComp.op('statetemplate'), name = name )
		self.states[new_state.name] = self.parse_state( new_state )
		return new_state
		
	def Print_States(self):
		debug( self.states )
		
	def Delete_State(self, name):
		for deleteme in self.stateholder.findChildren( name = name, maxDepth = 3):
			try:
				del self.states[ deleteme.parent().name ][ deleteme.name ]
			except:
				pass
			deleteme.destroy()
		del self.states[name]

	def New_Connection(self, start_state, to_state):
		if self.stateholder.op(start_state).op(to_state): return

		new_connection = self.stateholder.op(start_state).copy(self.ownerComp.op("connection_callback"), name = to_state)
		self.states[start_state][to_state] = new_connection
	
	def Delete_Connection( self, state, target):
		self.stateholder.op(state).op(target).destroy()
		del self.states[state][target]
		return

	@property
	def condition_comp(self):
		return self.ownerComp.op("repo_maker").Repo

	def Check_Conditions( self ):
		if self.Current_State not in self.states: return None
		for connection_key in self.states[ self.Current_State ]:
			check_function = getattr( self.states[ self.Current_State ][ connection_key ].module , "check", false_callback)
		
			if not check_function( self.Current_State, connection_key, self.condition_comp ): continue
			return connection_key

