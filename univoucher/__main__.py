from argparse import ArgumentParser
from .vouchers import create
from .models import Voucher
from getpass import getpass
from json import dump
from os import path
from itertools import islice
from typing import Callable
import math

ERR_OUTPUT_IS_DIR = {
    "code":10,
    "message":"The specified output path is a directory"
}

def write_json(vouchers:list, output):
    dump(obj=list(map(vars, vouchers)), fp=output, indent=4, sort_keys=True)

def write_csv(vouchers:list, output):
    import csv

    writer = csv.writer(output)

    writer.writerow([
        "identifier",
        "site",
        "admin",
        "code",
        "created",
        "duration",
        "hotspot",
        "note",
        "uses"
    ]) # Write the column names

    voucher:Voucher
    for voucher in vouchers:
        writer.writerow([
            voucher.identifier,
            voucher.site,
            voucher.admin,
            voucher.code,
            voucher.created,
            voucher.duration,
            voucher.hotspot,
            voucher.note,
            voucher.uses
        ])

writers = {
    "json": write_json,
    "csv": write_csv
}

def format_duration(duration:str) -> int:
    return int(duration) # TODO

class FunctionChain:
    function:Callable
    __returned = []

    def __init__(self, function:Callable):
        self.function = function
    
    def __call__(self, *args, **kwargs):
        self.__returned.append(self.function(*args, **kwargs))
        return self
    
    def __iter__(self):
        return islice(self.__returned, 0, len(self.__returned)-1)

#####################################

parser = ArgumentParser()

FunctionChain(parser.add_argument) \
    ("host") \
    ("--port", type=int, default=8443) \
    ("--duration", type=format_duration, default="1000", help="duration in minutes") \
    ("--amount", type=int, default=1) \
    ("--uses", type=int, default=1) \
    ("--unlimited", action="store_true", default=False) \
    ("--username") \
    ("--no-verify-ssl", action="store_true", default=False) \
    ("--output") \
    ("--output-type", type=str.lower, default="json", choices=writers.keys())

#####################################

args = parser.parse_args()

if not args.username:
    args.username = input("Username: ")

password = getpass(prompt="Password: ")

vouchers = create(
    host=args.host, 
    port=args.port, 
    username=args.username, 
    password=password, 
    verify=not args.no_verify_ssl, 
    duration=args.duration, 
    amount=args.amount, 
    uses=(math.inf if args.unlimited else args.uses)
)

write:callable = writers.get(args.output_type)

#####################################

if args.output:
    if path.isdir(args.output):
        print(ERR_OUTPUT_IS_DIR["message"], file=sys.stderr)
        exit(ERR_OUTPUT_IS_DIR["code"])
    
    with open(args.output, "w", newline='') as stream:
        write(vouchers=vouchers, output=stream)
else:
    import sys
    write(vouchers=vouchers, output=sys.stdout)