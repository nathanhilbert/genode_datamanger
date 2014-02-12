import base64
import json
import csv
import StringIO

from datetime import datetime
from functools import wraps
import urllib
from django.contrib.auth import authenticate
from django.http import HttpResponse
import httplib2
import os.path
import os

from django.conf import settings
from django.template.base import Template
from django.template.context import Context
from geonode import datamanager


def testFormhubConnection(url, username, password):
    auth = base64.encodestring(username+ ':' + password)
    headers = {'Authorization' : 'Basic ' + auth}
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    http.add_credentials(username, password)
    print "making request"
    resp, content = http.request(url, headers=headers)
    print resp.status
    if resp.status == 200:
        return True, "success"
    elif resp.status == 404:
        return False, "Cannot find URL"
    elif resp.status == 403:
        return False, "User name or password incorrect"
    else:
        return False, "Unknown error"


def getFormhubColumns(dataconnection):
    url = dataconnection.formhub_url.strip('/') + "/data.csv"
    auth = base64.encodestring(dataconnection.formhub_username + ':' +  dataconnection.formhub_password)
    headers = {'Authorization' : 'Basic ' + auth}
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    http.add_credentials(dataconnection.formhub_username, dataconnection.formhub_password)
    resp, content = http.request(url, headers=headers)
    try:
        headers = [""] + content.split("\n")[0].split(",")
    except:
        return {}
    return zip(headers, headers)

def getFormhubCSV(dataconnection):
    url = dataconnection.formhub_url.strip('/') + "/data.csv"
    auth = base64.encodestring(dataconnection.formhub_username + ':' +  dataconnection.formhub_password)
    headers = {'Authorization' : 'Basic ' + auth}
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    http.add_credentials(dataconnection.formhub_username, dataconnection.formhub_password)
    resp, content = http.request(url, headers=headers)

    f = StringIO.StringIO(content)
    reader = csv.reader(f, delimiter=',')
    headers = reader.next()
    data = []
    for row in reader:
        data.append(row)
    return headers, data


from geopy import geocoders


def geocodeSet(opentext, addition):
    if addition:
        geocodestring = opentext + addition
    else:
        geocodestring = opentext
    g = geocoders.GoogleV3()
    try:
        place, (lat, lon) = g.geocode(geocodestring)
    except:
        return False
    if lat and lon:
        return {'lat':lat, 'lon':lon}  
    else:
        return False
    #do the geocode



from shapely.geometry import Point, mapping
from fiona import collection

import random
import tempfile
import shutil
from django.template.defaultfilters import slugify
from geonode.layers.utils import file_upload

def fixShpNames(namesarray):
    newheaders = []
    finalheaders = []
    prefix = {}
    for headername in namesarray:
        try:
            writesection = headername.split("/")[-1]
        except:
            writesection = headername
        newname = (writesection[:10]) if len(writesection) > 10 else writesection
        if newname in prefix.keys():
            prefix[newname] +=1
        else :
            prefix[newname] = 1
        newheaders.append(newname)
    for newname in newheaders:
        if prefix[newname] == 1:
            finalheaders.append(newname)
        else:
            if len(newname) < 8:
                newname = newname + str(prefix[newname]).zfill(1)
            else:
                newname = newname[:8]+ str(prefix[newname]).zfill(1)
            finalheaders.append(newname)
    return finalheaders


def createLayerFromCSV(dataconnection):
    rawheaders, data = getFormhubCSV(dataconnection)
    headers = fixShpNames(rawheaders)
    print headers
    props = {}
    for headstr in headers:
        props[headstr] = 'str'
    schema = { 'geometry': 'Point', 'properties': props}

    temporaryfile = tempfile.gettempdir() + "/" + slugify(dataconnection.title)

    with collection(temporaryfile + ".shp", "w", "ESRI Shapefile", schema) as output:
        for row in data:
            dataset = dict(zip(rawheaders, row))
            atrributes = dict(zip(headers, row))
            try:
                point = Point(float(dataset[dataconnection.lon_column]), float(dataset[dataconnection.lat_column]))
            except Exception,e: 
                print str(e)
                point = None
            if not point and dataconnection.geocode_column:
                print "trying to geocode"
                pointset = geocodeSet(dataconnection.geocode_column, dataconnection.geocode_country)
                if not pointset:
                    continue
                else:
                    point = Point(float(pointset['lon']), float(pointset['lat']))

                #attempt to geocode
            if not point:
                continue
            output.write({
                'properties': atrributes,
                'geometry': mapping(point)
            })
    #add proj file to the mix
    fromprojname = os.path.dirname(datamanager.__file__) + "/fixtures/wgs84.prj"
    shutil.copy(fromprojname, temporaryfile + ".prj")

    #upload file and done
    newlayer = file_upload(temporaryfile + ".shp", user=dataconnection.owner, overwrite=True)

    try:
        os.remove(temporaryfile + ".shp")
        os.remove(temporaryfile + ".cpg")
        os.remove(temporaryfile + ".dbf")
        os.remove(temporaryfile + ".shx")
        os.remove(temporaryfile + ".prj")
    except:
        print "error removing file"
    return newlayer

