# -*- coding: utf8 -*-
#
#  pyamazon.py
#  pyshelf
#
#  Created by makoto tsuyuki on 07/11/04.
#  Copyright (c) 2007 everes.net All rights reserved.
#
from datetime import datetime
import httplib, urllib
from xml.etree import ElementTree


class Item(object):
    def __init__(self, asin='', sales_rank=0, image='',
                   isbn='', price=0, formattedPrice='',
                   publisher='', title=''):
        self.asin = asin
        self.sales_rank = sales_rank
        self.image = image
        self.isbn=isbn
        self.price=price
        self.formattedPrice = formattedPrice
        self.publisher=publisher
        self.title = title
        self.recommends = []
        self.authors = []
    def toXml(self):
        tmp = u'''<?xml version="1.0" encoding="utf-8"?>
<ebmo>
<title>%(title)s</title>
<asin>%(asin)s</asin>
<price>%(price)s</price>
<author>%(authors)s</author>
<rank>%(rank)s</rank>
<recommends>%(recs)s</recommends>
<created>%(create_date)s</created>
</ebmo>'''
        d = datetime.now()
        create_date = '%4d-%02d-%02d %02d:%02d:%02d' % (d.year, d.month, d.day, d.hour, d.minute, d.second)
        return tmp % dict(title=self.title, asin=self.asin, price=self.formattedPrice,
                                    authors=u','.join([u'%s' % a for a in self.authors]),
                                    rank=self.sales_rank,
                                    recs=u'\n'.join( [u'<recommend><rasin>%s</rasin><rtitle>%s</rtitle></recommend>' % (r.asin, r.title) for r in self.recommends]),
                                    create_date=create_date)
    def __unicode__(self):
        tmp = '''
Title: %(title)s
Asin: %(asin)s
Price: %(price)s
Author: %(authors)s
Rank: %(rank)s
Recommends:
%(recs)s'''
        return tmp % dict(title=self.title, asin=self.asin, price=self.formattedPrice,
                                    authors=u','.join([a for a in self.authors]),
                                    rank=self.sales_rank,
                                    recs=u'\n'.join( [u'%s(%s)' % (r.title, r.asin,) for r in self.recommends]))


class PylibAPIError(Exception):
    def __init__(self, message):
        self.message = message
    def __unicode__(self):
        return self.message

class PylibNotFoundError(Exception):
    def __init__(self, message):
        self.message = message
    def __unicode__(self):
        return self.message

class Recommend(object):
    def __init__(self, asin, title):
        self.asin = asin
        self.title = title
    def __unicode__(self):
        return'%s(%s)' % (self.title, self.asin, )
xml = ''

def parseXML(xml):
    def getImageURL(item):
        node = item.find('LargeImage')
        if node is not None:
            return node.find('URL').text
        return ''
    def isValid(items):
        valid = items.find('Request').find('IsValid').text
        if valid == 'True': return True
        return False
    
    root = ElementTree.fromstring(xml)
    #print xml
    items = root.find('Items')
    if not items:
        raise PylibAPIError('No Items')
    if not isValid(items):
        errors = items.find('Request').find('Errors')
        error_message = ''
        errorlist = errors.findall('Error')
        for e in errorlist:
            error_message += '%s: %s\n' % (e.find('Code').text, e.find('Message').text)
        raise PylibAPIError(error_message)
    
    item = items.find('Item')
    if not item:
        raise PylibNotFoundError('Your request item is not found at Amazon.co.jp')
    asin = item.find('ASIN') is not None and item.find('ASIN').text or ''
    sales_rank = item.find('SalesRank') is not None and item.find('SalesRank').text or ''
    image = getImageURL(item)
    attributes = item.find('ItemAttributes')
    author = attributes.findall('Author')
    isbn = attributes.find('ISBN') is not None and attributes.find('ISBN').text or ''
    lp = attributes.find('ListPrice')
    price = lp is not None and lp.find('Amount') and lp.find('Amount').text or ''
    formattedPrice = lp is not None and lp.find('FormattedPrice') is not None and lp.find('FormattedPrice').text or ''
    publisher = attributes.find('Publisher') is not None and attributes.find('Publisher').text or ''
    title = attributes.find('Title').text
    recommends = []
    authors = []
    obj = Item(asin=asin, sales_rank=sales_rank,
                     image=image, isbn=isbn, price=price,
                     formattedPrice=formattedPrice, publisher=publisher,
                     title = title)
    for a in author:
        authors.append(a.text)
    if item.find('SimilarProducts') is not None:
        for p in item.find('SimilarProducts'):
            r = Recommend(p.find('ASIN').text, p.find('Title').text)
            recommends.append(r)
    obj.authors = authors
    obj.recommends = recommends
    return obj

def getBook(api_key, barcode):
    return getMedia(api_key, barcode, searchIndex='Books', type='ISBN')

def getMusic(api_key, barcode):
    return getMedia(api_key, barcode, searchIndex='Music', type='UPC')

def getVideo(api_key, barcode):
    return getMedia(api_key, barcode, searchIndex='Video', type='UPC')

def getGame(api_key, barcode):
    return getMedia(api_key, barcode, searchIndex='VideoGames', type='UPC')


VERSION = '0.1'
API_SERVER = 'ecs.amazonaws.jp:80'

def getMedia(api_key, barcode, searchIndex='Book', type='ISBN'):
    param = {'Service': 'AWSECommerceService',
                   'AWSAccessKeyId': api_key,
                   'Operation': 'ItemLookup',
                   'SearchIndex': searchIndex,
                   'ItemId': barcode,
                   'IdType': type,
                   'ResponseGroup': 'Medium,Reviews,SalesRank,Similarities',
                   'Version': '2007-10-29'}
    headers = {"Content-type": "application/x-www-form-urlencoded",
                      "Accept"      : "text/plain",
                      "User-agent"  : "pylibrary/%s" % (VERSION)}
    params = urllib.urlencode(param)
    conn = httplib.HTTPConnection(API_SERVER)
    conn.request("POST", "/onca/xml", params, headers)
    response = conn.getresponse()
    xml = response.read()
    xml = xml.replace('xmlns="http://webservices.amazon.com/AWSECommerceService/2007-10-29"', '')
    conn.close()
    return parseXML(xml)



#try:
#    b = getGame(API_KEY, '4976219754576')
#except Exception, e:
#    print unicode(e)

