# Benchmarking Clickhouse no-JSON vs JSON 

CK查询有无JSON匹配对比。


测试环境

硬件aliyun

	CPU Intel(R) Xeon(R) CPU E5-2682 v4 @ 2.50GHz
	nproc 32
	RAM 128
	NASSSD 1PB
	
	
软件

	clickhouse 18.12.17
	
数据样本使用 metrics_generator_ck.sh 生成，生成一亿条记录大概耗时 2m44.897s 。
	
		
10m 4+

	select count() from dps where metric='net.in.bytes';
	select count() from dps where metric='net.in.bytes' and visitParamExtractString(tags, 'face') = 'eth1';

	
10m 2+

	select sum(value) from dps where metric in ('net.out.bytes', 'net.in.bytes');
	select sum(value) from dps where metric in ('net.out.bytes', 'net.in.bytes') and visitParamExtractString(tags, 'face') = 'eth1';

	
100m 6+

	select count() from dps;
	select count() from dps where visitParamExtractString(tags, 'face') = 'eth1';

	
	
50b 3+
	
	select sum(value) from dps where metric in ('net.out.bytes', 'net.in.bytes');
	select sum(value) from dps where metric in ('net.out.bytes', 'net.in.bytes') and visitParamExtractString(tags, 'face') = 'eth1';

	
50b 5+
	
	select count() from dps where metric='net.in.bytes';
	select count() from dps where metric='net.in.bytes' and visitParamExtractString(tags, 'face') = 'eth1';


m表示 million 百万级别条记录，b 表示 billion 十亿级别条记录。


## Conclusion

使用 JSON visitParamExtractString 类函数匹配慢 2~6倍。
