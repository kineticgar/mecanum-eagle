import os
from distutils.version import StrictVersion
from xml.etree import ElementTree
from urllib import urlopen

if os.name == 'nt':
    try:
        import winreg as winreg
    except:
        import _winreg as winreg

class Library:
    '''Docstring'''
    
    def __init__(self, library_name, version = None):
        self._library_name = library_name
        
        # Get a list of possible locations the library can be found at
        search_path = self._get_library_search_path(version)
        
        for path in search_path:
            # Append the name of the library and the .lbr extension
            path += library_name + '.lbr'
            try:
                print('Opening library file: ' + path)
                if path[0:4] != 'http':
                    eagle_node = ElementTree.parse(path).getroot() # <eagle>
                else:
                    try:
                        eagle_node = ElementTree.parse(urlopen(path)).getroot()
                    except:
                        continue
                # Store the <library> node so that we can access it later
                self._library_node = eagle_node.find('drawing').find('library')
                break # Success, return
            except IOError:
                # Library file doesn't exist, move on to the next one
                continue
        else:
            # Ran out of library files to try
            raise Exception('Could not open library file')
    
    def GetName(self):
        '''Returns the name of the library (omitting the .lbr extension).'''
        return self._library_name
    
    def GetSymbolNode(self, deviceset_name):
        '''Given a device set ID, this will return the node of the object's
        symbol.
        
        The symbol is the stuff that appears inside EAGLE when you place the
        object into your schematic. In EAGLE's "Add a part" window, the symbol
        is on the left and the object's footprint is on the right. Multiple
        devices are defined for each device set; while they have differing
        footprints, they all use the same device symbol (e.g. all US resistors
        have the same resistor symbol).
        
        An example symbol node looks like this (where ... represents the lines,
        text and shapes that EAGLE draws on the screen):
        <symbol name="R-US">
            ...
            <pin name="1" x="-5.08" y="0" visible="off" length="short" direction="pas" swaplevel="1"/>
        </symbol>
        '''
        
        symbol_name = self._get_symbol_name(deviceset_name)
        # Search <symbols> for the discovered symbol name
        for symbol_node in self._library_node.find('symbols'):
            if symbol_node.attrib['name'] == symbol_name: # <symbol name="...">
                return symbol_node
        raise Exception("Couldn't locate symbol: " + symbol_name)
    
    def _get_symbol_name(self, deviceset_name):
        '''Translates a device name into a symbol name.
        
        The translation happens by finding the corresponding device set and
        retrieving the symbol's name. A device set node looks like this:
        <deviceset name="R-US_" prefix="R" uservalue="yes">
            <gates>
                <gate name="G$1" symbol="R-US" x="0" y="0"/>
            </gates>
            ...
        </deviceset>'''
        
        for deviceset_node in self._library_node.find('devicesets'):
            if deviceset_node.attrib['name'] == deviceset_name: # <deviceset name="...">
                gate_node = deviceset_node.find('gates').find('gate')
                symbol_name = gate_node.attrib['symbol'] # target acquired
                return symbol_name
        raise Exception("Couldn't locate device set: " + deviceset_name)
    
    def _get_library_search_path(self, desired_version):
        '''This returns the path (a list of possible library file locations),
        taking into account the desired version number. All EAGLE versions
        are included; desired_version only affects the order of these
        directories.'''
        
        # Make sure desired version isn't a string
        if desired_version and not isinstance(desired_version, StrictVersion):
            desired_version = StrictVersion(desired_version)
        
        eagle_path = self._get_os_eagle_path()
        path = []
        
        # If desired_version isn't given, assume the most recent version available
        if not desired_version:
            desired_version = StrictVersion('1.0')
            for v in eagle_path:
                if desired_version < v:
                    desired_version = StrictVersion(v)
        
        # The general algorithm is: if the specified version isn't found, prefer
        # newer versions in ascending order; otherwise, prefer older versions in
        # descending order. If the desired version is 3.0:
        # [1.0, 2.0, 3.0, 4.0, 5.0] would become [3.0, 4.0, 5.0, 2.0, 1.0]
        # [2.0, 2.5, 3.5] would become [3.5, 2.5, 2.0]
        versions = sorted(eagle_path, key = lambda v: StrictVersion(v))
        i = 0
        for eagle_version in versions:
            if desired_version <= eagle_version:
                break
            i += 1
        for v in versions[i:] + (versions[i - 1::-1] if i >= 1 else []):
            path.append(eagle_path[v])
        
        # Append any remote library locations. These will be retrieved if the
        # library cannot be found on the local path.
        path.append('https://raw.github.com/sparkfun/SparkFun-Eagle-Libraries/master/')
        
        return path
    
    def _get_os_eagle_path(self):
        '''Returns the path (a list of directories) by locatiing EAGLE install
        directories in the OS.'''
        
        eagle_path = {}
        if os.name == 'nt':
            # First look in the registry for EAGLE installation directory
            # On x64, key is HKLM\SOFTWARE\Wow6432Node\CadSoft\EAGLE
            # On x86, I imagine this key would be HKLM\SOFTWARE\CadSoft\EAGLE
            try:
                eagle_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node\CadSoft\EAGLE')
            except WindowsError:
                try:
                    eagle_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\CadSoft\EAGLE')
                except WindowsError:
                    eagle_key = False;
            if eagle_key:
                try:
                    i = 0
                    while True:
                        version = winreg.EnumKey(eagle_key, i)
                        i += 1
                        try:
                            # Make sure the version is a valid version string
                            StrictVersion(version)
                        except:
                            continue
                        version_key = winreg.OpenKey(eagle_key, version)
                        # Blank string causes a trailing slash to be added
                        dir = os.path.join(winreg.QueryValueEx(version_key, 'Target')[0], 'lbr', '')
                        eagle_path[str(StrictVersion(version))] = dir
                        version_key.Close()
                except WindowsError:
                    # WindowsError: [Errno 259] No more data is available
                    pass
                eagle_key.Close()
        # If we don't have an Eagle path, assume the registry lookup failed
        if not len(eagle_path):
            if os.name == 'nt':
                try:
                    base_eagle_path = os.environ['ProgramFiles(x86)']
                except:
                    base_eagle_path = os.environ['ProgramFiles']
            else:
                base_eagle_path = '' # TODO: Get Linux directory
            for dir in os.listdir(base_eagle_path):
                if dir.startswith('EAGLE-'):
                    version = dir[len('EAGLE-'):]
                    try:
                        # Make sure the version is a valid version string
                        StrictVersion(version)
                    except:
                        continue
                    # Blank string causes a trailing slash to be added
                    eagle_path[str(StrictVersion(version))] = os.path.join(program_files, dir, 'lbr', '')
        #elif os.name == 'posix':
        #    pass
        
        return eagle_path
