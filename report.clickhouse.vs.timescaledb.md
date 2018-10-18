# Benchmarking TimescaleDB vs. Clickhouse for time-series data 

测试环境

硬件aliyun

	CPU Intel(R) Xeon(R) CPU E5-2682 v4 @ 2.50GHz
	nproc 32
	RAM 128
	NASSSD 1PB
	
	
软件

	postgres 10.5 + timescaledb 1.0.0-dev
	clickhouse 18.12.17


样本使用 metrics_generator.py 生成 ，模拟时间跨度一天 * 10个metric每分钟 * 6944台机器 ~= 一亿(100 million)条监控数据记录。

	
## Setup environment

timescaledb 部分
				
	PGPASSWORD=postgres psql -h127.0.0.1 -p5432 -Upostgres -d postgres

	CREATE TABLE dps (
		endpoint TEXT NOT NULL,
		metric TEXT NOT NULL,
		value DOUBLE PRECISION NOT NULL,
		tags JSONB DEFAULT '{}',
		ts TIMESTAMPTZ NOT NULL
	);
	CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
	SELECT create_hypertable('dps', 'ts');
	CREATE INDEX idx_dp ON dps (endpoint);
	CREATE INDEX idx_metric ON dps (metric);
	CREATE INDEX idx_tags ON dps USING GIN (tags);
	

	INSERT INTO dps (endpoint,metric,value,tags,ts) VALUES ('127.0.0.1','net.in.bytes',85,'{}','2018-10-17'),('127.0.0.1','net.in.bytes',85,'{"face":"eth1"}','2018-10-17');
	select * from dps where tags->>'face' = 'eth1';	
		
	\COPY dps(endpoint,metric,value,tags,ts) FROM '/tmp/sample.100m' (DELIMITER E'\t');


clickhouse 部分
	
	clickhouse-client --host 127.0.0.1 --port 9000 --user default


	CREATE TABLE default.dps (endpoint String, metric String, value Float32, tags String, ts DateTime) ENGINE = MergeTree() PARTITION BY toYYYYMM(ts) ORDER BY (ts, endpoint, metric) SETTINGS index_granularity=8192;	

	INSERT INTO dps (endpoint,metric,value,tags,ts) VALUES ('127.0.0.1','net.in.bytes',85,'{}',toDateTime('2018-10-17 00:00:00')),('127.0.0.1','net.in.bytes',85,'{"face":"eth1"}',toDateTime('2018-10-17 00:00:00'));
	select * from dps where visitParamExtractString(tags, 'face') = 'eth1';
	
	clickhouse-client --query='INSERT INTO dps FORMAT TabSeparated' < sample.data

	


## Benchmarking 

导入数据 36x
		
	time clickhouse-client --port 9000 --query='INSERT INTO dps FORMAT TabSeparated' < /nasssd/sample.100m
	real    0m50.061s
	user    0m17.076s
	sys     0m1.876s

	\COPY dps(endpoint,metric,value,tags,ts) FROM '/nasssd/sample.100m' (DELIMITER E'\t');	
	COPY 99993600
	Time: 1825493.894 ms (30:25.494)
	

count 35x

	select count(*) from dps;
	Time: 2177.037 ms (00:02.177)	
	1 rows in set. Elapsed: 0.062 sec. Processed 99.99 million rows, 399.97 MB (1.62 billion rows/s., 6.49 GB/s.)
	

distinct 163x

	select distinct(metric) from dps where ts > now() - interval '1 day';
	Time: 19773.413 ms (00:19.773)

	select distinct(metric) from dps where ts > now() - 60 * 60 * 24;	
	10 rows in set. Elapsed: 0.121 sec. Processed 48.42 million rows, 1.20 GB (401.69 million rows/s., 9.96 GB/s.)


select 36x
	
	select * from dps where metric='net.out.bytes' and ts > now() - interval '1 day' and tags->>'face' = 'eth1' limit 10;
	Time: 686.961 ms
	
	select * from dps where metric='net.out.bytes' and ts > now() - 86400 and visitParamExtractString(tags, 'face') = 'eth1' limit 10;
	10 rows in set. Elapsed: 0.019 sec. Processed 73.73 thousand rows, 3.10 MB (3.88 million rows/s., 163.04 MB/s.)
	

sum 48x

	select sum(value) from dps where metric='net.out.bytes' and ts > now() - interval '1 day' and tags->>'face' = 'eth1';
	Time: 14759.111 ms (00:14.759)
	
	select sum(value) from dps where metric='net.out.bytes' and ts > now() - 86400 and visitParamExtractString(tags, 'face') = 'eth1';
	1 rows in set. Elapsed: 0.304 sec. Processed 47.93 million rows, 1.59 GB (157.66 million rows/s., 5.23 GB/s.)
	
	
## Conclusion


| Time-series Database | Clickhouse | TimescaleDB |
| ------------- | ------------- |------------- |
| 导入数据(load data) | 36x  | - |
| count 查询 | 35x  | - |
| distinct 查询 | 163x | - |
| select 查询 | 36x  | - |
| sum 聚合查询 | 48x  | - |
| 综合查询 | 36~163x | - |


| Time-series Database | Clickhouse | TimescaleDB |
| ------------- | ------------- |------------- |
| JSON类型 | 有限支持 exist/get  | 完整支持 CRUD 字段 |
| JSON类型索引 | 不支持，纯字符串匹配 | 支持 |
