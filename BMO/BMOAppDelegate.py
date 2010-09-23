#
#  BMOAppDelegate.py
#  BMO
#
#  Created by makoto tsuyuki on 08/01/06.
#  Copyright everes.net 2008. All rights reserved.
#

from Foundation import *
from AppKit import *


import objc

from pyamazon import getBook, getMusic, getVideo, getGame, PylibNotFoundError
import time

import os

USER_HOME = os.path.expanduser('~')
BMO_DIR = os.path.join(USER_HOME, 'BMO')
IMG_DIR = os.path.join(BMO_DIR, '.img')
AP_PREF_DIR = os.path.join(os.path.join(USER_HOME, 'Library'), 'Preferences')
SETUP_FILE = os.path.join(AP_PREF_DIR, 'net.everes.BMO.plist')
IMG_WIDTH = 300

AWS_KEY = 'YOUR KEY HERE'

class BMOAppDelegate(NSObject):

    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
        if not os.path.exists(BMO_DIR):
            os.mkdir(BMO_DIR)
            os.mkdir(IMG_DIR)
        self.mainpanel.setIsVisible_(True)

    #main panel
    mainpanel = objc.IBOutlet()
    isbnfield = objc.IBOutlet()
    imagefield = objc.IBOutlet()
    outputfield = objc.IBOutlet()
    

    @objc.IBAction
    def scanBarcode_(self, sender):
        scanner = MyBarcodeScanner.sharedInstance()
        scanner.setStaysOpen_(False)
        scanner.setDelegate_(self)
        scanner.setMirrored_(False)
        scanner.scanForBarcodeWindow_(None)
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)

    @objc.IBAction
    def execAmazon_(self, sender):
        b = self.isbnfield.stringValue()
        if len(b) == 0: return
        media = None
        if len(b) == 12 and b.rfind('78') == 0:
            b = '9%s' % b
        if len(b) == 13 and b.rfind('978') == 0:
            media = getBook(AWS_KEY, b)
        else:
            try:
                media = getVideo(AWS_KEY, b)
            except PylibNotFoundError:
                try:
                    media = getMusic(AWS_KEY, b)
                except PylibNotFoundError:
                    try:
                        media = getGame(AWS_KEY, b)
                    except PylibNotFoundError: pass
        if media is not None:
            self.outputfield.setStringValue_(unicode(media.title))
            if media.image is not None:
                img = NSImage.alloc().initWithContentsOfURL_(
                                NSURL.URLWithString_(media.image) )
                if not img:
                    r_img = NSImage.alloc().initWithContentsOfFile_(NSBundle.mainBundle().pathForResource_ofType_("noimage", "tiff"))
                else:
                    size = img.size()
                    width, height = size.width, size.height
                    scale = float(IMG_WIDTH)/width
                    new_width, new_height = int(width * scale), int(height * scale)
                    target_size = NSSize(new_width, new_height)
                    r_img = NSImage.alloc().initWithSize_(target_size)
                    try :
                        r_img.lockFocus()
                        NSGraphicsContext.currentContext().setImageInterpolation_(NSImageInterpolationHigh)
                        img.drawInRect_fromRect_operation_fraction_(((0,0), target_size), ((0,0), size), NSCompositeSourceOver, 1.0)
                    finally:
                        r_img.unlockFocus()
                self.imagefield.setImage_(r_img)
                try:
                    data = NSBitmapImageRep.imageRepWithData_(r_img.TIFFRepresentation())
                    data.representationUsingType_properties_(NSPNGFileType,None).writeToFile_atomically_(os.path.join(IMG_DIR, media.asin + ".png"),objc.YES)
                except AttributeError: pass
                data_file = os.path.join(BMO_DIR, '%s.ebmo' % media.asin)
                write_mode = 'w'
                f = open(data_file, 'w')
                dd = media.toXml().encode('utf-8')
                f.write(dd)
                f.close()
        else:
            self.outputfield.setStringValue_('No Items found')
        time.sleep(0.5)
        self.scanBarcode_(None)
        

    def gotBarcode_(self, barcode):
        b = str(barcode)
        self.isbnfield.setStringValue_(b)
        self.execAmazon_(None)
