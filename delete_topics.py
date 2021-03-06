from django.conf import settings

from geowatchdjango.utils import provision_geowatch_client

verbose = True

enabled = settings.GEOWATCH_ENABLED

if not enabled:
    print "GeoWatch not enabled via settings"

topic_requests = settings.TILEJET_GEOWATCH_TOPIC_REQUESTS
topic_logs = settings.TILEJET_GEOWATCH_TOPIC_LOGS
topic_stats = settings.TILEJET_GEOWATCH_TOPIC_STATS

if enabled:
    client = provision_geowatch_client()
    print client.list_topics(limit=100, verbose=verbose)
    topics = [topic_requests, topic_logs, topic_stats]
    client.delete_topics(topics)
    print "Final Check..."
    print client.list_topics(limit=100, verbose=verbose)

else:
    print "Missing settings"
