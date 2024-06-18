'''Info Header Start
Name : extUIBananaMash
Author : Wieland@AMB-ZEPH15
Saveorigin : bananaMash.toe
Saveversion : 2022.35320
Info Header End'''

def undoable(notification):
	def undoableWrapper(func):
		def wrappedFunction(*args, **kwargs):
			ui.undo.startBlock( notification, enable = True)
			returnValue = func(*args, **kwargs)
			ui.undo.endBlock()
			return returnValue
		return wrappedFunction
	return undoableWrapper

class extUIBananaMash:
	"""
	extUIBananaMash description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

	@property
	def Target(self):
		return self.ownerComp.par.Target.eval()
	
	@undoable("CreatedState")
	def CreateState(self, name, tx, ty):
		newStateComp = self.Target.NewState(name)
		newStateComp.store("_bs_TX", tx)
		newStateComp.store("_bs_TY", ty)
		return newStateComp
	
	@undoable("DeletedSelectedState")
	def DeleteSelectedState(self):
		self.Target.DeleteState( parent.Ui.par.Selectedstate.eval() )
		self.ownerComp.par.Selectedstate.val = parent.Ui.op("findStateComps")[1, "name"]

	@undoable("DeleteSelectedConnection")
	def DeleteSelectedConnection(self):
		self.Target.DeleteConnection( 
				self.ownerComp.par.Selectedstate.eval(),
				self.ownerComp.par.Selectedconnection.eval()
			 )
		self.ownerComp.par.Selectedmode.val = "State"