import time

from django.conf import settings

from geowatchdjango.utils import provision_geowatch_consumer, provision_geowatch_producer
from geowatchutil.codec.base import decode_tile_request_log, decode_tile_request
from geowatchutil.broker.base import GeoWatchBroker

from tilejetserver.cache.tasks import taskRequestTile
from tilejetlogs.tilelogs import buildTileRequestDocument
from tilejetstats.mongodb import buildStats

from pymongo import MongoClient


def connect_to_mongodb(host=None, port=None, name=None):
    client = None
    db = None
    #try:
    if 1==1:
        if port:
            client = MongoClient(host, port)
        else:
            client = MongoClient(host)
    #except:
    #    client = None
    if client:
        #try:
        if 1==1:
            db = client[name]
        #except:
        #    db = None
        #    try:
        #        client.close()
        #    except:
        #        client = None
        #    client = None
    return (client, db)

class TileJetBrokerTileRequests(GeoWatchBroker):

    def _pre(self):
        pass

    def _post(self, messages=None):

        for m in messages:
            tr = decode_tile_request(m)
            if self.verbose:
                print "Requesting: ",tr
            taskRequestTile(
                tr['layer'],
                tr['z'],
                tr['x'],
                tr['y'],
                tr['extension'],
                verbose=self.verbose)

    def __init__(self, consumer=None, sleep_period=5, count=1, timeout=5, deduplicate=False, verbose=False):
        super(TileJetBrokerTileRequests, self).__init__(
            consumers=[consumer],
            count=count,
            threads=1,
            sleep_period=sleep_period,
            timeout=timeout,
            deduplicate=deduplicate,
            verbose=verbose)


class TileJetBrokerLogs(GeoWatchBroker):

    _m_client = None
    _m_db = None
    _m_collection = None
    _list_stats = None
    _producer_stats = None

    def _pre(self):
        pass

    def _post(self, messages=None):

        if messages:
            r3_list = []
            for r in messages:
                r2 = decode_tile_request_log(r)
                if self.verbose:
                    print "Logging: ",r2
                r3 = buildTileRequestDocument(** r2)
                r3_list.append(r3)

            #print "_m_client: ",self._m_client 
            #print "_m_db: ",self._m_db 
            self._m_db[self._m_collection].insert(r3_list, w=0)
            for r3 in r3_list:
                self._producer_stats.send_json(data=buildStats(self._list_stats, r3))

    def __init__(self, consumer=None, sleep_period=5, count=1, timeout=5, mongodb_host=None, mongodb_port=None, mongodb_name=None, mongodb_collection=None, list_stats=None, producer_stats=None, verbose=False):
        super(TileJetBrokerLogs, self).__init__(
            consumers=[consumer],
            count=count,
            threads=1,
            sleep_period=sleep_period,
            timeout=timeout,
            deduplicate=False,
            verbose=verbose)

        # from pymongo import MongoClient
        m_client, m_db = connect_to_mongodb(host=mongodb_host, port=mongodb_port, name=mongodb_name)
        self._m_client = m_client
        self._m_db = m_db
        self._m_collection = mongodb_collection
        self._list_stats = list_stats
        self._producer_stats = producer_stats


class TileJetBrokerStats(GeoWatchBroker):

    _m_client = None
    _m_db = None

    def _pre(self):
        pass

    def _post(self, messages=None):

        for stats in messages:
            if self.verbose:
                print "Incrementing stats "+str(stats)
            for stat in stats:
                # try:
                if 1==1:
                    collection = self._m_db[stat['collection']]
                    collection.update(stat['attributes'], {'$set': stat['attributes'], '$inc': {'value': 1}}, upsert=True, w=0)
                # except:
                #     print "Issues with stats upsert"


    def __init__(self, consumer=None, sleep_period=5, count=1, timeout=5, mongodb_host=None, mongodb_port=None, mongodb_name=None, verbose=False):
        super(TileJetBrokerStats, self).__init__(
            consumers=[consumer],
            count=count,
            threads=1,
            sleep_period=sleep_period,
            timeout=timeout,
            deduplicate=False,
            verbose=verbose)

        # from pymongo import MongoClient
        m_client, m_db = connect_to_mongodb(host=mongodb_host, port=mongodb_port, name=mongodb_name)
        self._m_client = m_client
        self._m_db = m_db
