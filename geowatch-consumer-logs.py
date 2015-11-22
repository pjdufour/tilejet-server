import time

from django.conf import settings

from geowatchutil.client import create_client
from geowatchutil.consumer import create_consumer, receive_tile_requests, decode_tile_request
from geowatchutil.runtime import acquire_consumer

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
topic = settings.TILEJET_GEOWATCH_TOPIC_LOGS
count = settings.TILEJET_GEOWATCH_COUNT_LOGS
mongo_host = settings.TILEJET_MONGODB_HOST
mongo_port = settings.TILEJET_MONGODB_PORT
mongo_name = settings.TILEJET_MONGODB_NAME
mongo_collection = settings.TILEJET_COLLECTION_LOGS
list_stats = settings.TILEJET_LIST_STATS

print "GeoWatch Settings"
print "Host: "+host
print "Topic: "+topic

gw_client, consumer = acquire_consumer(host=host, topic=topic, max_tries=12, sleep_period=5)
if not consumer:
    print "Could not get lock on GeoWatch server after "+str(tries)+" tries."
else:
    print "Consumer locked.  Initialized producer for statistics"
    gw_client, producer = create_producer(client=gw_client)
    print "Starting consuming message"
    # Import Gevent and monkey patch
    try:
        from gevent import monkey
        monkey.patch_all()
    except:
        print "gevent monkey patch failed"
    from pymongo import MongoClient
    m_client, m_db = connect_to_mongodb(host=mongo_host, port=mongo_port, name=mongo_name)
    if m_client and m_db:
        cycle = 0
        while True:
            print "Cycle: "+str(cycle)
            requests = receive_messages(
                topic,
                count = count,
                timeout = 4,
                ttl = settings.TILEJET_GEOWATCH_TTL,
                consumer = consumer
            )
            if requests:
                print "Processing "+str(len(requests))+" tile request logs"
                for r in requests:
                    r2 = decode_tile_request_log(r)
                    if verbose:
                        print "Logging"+str(r2)
                    r3 = buildTileRequestDocument(** log_entry)
                    if r3:
                        store_success = True
                        try:
                            db[mongo_collection].insert(r3, w=0)
                        except:
                            print "Error saving Log to MongoDB"
                            store_success = False
                        if store_success:
                            send_json(topic_statistics, buildStats(list_stats, r3), producer=producer)

            else:
                if verbose:
                    print "No tile requests to log"
            cycle += 1
            time.sleep(settings.TILEJET_GEOWATCH_SLEEP_LOGS)

