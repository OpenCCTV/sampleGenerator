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
	
		
测试SQL

	select count() from dps;
	select count() from dps where visitParamExtractString(tags, 'face') = 'eth1';
	
	select sum(value) from dps where metric in ('net.out.bytes', 'net.in.bytes');
	select sum(value) from dps where metric in ('net.out.bytes', 'net.in.bytes') and visitParamExtractString(tags, 'face') = 'eth1';

	
m表示 million 百万级别条记录，b 表示 billion 十亿级别条记录，耗时单位毫秒ms。


| 100m | noJSON | JSON |
| ---- | ---- | ---- |
| count | 56 | 351 |
| sum | 250 | 577 |


| 56b | noJSON | JSON |
| ---- | ---- | ---- |	
| count | 3719 | 154620 |
| sum | 75630 | 223893 |



## Conclusion

使用 JSON visitParamExtractString 类函数匹配在 亿级记录慢 2~6倍，在百亿级慢 3~41 倍 。
