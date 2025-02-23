from os import path, listdir
import re
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path')
args = parser.parse_args()


def get_value_by_regex(regex_pattern, line):
    value = re.search(regex_pattern, line)
    return value.group(0) if value else '-'


def parse_file(filepath):
    ips = {}
    methods = {
        'GET': 0,
        'HEAD': 0,
        'OPTIONS': 0,
        'TRACE': 0,
        'PUT': 0,
        'DELETE': 0,
        'POST': 0,
        'PATCH': 0,
        'CONNECT': 0
    }

    res_list = []

    regex_ip = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
    regex_date = re.compile(r'\[.+ \+\d{4}\]')
    regex_method = re.compile(r'GET|HEAD|OPTIONS|TRACE|PUT|DELETE|POST|PATCH|CONNECT')
    regex_url = re.compile(r'http[s]?://[\w\./-]+')
    regex_duration = re.compile(r'\d+$')

    with open(filepath, 'r') as f:
        for line in f:
            ip = get_value_by_regex(regex_ip, line)
            date = get_value_by_regex(regex_date, line)
            method = get_value_by_regex(regex_method, line)
            url = get_value_by_regex(regex_url, line)
            duration = get_value_by_regex(regex_duration, line)

            if ips.get(ip) is None:
                ips[ip] = 1
            else:
                ips[ip] += 1

            methods[method] += 1

            res_list.append({'ip': ip,
                             'datetime': date,
                             'method': method,
                             'url': url,
                             'duration': int(duration)})

        res = sorted(res_list, key=lambda x: x['duration'], reverse=True)
        ips = sorted(ips.items(), key=lambda x: x[1], reverse=True)

        return res, methods, ips


def create_report(results, methods, ips, filename):
    report = dict()
    report['top_ips'] = dict(ips[:3])
    report['top_longest'] = results[:3]
    report['total_stat'] = methods
    report['total_requests'] = len(results)

    with open(f'result_{filename}.json', 'w') as f:
        f.write(json.dumps(report, indent=2))


if path.isfile(args.path):
    filepath = path.join(path.dirname(__file__), args.path)
    parse_res = parse_file(filepath)
    create_report(*parse_res, filename=args.path)
elif path.isdir(args.path):
    files = listdir(args.path)
    for file in files:
        filepath = path.join(path.dirname(__file__), args.path, file)
        parse_res = parse_file(filepath)
        create_report(*parse_res, filename=file)



