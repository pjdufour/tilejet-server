CMD=~/kafka_2.10-0.8.2.0/bin/kafka-topics.sh
ZK='localhost:8002'
# logging of all tilerequests in mongodb
$CMD --create --zookeeper $ZK --replication-factor 1 --partitions 1 --topic logs
# indirect tile requests
$CMD --create --zookeeper $ZK --replication-factor 1 --partitions 1 --topic requests
# statistics tracks need to increment mongo stats
$CMD --create --zookeeper $ZK --replication-factor 1 --partitions 1 --topic statistics
