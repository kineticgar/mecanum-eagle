# Copyright header
'''Module docstring.'''

import os, sys
from xml.etree import ElementTree
from kineticthings.eagle.part import Part

def main():
    eagle_node = ElementTree.parse('Layout.sch').getroot() # <eagle>
    version = eagle_node.attrib['version']
    schematic_node = eagle_node.find('drawing').find('schematic')
    
    parts = []
    for part_node in schematic_node.find('parts'):
        parts.append(Part(part_node, version))
    
    for part in parts:
        if part.GetDeviceSet() == 'ARDUINO-MEGA' and part.GetDevice() == 'FULL':
            arduino = part;
            print(arduino.GetName())
            break

            
if __name__ == '__main__':
    main()

# SCH file looks like:
# 
# eagle: {
#   version: "6.2",
#   drawing: {
#     layers: {
#       layer: {number: "91", name: "Nets",    color: "2", fill: "1", visible: "yes", active: "yes"},
#       layer: {number: "92", name: "Busses",  color: "1", fill: "1", visible: "yes", active: "yes"},
#       layer: {number: "93", name: "Pins",    color: "2", fill: "1", visible: "no",  active: "yes"},
#       layer: {number: "94", name: "Symbols", color: "4", fill: "1", visible: "yes", active: "yes"},
#       layer: {number: "95", name: "Names",   color: "7", fill: "1", visible: "yes", active: "yes"},
#       layer: {number: "96", name: "Values",  color: "7", fill: "1", visible: "yes", active: "yes"},
#       layer: {number: "97", name: "Info",    color: "7", fill: "1", visible: "yes", active: "yes"},
#       layer: {number: "98", name: "Guide",   color: "6", fill: "1", visible: "yes", active: "yes"},
#     },
#     schematic: {
#       libraries: {},
#       attributes: {},
#       varaintdefs: {},
#       classes: {},
#       parts: {},
#       sheets: {
#         sheet: {
#           plain: {},
#           instances: {},
#           busses: {},
#           nets: {}
#         }
#       }
#     }
#   }
# }

# Adding a straight wire:
# 
# nets: {
#   net: {
#     name: "N$1",
#     class: "0",
#     segment: {
#       wire: {x1: "0", y1: "0", x2: "27.94", y2: "0", width: "0.1524", layer: "91"}
#     }
#   }
# }

# Adding a bent wire:
# 
# segment: {
#   wire: {x1: "0",     y1: "0", x2: "30.48", y2: "0",     width: "0.1524", layer: "91"},
#   wire: {x1: "30.48", y1: "0", x2: "30.48", y2: "22.86", width: "0.1524", layer: "91"}
# }

# Rectangles travel in a closed loop.
# 
# segment: {
#   wire: {x1: "0",     y1: "0",     x2: "30.48", y2: "0",     width: "0.1524", layer: "91"},
#   wire: {x1: "30.48", y1: "0",     x2: "30.48", y2: "22.86", width: "0.1524", layer: "91"},
#   wire: {x1: "30.48", y1: "22.86", x2: "0",     y2: "22.86", width: "0.1524", layer: "91"},
#   wire: {x1: "0",     y1: "22.86", x2: "0",     y2: "0",     width: "0.1524", layer: "91"}
# }

# A T-intersection happens when a coordinate occurs thrice (starting or ending)
# 
# segment: {
#   wire: {x1: "0",     y1: "0", x2: "15.24", y2: "0",     width: "0.1524", layer: "91"},
#   wire: {x1: "15.24", y1: "0", x2: "30.48", y2: "0",     width: "0.1524", layer: "91"},
#   wire: {x1: "15.24", y1: "0", x2: "15.24", y2: "22.86", width: "0.1524", layer: "91"}
# }

# A net junction is created by specifying its coordinates
# 
# segment: {
#   wire: {x1: "0",     y1: "0", x2: "15.24", y2: "0",     width: "0.1524", layer: "91"},
#   wire: {x1: "15.24", y1: "0", x2: "30.48", y2: "0",     width: "0.1524", layer: "91"},
#   wire: {x1: "15.24", y1: "0", x2: "15.24", y2: "22.86", width: "0.1524", layer: "91"},
#   junction: {x1: "15.24", y1: "0"}
# }

# A new net is created when a line is placed not touching another line
# 
# nets: {
#   net: {
#     name: "N$1",
#     class: "0",
#     segment: {
#       wire: {x1: "0", y1: "0", x2: "30.48", y2: "0", width: "0.1524", layer: "91"}
#     }
#   },
#   net: {
#     name: "N$2",
#     class: "0",
#     segment: {
#       wire: {x1: "0", y1: "12.7", x2: "30.48", y2: "12.7", width: "0.1524", layer: "91"}
#     }
#   }
# }

# Placing a solo resistor:
# 
# schematic: {
#   ...
#   parts: {
#     part: {name: "R1", library: "rcl", deviceset: "R-US_", device: "0204/2V"}
#   },
#   sheets: {
#     sheet: {
#       plain: {},
#       instances: {
#         instance: {part: "R1", gate: "G$1", x: "17.78", y: "15.24"}
#       },
#       busses: {},
#       nets: {}
#     }
#   }
# }

# Adding wires to both pins of the resistor:
# 
# sheet: {
#   plain: {},
#   instances: {
#     instance: {part: "R1", gate: "G$1", x: "17.78", y: "15.24"}
#   },
#   busses: {},
#   nets: {
#     net: {
#       name: "N$1",
#       class: "0",
#       segment: {
#         wire: {x1: "0", y1: "0", x2: "12.7", y2: "0", width: "0.1524", layer: "91"},
#         pinref: {part: "R1", gate: "G$1", pin: "1"}
#       }
#     },
#     net: {
#       name: "N$2",
#       class: "0",
#       segment: {
#         pinref: {part: "R1", gate: "G$1", pin: "2"},
#         wire: {x1: "22.86", y1: "0", x2: "30.48", y2: "0", width: "0.1524", layer: "91"}
#       }
#     }
#   }
# }

# Two resistors in series, no connecting line:
# 
# parts: {
#   part: {name: "R1", library: "rcl", deviceset: "R-US_", device: "0204/2V"}
#   part: {name: "R2", library: "rcl", deviceset: "R-US_", device: "0204/2V"}
# },
# 
# sheet: {
#   plain: {},
#   instances: {
#     instance: {part: "R1", gate: "G$1", x: "5.08",  y: "0"},
#     instance: {part: "R2", gate: "G$1", x: "15.24", y: "0"}
#   },
#   busses: {},
#   nets: {
#     net: {
#       name: "N$1",
#       class: "0",
#       segment: {
#         pinref: {part: "R1", gate: "G$1", pin: "2"},
#         pinref: {part: "R2", gate: "G$1", pin: "1"}
#       }
#     }
#   }
# }
