#!/usr/bin/env bash
# Usage: metrics_generator_ck.sh <records>

echo "insert into dps(ts,endpoint,metric,value,tags) select now() - rand()%604800, IPv4NumToString(rand()), concat('m_', toString(rand()%50)), rand()%10 , concat(concat('{\"face\":\"eth', toString(rand()%2)), '\"}') from system.numbers limit $1" | clickhouse-client --port 9000


