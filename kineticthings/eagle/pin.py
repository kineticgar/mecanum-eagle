class Pin:
    '''Represents a pin belonging to a part. A pin node looks like this:
    <pin name="2" x="5.08" y="0" visible="off" length="short" direction="pas"
        swaplevel="1" rot="R180"/>
    
    The coordinates specified by the pin are relative to the part's origin. For
    example, if a part's X location is 5.08 and it has two pins at X = -5.08
    and X = 4.08, the location of the pins in the schematic would be X = 0 and
    X = 9.16.
    
    I think that pins are referenced from the .sch file like so:
    <pinref part="R1" gate="G$1" pin="2"/>
    '''
    
    def __init__(self, pin_node):
        self._name = pin_node.attrib['name']
        self._x = pin_node.attrib['x']
        self._y = pin_node.attrib['y']
    
    def GetName(self):
        '''Returns the name of the pin as given by the initial part node.'''
        return self._name
    
    def GetX(self):
        '''Returns the X coordinate of the pin relative to the part's origin.'''
        return self._x
    
    def GetY(self):
        '''Returns the Y coordinate of the pin relative to the part's origin.'''
        return self._y
