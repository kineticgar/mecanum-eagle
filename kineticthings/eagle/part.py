from pin import Pin
from library import Library

class Part:
    '''Represents a part in an EAGLE schematic.
    
    Parts are referenced in the EAGLE .sch file like so:
    <part name="R1" library="rcl" deviceset="R-US_" device="0204/2V"/>
    
    Additional information has to come from looking up the deviceset ID in the
    foreign library file (in this case, rcl.lbr). The Library object takes care
    of locating this file and retrieving the additional details. Currently, we
    only use the symbol node in the library file to generate a list of pins.
    The coordinates of these pins can be used to determine where the part
    interacts with the surrounding schematic.'''
    
    def __init__(self, part_node, version_str):
        self._name = part_node.attrib['name']
        self._deviceset = part_node.attrib['deviceset']
        self._device = part_node.attrib['device']
        try:
            self._value = part_node.attrib['value']
        except:
            self._value = ''
        
        # TODO: libraries should be cached in a global or static variable using
        # the library name as a key
        self._library = Library(part_node.attrib['library'], version_str)
        # The symbol node contains the location of the part's pins
        symbol_node = self._library.GetSymbolNode(part_node.attrib['deviceset'])
        # Extract the pin locations
        self._pins = []
        for pin_node in symbol_node.findall('pin'):
            self._pins.append(Pin(pin_node))
    
    def GetName(self):
        '''Returns the name of the part.'''
        return self._name
    
    def GetValue(self):
        '''Returns the value given to the part, if any.'''
        return self._value
    
    def GetDevice(self):
        '''Returns the name of the device for this part.'''
        return self._device
    
    def GetDeviceSet(self):
        '''Returns the device set ID of the part.'''
        return self._deviceset
    
    def GetPins(self):
        '''Returns a list of pins belonging to the part. The coordinates of the
        pins are relative to the part's origin.'''
        return self._pins
