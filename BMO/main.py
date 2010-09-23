#
#  main.py
#  BMO
#
#  Created by makoto tsuyuki on 08/01/06.
#  Copyright everes.net 2008. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import BMOAppDelegate

# pass control to AppKit
AppHelper.runEventLoop()
