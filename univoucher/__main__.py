from argparse import ArgumentParser, ArgumentTypeError
from .vouchers import Voucher, create
from getpass import getpass
from json import dump
from os import path
import sys
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

def uses(uses:str):
    uses = uses.lower()

    if uses in ("infinity", "inf", "unlimited"):
        return math.inf
    else:
        return int(uses)

#####################################

parser = ArgumentParser()

parser.add_argument("host")

parser.add_argument("--port", type=int, default=8443)

parser.add_argument("--duration", type=format_duration, default="1000")

parser.add_argument("--amount", type=int, default=1)
parser.add_argument("--uses", type=uses, default=1)

parser.add_argument("--username")

parser.add_argument("--no-verify-ssl", action="store_true", default=False)

parser.add_argument("--output")

parser.add_argument("--type", type=str.lower, default="json", choices=writers.keys())

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
    uses=args.uses
)

write:callable = writers.get(args.type)

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