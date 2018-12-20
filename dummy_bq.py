#!/bin/python

import argparse
import json
import random
import string
from datetime import datetime as dt
from datetime import timedelta


parser = argparse.ArgumentParser(description="generate mock data for BigQuery.")
parser.add_argument('input', metavar='FILE', help='input schema file.')
parser.add_argument('-l', metavar='-l', type=int, default=1000, help='output mock data raws. (default: 1000)')
parser.add_argument('-o', metavar='-o', default='output.json', help='output mock data file. (default: output.json)')

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

DUMMY_RAND_INT_MIN = 1
DUMMY_RAND_INT_MAX = 10000

DUMMY_RAND_FLOAD_MIN = 1
DUMMY_RAND_FLOAT_MIN = 10000

DUMMY_RAND_TIMESTAMP_MIN = dt.now() - timedelta(1)
DUMMY_RAND_TIMESTAMP_MAX = dt.now()

MAX_REPEAT_NUM = 5

def random_str(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_timestamp(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return (start + timedelta(seconds=random_second)).strftime(TIMESTAMP_FORMAT)


def mockdata(t):
    if t == 'STRING':
        return random_str()
    elif t == 'INTEGER':
        return random.randint(DUMMY_RAND_INT_MIN, DUMMY_RAND_INT_MAX)
    elif t == 'FLOAT':
        return random.randint(DUMMY_RAND_FLOAD_MIN, DUMMY_RAND_INT_MAX - 1) + random.random()
    elif  t == 'TIMESTAMP':
        return random_timestamp(DUMMY_RAND_TIMESTAMP_MIN, DUMMY_RAND_TIMESTAMP_MAX)
    elif t == 'BOOLEAN':
        return bool(random.getrandbits(1))


def generate(schema):
    dic = {}
    for column in schema:
        if column['mode'] == 'REPEAT':
            if column['type'] == 'RECORD':
                dic[column['name']] = [generate(column['FIELDS']) for i in range(0, random.randrange(MAX_REPEAT_NUM) + 1)]
            else:
                dic[column['name']] = [mockdata(column['type']) for i in range(0, random.randrange(MAX_REPEAT_NUM) + 1)]
        else:
            if column['mode'] == 'NULLABLE':
                if random.randint(0, 1):
                    continue

            if column['type'] == 'RECORD':
                dic[column['name']] = generate(column['FIELDS'])
            else:
                dic[column['name']] = mockdata(column['type'])
    return dic


def to_upper(schema):
    l = []
    for column in schema:
        d = {}
        for k, v in column.items():
            if isinstance(k, str):
                k = k.upper()
            if isinstance(v, str):
                if k != 'name':
                    v = v.upper()
            if isinstance(v, list):
                v = to_upper(v)
            d[k] = v
        l.append(d)
    return l


if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.input, 'r') as ijf, open(args.o, 'w') as ojf:
        schema = to_upper(json.load(ijf))
        for l in range(0, args.l):
            ojf.write(json.dumps(generate(schema)) + '\n')
