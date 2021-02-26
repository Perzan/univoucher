from univoucher import models, local
from getpass import getpass
import math

client:models.Client = local.Client(input("Netloc: "), input("Username: "), getpass("Password: "))
client.verify = False

vouchers = client(2, 3, math.inf)

for voucher in vouchers:
    print(voucher.code)