from __future__ import absolute_import

import os, datetime, time

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404, render

from celery import shared_task

from tilejetutil.tilemath import tms_to_bbox, flip_y

from tilejetserver.utils import bbox_intersects_source, TYPE_TMS, TYPE_TMS_FLIPPED, TYPE_BING, TYPE_WMS, commit_to_file, getValue
from tilejetserver.source.models import TileSource
from tilejetserver.source.utils import getTileSources, requestTileFromSource

from tilejetstats.mongodb import getStat, getStats
from tilejetcache.cache import getTileFromCache, commit_to_cache

from tilejetlogs.base import LOG_FIELD_FORMATS


def update_stats():
    GEVENT_MONKEY_PATCH = False
    # GEVENT_MONKEY_PATCH = settings.TILEJET_GEVENT_MONKEY_PATCH
    #=======#
    now = datetime.datetime.now()
    stats = {}
    if GEVENT_MONKEY_PATCH:
        # Import Gevent and monkey patch
        from gevent import monkey
        monkey.patch_all()
    # Update MongoDB
    from pymongo import MongoClient
    client = None
    db = None
    try:
        client = MongoClient(settings.TILEJET_DBHOST, settings.TILEJET_DBPORT)
        db = client[settings.TILEJET_DBNAME]
    except:
        client = None
        db = None
        errorline = "Error: Could not connet to stats database from scheduled taskUpdateStats. Most likely issue with connection pool"
        error_file = settings.LOG_ERRORS_ROOT+os.sep+"requests_tiles_"+now.strftime('%Y-%m-%d')+"_errors.txt"
        with open(error_file,'a') as f:
            f.write(errorline+"\n")

    if client and db:
        stats_total = db['stats_total']
        stats = {
            'total': {
                'count': getStat(stats_total, 'total.count', 0)
            }
        }
        print stats
        for desc in settings.TILEJET_LIST_STATS:
            name = desc['name']
            attrs = desc['attributes']
            window = getValue(desc,'window')
            query = None
            if window:
                td = window['delta']
                mintime = now - datetime.timedelta(**td)
                minvalue = mintime.strftime(LOG_FIELD_FORMATS[window['attribute']]) 
                query = {window['attribute']: {"$gte": minvalue}}

            if len(attrs) == 0:
                for doc in getStats(db[desc['collection']],[],query=query):
                    stats[name] = doc['value']

            elif len(attrs) > 0:
                stats[name] = {}
                docs = getStats(db[desc['collection']],[],query=query)
                for doc in docs:
                    v = doc['value']
                    obj = stats[name]
                    for i in range(len(attrs)-1):
                        a = attrs[i]
                        try:
                            obj = obj[doc[a]]
                        except KeyError, e:
                            obj[doc[a]] = {}
                            obj = obj[doc[a]]

                    obj[doc[attrs[len(attrs)-1]]] = v

        #print stats

        if settings.STATS_SAVE_FILE:
            print "Saving to file"
            import json
            commit_to_file(settings.STATS_REQUEST_FILE, json.dumps(stats), binary=False)

        if settings.STATS_SAVE_MEMORY:
            print "Saving to memory"
            commit_to_cache('default', 'stats_tilerequests', stats, GEVENT_MONKEY_PATCH=GEVENT_MONKEY_PATCH)


verbose = False
cycle = 1
while True:
    print "Cycle: ",cycle
    update_stats()
    cycle += 1
    time.sleep(settings.TILEJET_SLEEP_UPDATE_STATS)
