from django.conf import settings

from boto import kinesis


aws_access_key_id=settings.AWS_ACCESS_KEY_ID
aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
region = settings.TILEJET_GEOWATCH_KINESIS_REGION
stream_name_requests = settings.TILEJET_GEOWATCH_STREAM_REQUESTS
stream_name_logs = settings.TILEJET_GEOWATCH_STREAM_LOGS
stream_name_stats = settings.TILEJET_GEOWATCH_STREAM_STATS

if region and stream_name_requests:
    kinesis = kinesis.connect_to_region(
        region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    streams = kinesis.list_streams(limit=100)
    stream_names = streams[u'StreamNames']
    print streams

    # Requests
    if not stream_name_requests in stream_names:
        print "Stream "+stream_name_requests+" doesn't exist."
    else:
        kinesis.delete_stream(stream_name_requests)

    # Logs
    if not stream_name_logs in stream_names:
        print "Stream "+stream_name_logs+" doesn't exist."
    else:
        kinesis.delete_stream(stream_name_logs)

    # Stats
    if not stream_name_stats in stream_names:
        print "Stream "+stream_name_stats+" doesn't exist."
    else:
        kinesis.delete_stream(stream_name_stats)

    # Final Check
    print "Final Check..."
    print "** FYI... AWS Streams don't delete synchronously so it may be a few seconds.  Just re-run delete_streams.py to confirm."
    streams = kinesis.list_streams(limit=100)
    print streams

else:
    print "Missing settings"
