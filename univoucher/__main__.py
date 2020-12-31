from argparse import ArgumentParser, ArgumentTypeError
from .storage import VoucherManager, Response
from getpass import getpass
from json import dump
from os import path
import sys

ERR_OUTPUT_IS_DIR = {
    "code":10,
    "message":"The specified output path is a directory"
}

def vouchers_to_json(vouchers:list):
    return [voucher.dictify() for voucher in vouchers]

def write_json(vouchers:list, output):
    dump(obj=vouchers_to_json(vouchers), fp=output, indent=4, sort_keys=True)

writers = {
    "json": write_json
}

def format_duration(duration:str) -> int:
    return int(duration) # TODO

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')

#####################################

parser = ArgumentParser()

parser.add_argument("host")
parser.add_argument("duration", type=format_duration)

parser.add_argument("--amount", type=int, default=1)
parser.add_argument("--uses", type=int, default=1)

parser.add_argument("--username")

parser.add_argument("--verify-ssl", type=str2bool, default=True)

parser.add_argument("--output")

parser.add_argument("--type", type=str.lower, default="json", choices=writers.keys())

#####################################

args = parser.parse_args()

if not args.username:
    args.username = input("Username: ")

password = getpass(prompt="Password: ")

vman = VoucherManager(host=args.host, username=args.username, password=password, verify=args.verify_ssl)
response:Response = vman.create(duration=args.duration, amount=args.amount, uses=args.uses)

write:callable = writers.get(args.type)

#####################################

if args.output:
    if path.isdir(args.output):
        print(ERR_OUTPUT_IS_DIR["message"], file=sys.stderr)
        exit(ERR_OUTPUT_IS_DIR["code"])
    
    with open(args.output, "w") as stream:
        write(vouchers=response.content, output=stream)
else:
    import sys
    write(vouchers=response.content, output=sys.stdout)