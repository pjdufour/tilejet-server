#!/bin/bash
#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#export LOG_DIR="$DIR/logs/kafka"
#export KAFKA_LOG4J_OPTS="-Dlog4j.configuration=file:$DIR/log4j.properties"
#export KAFKA_HEAP_OPTS="-Xmx1G -Xms1G"
#exec kafka-run-class.sh -name kafkaServer -loggc kafka.Kafka kafka.properties
rm -fr /tmp/kafka-logs/
~/kafka_2.10-0.8.2.0/bin/kafka-server-start.sh kafka.properties
