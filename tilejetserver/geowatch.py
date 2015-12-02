from django.conf import settings

from geowatchutil.runtime import acquire_consumer

def acquire_geowatch_consumer(topic, max_tries=12, sleep_period=5, verbose=True):
    backend = settings.TILEJET_GEOWATCH_STREAMING_BACKEND
    topic_prefix = settings.TILEJET_GEOWATCH_TOPIC_PREFIX
    # Kinesis
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    region = settings.TILEJET_GEOWATCH_KINESIS_REGION
    # Kafka
    host = settings.TILEJET_GEOWATCH_HOST

    print "GeoWatch Settings"
    print "Host: "+host
    print "Topic: "+topic
    print "Count: "+str(count)

    client = None
    consumer = None
    if backend == "kafka"
        client, consumer = acquire_consumer_kafka(
            backend,
            host=host,
            topic=topic,
            topic_prefix=topic_prefix,
            max_tries=max_tries,
            sleep_period=sleep_period)
    elif backend == "kinesis"
        client, consumer = acquire_consumer_kinesis(
            backend,
            aws_region=aws_region,
            aws_access_key_id=aws_acccess_key_id,
            aws_secret_access_key=aws_secret_access_key,
            topic=topic,
            topic_prefix=topic_prefix,
            max_tries=max_tries,
            sleep_period=sleep_period
        )

    return (client, consumer)

def acquire_geowatch_producer(topic, verbose=True):
    backend = settings.TILEJET_GEOWATCH_STREAMING_BACKEND
    topic_prefix = settings.TILEJET_GEOWATCH_TOPIC_PREFIX
    # Kinesis
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    region = settings.TILEJET_GEOWATCH_KINESIS_REGION
    # Kafka
    host = settings.TILEJET_GEOWATCH_HOST

    print "GeoWatch Settings"
    print "Host: "+host
    print "Topic: "+topic
    print "Count: "+str(count)

    client = None
    producer = None
    if backend == "kafka"
        client, producer = acquire_producer_kafka(
            backend,
            host=host,
            topic=topic,
            topic_prefix=topic_prefix,
            max_tries=max_tries,
            sleep_period=sleep_period)
    elif backend == "kinesis"
        client, producer = acquire_producer_kinesis(
            backend,
            aws_region=aws_region,
            aws_access_key_id=aws_acccess_key_id,
            aws_secret_access_key=aws_secret_access_key,
            topic=topic,
            topic_prefix=topic_prefix,
            max_tries=max_tries,
            sleep_period=sleep_period
        )

    return (client, producer)
