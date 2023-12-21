'''Info Header Start
Name : utilityClasses
Author : Wieland@AMB-ZEPH15
Saveorigin : bananaMash.toe
Saveversion : 2022.28040
Info Header End'''

from dataclasses import dataclass, field

@dataclass
class State:
    _sourceComp : baseCOMP
    name : str = field( default = property( lambda self: self._sourceComp.name), init = False )
    
@dataclass
class Transition:
    source  : State
    target  : State
    length  : float
