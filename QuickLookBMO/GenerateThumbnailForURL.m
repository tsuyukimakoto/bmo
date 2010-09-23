#include <CoreFoundation/CoreFoundation.h>
#include <CoreServices/CoreServices.h>
#include <QuickLook/QuickLook.h>
#include <Cocoa/Cocoa.h>

OSStatus GenerateThumbnailForURL(void *thisInterface, QLThumbnailRequestRef thumbnail, CFURLRef url, CFStringRef contentTypeUTI, CFDictionaryRef options, CGSize maxSize)
{
    NSAutoreleasePool *pool;
    NSMutableDictionary *dict;
    NSXMLDocument *xmlDoc;
    NSXMLNode *aNode = nil;
    NSError *err=nil;
    
    CGDataProviderRef source;
    CGImageRef img; 

    NSMutableString *png = nil;    
    NSString *k;
    NSString *v;

    pool = [[NSAutoreleasePool alloc] init];

    dict = [[[NSMutableDictionary alloc] init] autorelease];
    xmlDoc = [[[NSXMLDocument alloc] initWithContentsOfURL:url
            options:(NSXMLNodePreserveWhitespace|NSXMLNodePreserveCDATA)
            error:&err] autorelease];
    if (xmlDoc == nil) {
        xmlDoc = [[[NSXMLDocument alloc] initWithContentsOfURL:url
                    options:NSXMLDocumentTidyXML
                    error:&err] autorelease];
    }
    aNode = [xmlDoc rootElement];
    while (aNode = [aNode nextNode]) {
        k = [aNode name];
        if (k != nil) {
            NSLog([aNode name]);
            NSLog(@"=>");
            aNode = [aNode nextNode];
            NSLog([aNode stringValue]);
            v = [aNode stringValue];
            [dict setValue: v forKey:k];
        }
    }

    
    png = [[[NSMutableString alloc] init] autorelease];
    [png appendString:@"/.img/"];
    [png appendString:[dict objectForKey:@"asin"]];
    [png appendString:@".png"];
    
    
    source = CGDataProviderCreateWithURL(
                                [NSURL URLWithString:[NSString stringWithFormat:@"file://localhost%@%@",
                                [[NSString stringWithFormat:@"%@",[url path]] stringByDeletingLastPathComponent],
                                png]]
                                );
    if(source == nil) return noErr;
    
    img = CGImageCreateWithPNGDataProvider ( source, NULL, NO, kCGRenderingIntentDefault ); 
    QLThumbnailRequestSetImage(thumbnail, img, NULL);

    [pool release];
    CFRelease(source);
    CFRelease(img);

    return noErr;
}

void CancelThumbnailGeneration(void* thisInterface, QLThumbnailRequestRef thumbnail)
{
    // implement only if supported
}




