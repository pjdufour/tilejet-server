from django.conf import settings

from geowatchdjango.utils import provision_geowatch_consumer

from tilejetserver.broker import TileJetBrokerTileRequests

verbose = False
enabled = settings.GEOWATCH_ENABLED
topic = settings.TILEJET_GEOWATCH_TOPIC_REQUESTS
count = settings.TILEJET_GEOWATCH_COUNT_REQUESTS
sleep_period = settings.TILEJET_GEOWATCH_SLEEP_REQUESTS
timeout = 5
max_tries = 3
client, consumer = provision_geowatch_consumer(topic, "GeoWatchCodecTileRequest", max_tries=max_tries, sleep_period=5, verbose=verbose)

if not consumer:
    print "Could not get lock on GeoWatch server after "+str(max_tries)+" tries."
else:
    broker = TileJetBrokerTileRequests(
        consumer=consumer,
        sleep_period=sleep_period,
        count=count,
        timeout=timeout,
        deduplicate=True,
        verbose=verbose)
    broker.run()
