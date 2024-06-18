'''Info Header Start
Name : extBananaMash
Author : Wieland@AMB-ZEPH15
Saveorigin : bananaMash.toe
Saveversion : 2022.35320
Info Header End'''

class extBananaMash:
	"""
	extBananaMash description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.ownerComp.op("eventEmitter").Attach_Emitter(self)
		self.GoTo( self.ownerComp.par.Initstate.eval() )

	def _publicateEvent(self, event, *args):
		self.ownerComp.op("callbackManager").Do_Callback(
			f"on{event}", *(args + (self.Datastore, self.ownerComp))
		)
		self.Emit(
			f"on{event}", *(args + (self.Datastore, self.ownerComp))
		)
		return
	

	@property
	def CurrentState(self):
		return self.ownerComp.par.Currentstate.eval()
	
	@property
	def NextState(self):
		return self.ownerComp.par.Nextstate.eval()

	@property
	def _states(self) -> COMP:
		return self.ownerComp.op("statesRepo").Repo

	@property
	def Datastore(self) -> COMP:
		return self.ownerComp.op("datastoreRepo").Repo


	def NewState(self, name):
		return self._states.copy(
			self.ownerComp.op("statePrefab"),
			name = name
		)
		return
	
	def NewConnection(self, sourceState:str, targetState:str):
		stateComp = self._getState( sourceState )
		newConnection = stateComp.op("_connections").op(targetState) or stateComp.op("_connections").copy( 
											self.ownerComp.op("connectionPrefab"),
											name = f"{targetState}"
										)
		#newConnection.par.Target.val = targetState
		return newConnection
		

	def DeleteConnection(self, sourceState, targetState):
		targetConnection = self._getState( sourceState ).op("_connections").op(targetState)
		if targetConnection is None: return
		targetConnection.destroy()

	def DeleteState(self, stateName):
		stateComp = self._getState( stateName )
		deleteConnections = []
		for connection in self._states.ops("*/_connections/*"):
			if connection.par.Target.eval() == stateName: deleteConnections.append( connection)
		for deleteConnection in deleteConnections:
			deleteConnection.destroy()
		stateComp.destroy()

	def _getState(self, stateName:str) -> COMP:
		returnState = self._states.op( stateName )
		if returnState is None:
			raise Exception(f"Invalid State currently active. Could not find State {self.ownerComp.par.Currentstate.eval()}. Re-Init statemashine!")
		return returnState
	
	def _runTimer(self, timerComp, length, activate = False):
		timerComp.par.length.val 	= length
		if activate: timerComp.par.active.val 	= True
		timerComp.par.initialize.pulse()
		timerComp.par.start.pulse()

	def Check(self, triggerParameter = None):
		currentStateComp:COMP = self._getState( self.ownerComp.par.Currentstate.eval() )
	
		for connectionContainer in currentStateComp.op("_connections").findChildren( depth = 1, type = baseCOMP):

			if triggerParameter and not tdu.match( connectionContainer.par.Parameterfilter.eval(), triggerParameter): 
				"""The Parameters that triggered the statechange are not in the defined filter for the transition.
				The means we are skipping this transition."""
				continue

			if connectionContainer.op("check").module.check(
				self.Datastore,
				self.ownerComp
			): 
				self._transitionTo( 
					connectionContainer.par.Target.eval(),
					connectionContainer.par.Duration.eval() )
				return True
		
		self._publicateEvent(f"StateCycle", self.CurrentState)
		self._publicateEvent(f"StateCycle__{self.CurrentState}", self.CurrentState)
		return False
	
	def _transitionTo(self, targetState:str, transitionTime:float):

		self.ownerComp.par.Nextstate.val = targetState
		self.ownerComp.op("stateTimer").par.initialize.pulse()

		self._publicateEvent("StateExit", self.CurrentState, self.NextState, transitionTime )
		self._publicateEvent(f"StateExit__{self.CurrentState}", self.CurrentState, self.NextState, transitionTime )

		self._publicateEvent("TransitionStart", self.CurrentState, self.NextState, transitionTime )
		self._publicateEvent(f"TransitionStart__{self.CurrentState}__{self.NextState}", self.CurrentState, self.NextState, transitionTime )
		if self.ownerComp.par.Enforceminimumtransitiontime.eval():
			transitionTime = max( 1 / project.cookRate * 2, transitionTime )
		if transitionTime:
			self.ownerComp.par.Mode.val = "Transition"
			self._runTimer( self.ownerComp.op("transitionTimer"), transitionTime, activate=True )
		else:
			self._TransitionDone()
		return
	
	def GoTo(self, targetState):
		self._transitionTo( targetState, 0)

	def _TransitionDone(self, transitionTime = 0):
		self.ownerComp.op("transitionTimer").par.active.val = False
		newCurrentState 					= self.ownerComp.par.Nextstate.eval()

		self._publicateEvent("StateEnter", self.NextState, self.CurrentState, transitionTime )
		self._publicateEvent(f"StateEnter__{newCurrentState}", self.NextState, self.CurrentState, transitionTime )
		self._publicateEvent("TransitionEnd", self.NextState, self.CurrentState, transitionTime )
		self._publicateEvent(f"TransitionEnd__{self.CurrentState}__{self.NextState}", self.CurrentState, self.NextState, transitionTime )


		self.ownerComp.par.Currentstate.val = newCurrentState
		self.ownerComp.par.Nextstate.val 	= ""
		self.ownerComp.par.Mode.val 		= "State"

		newCurrentStateComp = self._getState( newCurrentState )
		duration = newCurrentStateComp.par.Duration.eval()
		self._runTimer( self.ownerComp.op("stateTimer"), duration )

		if self.ownerComp.par.Checkonstateenter.eval(): self.Check()

		