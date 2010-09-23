#include <CoreFoundation/CoreFoundation.h>
#include <CoreServices/CoreServices.h>
#include <QuickLook/QuickLook.h>
#include <Cocoa/Cocoa.h>

OSStatus GeneratePreviewForURL(void *thisInterface, QLPreviewRequestRef preview, CFURLRef url, CFStringRef contentTypeUTI, CFDictionaryRef options)
{
    NSAutoreleasePool *pool;
    NSData *image;
    NSMutableString *html, *png;
    NSMutableDictionary *dict, *props, *imgProps, *reco;
    NSXMLDocument *xmlDoc;
    NSError *err=nil;

    NSXMLNode *aNode;
    NSString *k, *v, *key;
    
    pool = [[NSAutoreleasePool alloc] init];

    xmlDoc = [[[NSXMLDocument alloc] initWithContentsOfURL:url
            options:(NSXMLNodePreserveWhitespace|NSXMLNodePreserveCDATA)
            error:&err] autorelease];
    if (xmlDoc == nil) {
        xmlDoc = [[[NSXMLDocument alloc] initWithContentsOfURL:url
                    options:NSXMLDocumentTidyXML
                    error:&err] autorelease];
    }
    aNode = [xmlDoc rootElement];
    if (QLPreviewRequestIsCancelled(preview))
        return noErr;

    dict = [[[NSMutableDictionary alloc] init] autorelease];
    reco = [[[NSMutableDictionary alloc] init] autorelease];
    
    //NSLog(@"KKKKKK");
    while (aNode = [aNode nextNode]) {
        k = [aNode name];
        if (k != nil) {
            //aNode = [aNode nextNode];
    //NSLog(k);
            if([@"recommend" isEqualToString:k]) {
              aNode = [aNode nextNode];
    //NSLog(@"aNode---------------------");
    //NSLog([aNode stringValue]);
              NSString *asin = [aNode stringValue];
              aNode = [aNode nextNode];
              aNode = [aNode nextNode];
              NSString *title = [aNode stringValue];
              [reco setValue:title forKey:asin];
              //NSLog(@"----");
              //NSLog(title);
              //NSLog(asin);
            } else {
              v = [aNode stringValue];
              [dict setValue: v forKey:k];
            }
        }
    }
    //[aNode release]; [k release]; [v release];
    
    html = [[[NSMutableString alloc] init] autorelease];
    [html appendString:@"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"];
    [html appendString:@"<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">\n"];
    [html appendString:@"<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"ja\">\n"];
    [html appendString:@"  <head>\n"];
    [html appendString:@"    <title></title>\n"];
    [html appendString:@"    <style type=\"text/css\">\n"];
    [html appendString:@"    <!--\n"];
    [html appendString:@"    * { padding: 0px; margin: 0px; }\n"];
    [html appendString:@"    .cover { float: left;  width: 320px; padding-left: 20px; }\n"];
    [html appendString:@"    .meta { float: left;  width: 410px; padding-left: 30px; padding-top: 50px; }\n"];
    [html appendString:@"    .recommends {  padding-top: 80px; }\n"];
    [html appendString:@"    body{color: #EEF; background-color: #000;}\n"];
    [html appendString:@"    a:link, a:visited { color:#3366AA;}\n"];
    [html appendString:@"    a:active { color:#FF3399; }\n"];
    [html appendString:@"    a:hover { color:#FF3399; text-decoration: underline;}\n"];
    [html appendString:@"    h1  {font-size: medium; margin-bottom: 1em; }\n"];
    [html appendString:@"    h2  {font-size: small;}\n"];
    [html appendString:@"    h3,h4  {font-size: small; margin-left: 1em;}\n"];
    [html appendString:@"    h5  {font-size: small; margin-top: .8em; margin-left: 1em; }\n"];
    [html appendString:@"    -->\n"];
    [html appendString:@"    </style>\n"];
    [html appendString:@"  </head>\n"];
    [html appendString:@"<body>\n"];
    [html appendString:@"<div class=\"cover\">\n"];
    [html appendString:@"  <img src=\"cid:ebmo.png\"/>"];
    [html appendString:@"</div>"];
    [html appendString:@"<div class=\"meta\">\n"];
    [html appendString:@"  <h1>"];
    if([dict objectForKey:@"title"])
        [html appendString:[dict objectForKey:@"title"]];
    [html appendString:@"</h1>\n"];
    [html appendString:@"  <h2>"];
    if([dict objectForKey:@"author"])
        [html appendString:[dict objectForKey:@"author"]];
    [html appendString:@"</h2>\n"];
    [html appendString:@"  <h3>価格: "];
    if([dict objectForKey:@"price"])
        [html appendString:[dict objectForKey:@"price"]];
    [html appendString:@"</h3>\n"];
    [html appendString:@"  <h3>ランク: "];
    if([dict objectForKey:@"rank"])
        [html appendString:[dict objectForKey:@"rank"]];
    [html appendString:@"</h3>\n"];
    [html appendString:@"<div class=\"recommends\">\n"];
    [html appendString:@"<h2>おすすめ</h2>\n"];
    NSLog(@"s---------------------");
    for (key in reco) {
        [html appendString:[NSString stringWithFormat:@"<h5><a href=\"http://www.amazon.co.jp/exec/obidos/ASIN/%@/everes-22/ref=nosim\">%@</h5>\n", key, [reco objectForKey:key]]];
        //NSLog(key);
    }
    NSLog(@"e---------------------");
    [html appendString:@"</div>\n"];
    [html appendString:@"</div>\n"];
    [html appendString:@"</body></html>\n"];
    
    //[key release];
    //[xmlDoc release];
    
    props=[[[NSMutableDictionary alloc] init] autorelease];
    [props setObject:@"UTF-8" forKey:(NSString *)kQLPreviewPropertyTextEncodingNameKey];
    [props setObject:@"text/html" forKey:(NSString *)kQLPreviewPropertyMIMETypeKey];

    png = [[[NSMutableString alloc] init] autorelease];
    [png appendString:@"/.img/"];
    [png appendString:[dict objectForKey:@"asin"]];
    [png appendString:@".png"];
    
    //[reco release];
    //[dict release];
    
    image=[[NSData dataWithContentsOfFile:[NSString stringWithFormat:@"%@%@",
          [[NSString stringWithFormat:@"%@",
          [url path]] stringByDeletingLastPathComponent],
          png]] autorelease];
    imgProps=[[[NSMutableDictionary alloc] init] autorelease];
    [imgProps setObject:@"image/png" forKey:(NSString *)kQLPreviewPropertyMIMETypeKey];
    [imgProps setObject:image forKey:(NSString *)kQLPreviewPropertyAttachmentDataKey];
    [props setObject:[NSDictionary dictionaryWithObject:imgProps forKey:@"ebmo.png"] forKey:(NSString *)kQLPreviewPropertyAttachmentsKey];

 
    QLPreviewRequestSetDataRepresentation(preview,(CFDataRef)[html dataUsingEncoding:NSUTF8StringEncoding],kUTTypeHTML,(CFDictionaryRef)props);

    [pool release];
    //[props release];
    //[png release];
    //[html release];
    //[image release];
    //[imgProps release];

    return noErr;
}
void CancelPreviewGeneration(void* thisInterface, QLPreviewRequestRef preview)
{
    // implement only if supported
}
