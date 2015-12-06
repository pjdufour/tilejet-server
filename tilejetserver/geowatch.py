import time
from django.conf import settings

from geowatchdjango.utils import provision_geowatch_client, provision_geowatch_producer


def provision_client_logs_requests(topic_check=False, verbose=False):
    start = time.time()
    gw_client = provision_geowatch_client()
    end = time.time()
    print "Duration 1: ", (end - start)
    start = end
    gw_client, gw_requests = provision_geowatch_producer(
        settings.TILEJET_GEOWATCH_TOPIC_REQUESTS,
        "GeoWatchCodecTileRequest",
        client=gw_client,
        max_tries=5,
        sleep_period=0.25,
        topic_check=topic_check,
        verbose=verbose)
    end = time.time()
    print "Duration 2: ", (end - start)
    start = end
    gw_client, gw_logs = provision_geowatch_producer(
        settings.TILEJET_GEOWATCH_TOPIC_LOGS,
        "GeoWatchCodecPlain",
        client=gw_client,
        max_tries=5,
        sleep_period=0.25,
        topic_check=topic_check,
        verbose=verbose)
    end = time.time()
    print "Duration 3: ", (end - start)
    return (gw_client, gw_logs, gw_requests)
