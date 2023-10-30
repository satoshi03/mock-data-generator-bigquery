#!/bin/python

import argparse
import json
import random
import string
from datetime import datetime as dt
from datetime import timedelta
from six import string_types


parser = argparse.ArgumentParser(description="generate mock data for BigQuery.")
parser.add_argument('input', metavar='FILE', help='input schema file.')
parser.add_argument('-l', metavar='-l', type=int, default=1000, help='output mock data raws. (default: 1000)')
parser.add_argument('-o', metavar='-o', default='output.json', help='output mock data file. (default: output.json)')
parser.add_argument('-t', metavar='-t', default='bigquery', help='the type of the input file. (default: bigquery)')

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
    elif t == 'FLOAT64':
        return random.uniform(DUMMY_RAND_FLOAD_MIN, DUMMY_RAND_FLOAT_MIN)
    elif t == 'INT64':
        return random.randint(DUMMY_RAND_INT_MIN, DUMMY_RAND_INT_MAX)
    elif t == 'INTEGER':
        return random.randint(DUMMY_RAND_INT_MIN, DUMMY_RAND_INT_MAX)
    elif t == 'FLOAT':
        return random.randint(DUMMY_RAND_FLOAD_MIN, DUMMY_RAND_INT_MAX - 1) + random.random()
    elif  t == 'TIMESTAMP':
        return random_timestamp(DUMMY_RAND_TIMESTAMP_MIN, DUMMY_RAND_TIMESTAMP_MAX)
    elif t == 'BOOLEAN':
        return bool(random.getrandbits(1))
    else:
        print("not found type: " + t)


def generate(schema):
    dic = {}
    for column in schema:
        if column['MODE'] == 'REPEAT':
            if column['TYPE'] == 'RECORD':
                dic[column['NAME']] = [generate(column['FIELDS']) for i in range(0, random.randrange(MAX_REPEAT_NUM) + 1)]
            else:
                dic[column['NAME']] = [mockdata(column['TYPE']) for i in range(0, random.randrange(MAX_REPEAT_NUM) + 1)]
        else:
            if column['MODE'] == 'NULLABLE':
                if random.randint(0, 1):
                    continue

            if column['TYPE'] == 'RECORD':
                dic[column['NAME']] = generate(column['FIELDS'])
            else:
                dic[column['NAME']] = mockdata(column['TYPE'])
    return dic


def to_upper(schema):
    l = []
    for column in schema:
        d = {}
        for k, v in column.items():
            if isinstance(k, string_types):
                k = k.upper()
            if isinstance(v, string_types):
                if k != 'NAME':
                    v = v.upper()
            if isinstance(v, list):
                v = to_upper(v)
            d[k] = v
        l.append(d)
    return l


if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.input, 'r') as input_json_file, open(args.o, 'w') as output_json_file:
        if args.t != 'bigquery':
            schema = to_upper(json.load(input_json_file))
            for l in range(0, args.l):
                output_json_file.write(json.dumps(generate(schema)) + '\n')
        else:
            lines = input_json_file.readlines()
            header = ",".join([line.split(" ")[0] for line in lines])
            output_json_file.write(header + '\n')
            for i in range(0, args.l):
                output_json_file.write(",".join([str(mockdata(line.split(" ")[1].strip())) for line in lines]) + '\n')
