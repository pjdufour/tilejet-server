import time

from django.conf import settings

from geowatchutil.client import create_client
from geowatchutil.consumer import receive_tile_requests, decode_tile_request, receive_messages
from geowatchutil.decoder import decode_tile_request_log
from geowatchutil.producer import create_producer, send_json
from geowatchutil.runtime import acquire_consumer

from tilejetlogs.tilelogs import buildTileRequestDocument
from tilejetstats.mongodb import buildStats, incStats

from tilejetserver.cache.tasks import taskRequestTile


def connect_to_mongodb(host=None, port=None, name=None):
    client = None
    db = None
    try:
        if port:
            client = MongoClient(host, port)
        else:
            client = MongoClient(host)
    except:
        client = None
    if client:
        try:
            db = client[name]
        except:
            db = None
            try:
                client.close()
            except:
                client = None
            client = None
    return (client, db)


verbose=False
# Initialize Settings
host = settings.TILEJET_GEOWATCH_HOST
topic_logs = settings.TILEJET_GEOWATCH_TOPIC_LOGS
count_logs = settings.TILEJET_GEOWATCH_COUNT_LOGS
topic_stats = settings.TILEJET_GEOWATCH_TOPIC_STATS
mongo_host = settings.TILEJET_MONGODB_HOST
mongo_port = settings.TILEJET_MONGODB_PORT
mongo_name = settings.TILEJET_MONGODB_NAME
mongo_collection = settings.TILEJET_COLLECTION_LOGS
list_stats = settings.TILEJET_LIST_STATS

print "GeoWatch Settings"
print "Host: "+host
print "Input Topic: "+topic_logs
print "Output Topic: "+topic_stats
print "Count: "+str(count_logs)

client_consumer, consumer = acquire_consumer(host=host, topic=topic_logs, max_tries=3, sleep_period=5)
if not consumer:
    print "Could not get lock on GeoWatch server after "+str(tries)+" tries."
else:
    print "Consumer locked.  Initializing producer for statistics"
    client_producer, producer = create_producer(host=host)
    print "Starting consuming message"
    # ! Cannot Gevent Monkey Patch, since it's not comaptible with python-kafka
    # ! also the benefits might that be great for a consumer, since it isn't part of 
    # ! request/response cycle
    # !
    # Import Gevent and monkey patch
    #try:
    #    from gevent import monkey
    #    monkey.patch_all()
    #except:
    #    print "gevent monkey patch failed"
    from pymongo import MongoClient
    m_client, m_db = connect_to_mongodb(host=mongo_host, port=mongo_port, name=mongo_name)
    if m_client and m_db:
        cycle = 0
        while True:
            print "Cycle: "+str(cycle)
            try:
                requests = receive_messages(
                    topic_logs,
                    count = count_logs,
                    timeout = 4,
                    ttl = settings.TILEJET_GEOWATCH_TTL,
                    consumer = consumer
                )
            except IOError, e:
                print "Could not receive messages, b/c IO Error.  Skipping to next cycle"
                print e
                continue

            if requests:
                print "Processing "+str(len(requests))+" tile request logs"
                for r in requests:
                    r2 = decode_tile_request_log(r)
                    if verbose:
                        print "Logging"+str(r2)
                    r3 = buildTileRequestDocument(** r2)
                    if r3:
                        store_success = True
                        print r3
                        #try:
                        m_db[mongo_collection].insert(r3, w=0)
                        #except:
                        #    print "Error saving Log to MongoDB"
                        #    store_success = False
                        if store_success:
                            send_json(topic_stats, buildStats(list_stats, r3), producer=producer)

            else:
                if verbose:
                    print "No tile requests to log"
            cycle += 1
            time.sleep(settings.TILEJET_GEOWATCH_SLEEP_LOGS)

