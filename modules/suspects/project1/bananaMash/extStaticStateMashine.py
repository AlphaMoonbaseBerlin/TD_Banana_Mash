
'''Info Header Start
Name : extStaticStateMashine
Author : Wieland@AMB-ZEPH15
Saveorigin : bananaMash.toe
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

		
		self.CurrentState = tdu.Dependency( self.ownerComp.par.Defaultstate.eval() )

		self.stateTimer = self.ownerComp.op('stateTimer')
		self.ownerComp.op("Emitter").Attach_Emitter(self)
		self.GoToState = self.GoToState
		self.callback = self.ownerComp.op('callbackManager')
		self.Check = self.UpdateState
		self.states = self.GetStatesDict()
		if self.ownerComp.par.Autocontinueonstateenter.eval(): self.UpdateState()		

	def Do_Callback(self, name, *args, **kwargs):
		self.callback.Do_Callback( f"On{name}", *args, **kwargs)
		self.Emit( name, *args, **kwargs)

	@property
	def States(self):
		return self.ownerComp.op("state_repo_maker").Repo

	@property
	def Store(self):
		return self.ownerComp.op("repo_maker").Repo

	def GetStatesDict( self ):
		return { state.name : self.parseState(state) for state in self.States.findChildren(depth = 1) }
		
	def parseState(self, state):
		return { connection.name : self.readConnection(connection) for connection in state.findChildren(depth = 1) }

	def UpdateConnection(self, connection):
		self.states[ connection.parent().name ][ connection.name ] = self.readConnection(connection)
	
	def readConnection(self, connection):
		return connection


	def executeStatechangeCallbacks(self, newState):
		self.Do_Callback( "StateExit", 
				   self.CurrentState.val, 
				   newState,
				   self.ownerComp,
				   self.Store)
		self.Do_Callback( "StateEnter", 
				   self.CurrentState.val, 
				   newState, 
				   self.GetStateTime( newState ),
				   self.ownerComp,
				   self.Store )

		self.Do_Callback( f"{self.CurrentState.val}Exit", 
				   self.CurrentState.val, 
				   newState,
				   self.ownerComp,
				   self.Store )
		self.Do_Callback( f"{newState}Enter", 
				   self.CurrentState.val, 
				   newState, self.GetStateTime( newState ),
				   self.ownerComp,
				   self.Store )

	def executeStatecycleCallbacks(self):
		self.Do_Callback( "StateCycle", 
				   self.CurrentState.val, 
				   self.GetStateTime( self.CurrentState.val),
				   self.ownerComp,
				   self.Store )
		self.Do_Callback( f"{self.CurrentState.val}Cycle", 
				   self.CurrentState.val,
				   self.GetStateTime( self.CurrentState.val),
				   self.ownerComp,
				   self.Store )

	def GetStateTime(self, state):
		return self.States.op(state).par.Length.eval() if self.States.op(state) else 0

	def startTimer(self, state):
		self.stateTimer.par.length = self.GetStateTime ( state )
		self.stateTimer.par.start.pulse()

	def ResetTimer(self):
		self.startTimer( self.CurrentState.val )

	def GoToState(self, newState):
		if self.CurrentState.val == newState: return self.ResetTimer()
		self.executeStatechangeCallbacks( newState )
		self.CurrentState.val = newState
		if self.ownerComp.par.Timeactive.eval(): return self.startTimer( newState )
		if self.ownerComp.par.Autocontinueonstateenter.eval(): self.UpdateState()
		return

	def UpdateState( self ):
		new_state = self.Check_Conditions()
		if not new_state: return self.executeStatecycleCallbacks()
		self.GoToState(new_state)
		return new_state

	def NewState(self, name):
		new_state = self.States.copy( self.ownerComp.op('statetemplate'), name = name )
		self.states[new_state.name] = self.parseState( new_state )
		return new_state
		
	def PrintStates(self):
		debug( self.states )
		
	def DeleteState(self, name):
		for deleteme in self.States.findChildren( name = name, maxDepth = 3):
			try:
				del self.states[ deleteme.parent().name ][ deleteme.name ]
			except:
				pass
			deleteme.destroy()
		del self.states[name]

	def NewConnection(self, start_state, to_state):
		if self.States.op(start_state).op(to_state): return

		new_connection = self.States.op(start_state).copy(self.ownerComp.op("connection_callback"), name = to_state)
		self.states[start_state][to_state] = new_connection
	
	def DeleteConnection( self, state, target):
		self.States.op(state).op(target).destroy()
		del self.states[state][target]
		return

	

	def Check_Conditions( self ):
		if self.CurrentState.val not in self.states: return None
		for connection_key in self.states[ self.CurrentState.val ]:
			check_function = getattr( self.states[ self.CurrentState.val ][ connection_key ].module , "check", false_callback)
		
			if not check_function( self.CurrentState.val, connection_key, self.Store ): continue
			return connection_key

