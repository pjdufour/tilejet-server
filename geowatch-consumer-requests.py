import time

from django.conf import settings

from geowatchutil.client import create_client
from geowatchutil.consumer import create_consumer, receive_tile_requests
from geowatchutil.decoder import decode_tile_request
from geowatchutil.runtime import acquire_consumer

from tilejetserver.cache.tasks import taskRequestTile

from tilejetserver.geowatch import acquire_geowatch_consumer

verbose=False
enabled = settings.TILEJET_GEOWATCH_ENABLED
backend = settings.TILEJET_GEOWATCH_STREAMING_BACKEND
topic = settings.TILEJET_GEOWATCH_TOPIC_REQUESTS
count = settings.TILEJET_GEOWATCH_COUNT_REQUESTS

client, consumer = acquire_geowatch_consumer(topic, max_tries=3, sleep_period=5, verbose=verbose)

if not consumer:
    print "Could not get lock on GeoWatch server after "+str(tries)+" tries."
else:
    print "Consumer locked.  Starting consuming message"
    cycle = 0
    while True:
        seen = set()
        print "Cycle: "+str(cycle)
        requests = consumer.receive_tile_requests(
            count,
            timeout = 4,
            ttl = settings.TILEJET_GEOWATCH_TTL,
        )
        if requests:
            print "Processing "+str(len(requests))+" indirect tile requests"
            for r in requests:
                if r in seen:
                    continue
                seen.add(r)
                r2 = decode_tile_request(r)
                if verbose:
                    print "Requesting"+str(r2)
                taskRequestTile(
                    r2['layer'],
                    r2['z'],
                    r2['x'],
                    r2['y'],
                    r2['extension'],
                    verbose=True
                )
        else:
            print "No indirect tile requests"
        print str(len(seen))+" unique tile requests out of "+str(len(requests))+"."
        cycle += 1
        time.sleep(settings.TILEJET_GEOWATCH_SLEEP_REQUESTS)
