from django.conf import settings

from geowatchdjango.utils import provision_geowatch_consumer

from tilejetserver.broker import TileJetBrokerStats

verbose = True
enabled = settings.GEOWATCH_ENABLED
topic = settings.TILEJET_GEOWATCH_TOPIC_STATS
count = settings.TILEJET_GEOWATCH_COUNT_STATS
sleep_period = settings.TILEJET_GEOWATCH_SLEEP_STATS
mongodb_host = settings.TILEJET_MONGODB_HOST
mongodb_port = settings.TILEJET_MONGODB_PORT
mongodb_name = settings.TILEJET_MONGODB_NAME
timeout = 5
max_tries = 3
client, consumer = provision_geowatch_consumer(topic, "GeoWatchCodecJSON", max_tries=max_tries, sleep_period=sleep_period, topic_check=False, verbose=verbose)

if not consumer:
    print "Could not get lock on GeoWatch server after "+str(max_tries)+" tries."
else:
    broker = TileJetBrokerStats(
        consumer=consumer,
        sleep_period=sleep_period,
        count=count,
        timeout=timeout,
        mongodb_host=mongodb_host,
        mongodb_port=mongodb_port,
        mongodb_name=mongodb_name,
        verbose=verbose)
    broker.run()
