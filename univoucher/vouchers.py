import requests
from random import randint
from urllib.parse import urlunparse as geturl, quote as urlquote
from math import inf as infinity
from .models import Voucher

MAX_NONCE = 99999999999999999999999999999999999999999999999

def update(voucher, json:dict):
    voucher.identifier = json.get("_id")
    voucher.site = json.get("site_id")
    voucher.admin = json.get("admin_name")
    voucher.code = json.get("code")
    voucher.created = json.get("create_time")
    voucher.duration = json.get("duration")
    voucher.hotspot = json.get("for_hotspot")
    voucher.note = json.get("note")
    voucher.uses = json.get("quota")

class LocalException(Exception):
    response:requests.models.Response

    def __init__(self, response:requests.models.Response):
        self.response = response

class CreateException(LocalException): ...
class LoginException(LocalException): ...
class RetrieveException(LocalException): ...

def create(host:str, port:int, username:str, password:str, verify:bool, duration:int, amount:int, uses:int):
    if uses == infinity: uses = 0

    site:str="default"

    netloc = f"{urlquote(host, safe='')}:{int(port)}"

    # 401 Not logged in
    # 200 Logged in

    payload = {
        "username":username,
        "password":password,
        "for_hotspot":True,
        "site_name":site
    }

    url = geturl(("https", netloc, "/api/login", "", "", ""))

    response = requests.post(url=url, json=payload, verify=verify)

    status = response.status_code

    if status == 401: 
        raise LoginException(response)

    cookie = response.headers.get("Set-Cookie")
    headers = {"Cookie":cookie}

    note = str(randint(0, MAX_NONCE))

    payload = {
        "cmd":"create-voucher",
        "expire":duration,
        "n":amount,
        "quota":uses,
        "note":note
    }
    url = geturl(("https", netloc, f"/api/s/{site}/cmd/hotspot", "", "", ""))
    response = requests.post(url=url, json=payload, headers=headers, verify=verify)
    
    status = response.status_code

    if status != 200: 
        raise CreateException(response)
    
    data = response.json().get("data")

    if not data: return None # ???

    time_created = data[0]["create_time"]

    url = geturl(("https", netloc, f"/api/s/{site}/stat/voucher", "", "", ""))

    payload = {"create_time":time_created}
    response = requests.get(url=url, json=payload, headers=headers, verify=verify)
    
    status=response.status_code

    if status != 200: 
        raise RetrieveException(response)

    all_vouchers_raw = response.json().get("data")

    for raw_voucher in all_vouchers_raw:
        voucher:Voucher = Voucher()
        update(voucher, raw_voucher)
        
        yield voucher