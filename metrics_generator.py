#!/usr/bin/env python
#coding:utf8
"""
Generate monitor metrics samples for benchmarking.
"""
import datetime
import os
import random
import ipaddress

METRICS = (
    ('net.in.drop', ('eth0', 'eth1')),
    ('net.in.packets', ('eth0', 'eth1')),
    ('net.in.bytes', ('eth0', 'eth1')),
    ('net.in.errs', ('eth0', 'eth1')),

    ('net.out.bytes', ('eth0', 'eth1')),
    ('net.out.errs', ('eth0', 'eth1')),
    ('net.out.drop', ('eth0', 'eth1')),
    ('net.out.packets', ('eth0', 'eth1')),

    ('load.1min', None),
    ('load.5min',None),
)



def generate_endpoint_metrics(now, endpoint):
    ts_start = datetime.datetime(year=now.year,month=now.month, day=now.day)
    ts_end  = datetime.datetime(year=now.year,month=now.month, day=now.day)  + datetime.timedelta(days=1)
#    ts_end  = datetime.datetime(year=now.year,month=now.month, day=now.day)  + datetime.timedelta(minutes=1)
    step = datetime.timedelta(minutes=1)
    cur = ts_start
    lines = []
    while cur < ts_end:
        ts = cur

        for metric, tags in METRICS:
            if not tags:
                tags = "{}"
            else:
                tags = '{"face":"%s"}' % random.choice(tags)

            value = random.randrange(1, 10)

            line = "{endpoint}\t{metric}\t{value}\t{tags}\t{ts}".format(
                endpoint=endpoint,
                metric=metric,
                value=value,
                tags=tags,
                ts=ts,
            )
            lines.append(line)

        cur += step
    return lines

def append_lines(save_to, lines):
    with open(save_to, "a") as f:
        f.write("\n".join(lines)+"\n")

def main(total_endpoint, save_to):
    now = datetime.datetime.today()

    endpoint_n = 0
    while endpoint_n < total_endpoint:
        bits = random.getrandbits(32)
        addr = ipaddress.IPv4Address(bits)
        addr_str  = str(addr)
        endpoint = addr_str

        append_lines(save_to=save_to, lines=generate_endpoint_metrics(now=now, endpoint=endpoint))

        endpoint_n += 1

def guess_size(lines, line_size):
    total_size = lines * line_size
    
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    TB = GB * 1024
    PB = TB * 1024
	
    idx = 0
    tokens = []
    while total_size > 1024:
        idx += 1
	total_size /= 1024
    tokens.append(str(total_size))
    try:
        unit = units[idx]
    except IndexError:
        unit = 'unknown'

    tokens.append(unit)
    return "".join(tokens)


if __name__ == '__main__':
    import argparse

    DEFAULT_SAVE_TO = "/tmp/sample.data"
    DEFAULT_SAMPLE_LINE_SIZE = 60

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=10, help="total endpoints")
    parser.add_argument("-y", action="store_true", default=False, help="noinput")
    parser.add_argument("-o", default=DEFAULT_SAVE_TO, help="full path to output file")
    args =  parser.parse_args()

    total_endpoint = args.n
    total_metrics = len(METRICS)
    total_points_one_day = 60 * 24
    total_lines = total_endpoint * total_metrics * total_points_one_day

    size_in_human = guess_size(lines=total_lines, line_size=DEFAULT_SAMPLE_LINE_SIZE)
    if not args.y:
        msg = "it will generates (%d endpoints * %d metrics * %d points one day) = %d lines (~%s), ok? [y/N] " % \
		(total_endpoint, total_metrics, total_metrics, total_lines, size_in_human)
        aws = raw_input(msg)
        if aws.lower() != "y":
            exit(1)
    
    main(total_endpoint=args.n, save_to=args.o)
