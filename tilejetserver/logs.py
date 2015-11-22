import os
import glob
import sys
import httplib2
import base64
import math
import copy
import string
import datetime
import iso8601
import time

import email.utils as eut

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.cache import cache, caches, get_cache
from django.http import Http404

from geojson import Polygon, Feature, FeatureCollection, GeometryCollection

from geowatch.producer import connect_and_send

from tilejetstats.mongodb import buildStats, incStats
from tilejetlogs.tilelogs import buildTileRequestDocument
from tilejetserver.cache.tasks import taskIncStats

http_client = httplib2.Http()


def logTileRequest(tileorigin, tilesource, x, y, z, status, datetime, ip):
    log_root = settings.LOG_REQUEST_ROOT
    log_format = settings.LOG_REQUEST_FORMAT
    if log_root and log_format:
        log_file = log_root+os.sep+"requests_tiles_"+datetime.strftime('%Y-%m-%d')+".tsv"

        with open(log_file,'a') as f:
            line = log_format.format(status=status,tileorigin=tileorigin,tilesource=tilesource,z=z,x=x,y=y,ip=ip,datetime=datetime.isoformat())
            f.write(line+"\n")

            connect_and_send(
                settings.TILEJET_GEOWATCH_HOST,
                settings.TILEJET_GEOWATCH_TOPIC_LOGS,
                line)


def logTileRequest_old(tileorigin, tilesource, x, y, z, status, datetime, ip):
    #starttime = time.clock()
    #==#
    log_root = settings.LOG_REQUEST_ROOT
    #log_format = settings.LOG_REQUEST_FORMAT['tile_request']
    log_format = settings.LOG_REQUEST_FORMAT

    if log_root and log_format:
        #if not os.path.exists(log_root):
        #    os.makedirs(log_root)

        log_file = log_root+os.sep+"requests_tiles_"+datetime.strftime('%Y-%m-%d')+".tsv"

        with open(log_file,'a') as f:
            line = log_format.format(status=status,tileorigin=tileorigin,tilesource=tilesource,z=z,x=x,y=y,ip=ip,datetime=datetime.isoformat())
            f.write(line+"\n")

            # Import Gevent and monkey patch
            from gevent import monkey
            monkey.patch_all()
            # Update MongoDB
            from pymongo import MongoClient
            client = None
            db = None
            r = None
            try:
                client = MongoClient('/tmp/mongodb-27017.sock')
                db = client[settings.TILEJET_DBNAME]
                r = buildTileRequestDocument(
                    tileorigin=tileorigin,
                    tilesource=tilesource,
                    x=x,
                    y=y,
                    z=z,
                    extension=extension,
                    status=status,
                    datetime=datetime,
                    ip=ip)
            except:
                client = None
                db = None
                errorline = "Error: Could not connet to log database. Most likely issue with connection pool"
                error_file = settings.LOG_ERRORS_ROOT+os.sep+"requests_tiles_"+datetime.strftime('%Y-%m-%d')+"_errors.txt"
                with open(error_file,'a') as f:
                    f.write(errorline+"\n")

            # Update Mongo Logs
            if client and db and r:
                try:
                    db[settings.TILEJET_COLLECTION_LOGS].insert(r, w=0)
                except:
                    errorline = "Error: Could not write log entry into database.  Most likely socket issue.  For the following: "+line
                    error_file = settings.LOG_ERRORS_ROOT+os.sep+"requests_tiles_"+datetime.strftime('%Y-%m-%d')+"_errors.txt"
                    with open(error_file,'a') as f:
                        f.write(errorline+"\n")

                # Update Mongo Aggregate Stats
                stats = buildStats(settings.TILEJET_LIST_STATS, r)
                # Sync stats
                if settings.ASYNC_STATS:
                    try:
                        taskIncStats.apply_async(
                            args=[stats],
                            kwargs=None,
                            queue="statistics")
                    except:
                        errorline = "Error: Could not queue taskIncStats.  Most likely issue with rabbitmq."
                        error_file = settings.LOG_ERRORS_ROOT+os.sep+"requests_tiles_"+datetime.strftime('%Y-%m-%d')+"_errors.txt"
                        with open(error_file,'a') as f:
                            f.write(errorline+"\n")
                else:
                    incStats(db, stats)


    #print "Time Elapsed: "+str(time.clock()-starttime)


def logTileRequestError(line, datetime):
    log_root = settings.LOG_ERRORS_ROOT
    if log_root:
        #if not os.path.exists(log_root):
        #    os.makedirs(log_root)
        error_file = log_root+os.sep+"requests_tiles_"+datetime.strftime('%Y-%m-%d')+"_errors.txt"
        with open(error_file,'a') as f:
            f.write(line+"\n")
