from django.conf import settings

from boto import kinesis

from geowatchutil.client import create_client

verbose = True

enabled = settings.TILEJET_GEOWATCH_ENABLED

if not enabled:
    print "GeoWatch not enabled via settings"

backend = settings.TILEJET_GEOWATCH_STREAMING_BACKEND
topic_prefix = settings.TILEJET_GEOWATCH_TOPIC_PREFIX
topic_requests = settings.TILEJET_GEOWATCH_TOPIC_REQUESTS
topic_logs = settings.TILEJET_GEOWATCH_TOPIC_LOGS
topic_stats = settings.TILEJET_GEOWATCH_TOPIC_STATS
# Kafka
host = settings.TILEJET_GEOWATCH_HOST
# Kinesis
aws_region = settings.TILEJET_GEOWATCH_KINESIS_REGION
aws_access_key_id=settings.AWS_ACCESS_KEY_ID
aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY

if enabled:
    client = None
    if backend == "kafka":
        client = create_client_kafka(host, topic_prefix)
    elif backend == "kinesis":
        client = create_client_kinesis(aws_region, aws_access_key_id, aws_secret_access_key, topic_prefix)

    topics = client.list_topics(limit=100, verbose=verbose)
    print topics 
    client.create_topic(topic_requests)
    client.create_topic(topic_logs)
    client.create_topic(topic_stats)
    print "Final Check..."
    topics = client.list_topics(limit=100, verbose=verbose)
    print topics

else:
    print "Missing settings"
