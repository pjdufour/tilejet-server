from django.conf import settings

from geowatchdjango.utils import provision_geowatch_consumer, provision_geowatch_producer

from tilejetserver.broker import TileJetBrokerLogs

verbose = False
enabled = settings.GEOWATCH_ENABLED
topic_logs = settings.TILEJET_GEOWATCH_TOPIC_LOGS
count_logs = settings.TILEJET_GEOWATCH_COUNT_LOGS
sleep_period = settings.TILEJET_GEOWATCH_SLEEP_LOGS
mongodb_host = settings.TILEJET_MONGODB_HOST
mongodb_port = settings.TILEJET_MONGODB_PORT
mongodb_name = settings.TILEJET_MONGODB_NAME
topic_stats = settings.TILEJET_GEOWATCH_TOPIC_STATS
mongodb_collection = settings.TILEJET_COLLECTION_LOGS
list_stats = settings.TILEJET_LIST_STATS

timeout = 5
max_tries = 3
client_consumer, consumer = provision_geowatch_consumer(topic_logs, "GeoWatchCodecPlain", max_tries=max_tries, sleep_period=sleep_period, topic_check=False, verbose=verbose)

if not consumer:
    print "Could not get lock on GeoWatch server after "+str(max_tries)+" tries."
else:
    print "Consumer locked.  Initializing producer for statistics"
    client_producer, producer = provision_geowatch_producer(topic_stats, "GeoWatchCodecJSON", max_tries=3, sleep_period=5, verbose=verbose)
    broker = TileJetBrokerLogs(
        consumer=consumer,
        sleep_period=sleep_period,
        count=count_logs,
        timeout=timeout,
        mongodb_host=mongodb_host,
        mongodb_port=mongodb_port,
        mongodb_name=mongodb_name,
        mongodb_collection=mongodb_collection,
        list_stats=list_stats,
        producer_stats=producer,
        verbose=verbose)
    broker.run()
