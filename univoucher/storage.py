import requests
from random import randint

MAX_NONCE = 99999999999999999999999999999999999999999999999

class Voucher:
    identifier:str
    site:str
    admin:str
    code:str
    created:int
    duration:int
    hotspot:bool
    note:str
    uses:int

    def dictify(self):
        return {
            "identifier":self.identifier,
            "site":self.site,
            "admin":self.admin,
            "code":self.code,
            "created":self.created,
            "duration":self.duration,
            "hotspot":self.hotspot,
            "note":self.note,
            "uses":self.uses
        }

def update(voucher:Voucher, json:dict):
    voucher.identifier = json.get("_id")
    voucher.site = json.get("site_id")
    voucher.admin = json.get("admin_name")
    voucher.code = json.get("code")
    voucher.created = json.get("create_time")
    voucher.duration = json.get("duration")
    voucher.hotspot = json.get("for_hotspot")
    voucher.note = json.get("note")
    voucher.uses = json.get("quota")

class Response:
    status:int
    content:object

    def __init__(self, status:int, content:object=None):
        self.status = status
        self.content = content

class VoucherManager:
    cookie:str=""
    site:str="default"

    def __init__(self, host:str, username:str, password:str, verify:bool=True):
        self.host = host
        self.username = username
        self.password = password
        self.verify = verify
    
    @property
    def headers(self):
        if self.cookie:
            return {"Cookie":self.cookie}
        else:
            return {}
        
    def login(self):
        url = f"https://{self.host}/api/self/sites"

        # 401 Not logged in
        # 200 Logged in

        response = requests.get(url=url, headers=self.headers, verify=self.verify)

        vresponse = Response(status=response.status_code)

        if vresponse.status != 200:
            payload = {
                "username":self.username,
                "password":self.password,
                "for_hotspot":True,
                "site_name":self.site
            }

            url = f"https://{self.host}/api/login"

            response = requests.post(url=url, json=payload, verify=self.verify)

            self.cookie = response.headers.get("Set-Cookie")

        return vresponse


    def create(self, duration:int, amount:int=1, uses:int=1):
        self.login()

        note = str(randint(0, MAX_NONCE))

        payload = {
            "cmd":"create-voucher",
            "expire":duration,
            "n":amount,
            "quota":uses,
            "note":note
        }

        url = f"https://{self.host}/api/s/{self.site}/cmd/hotspot"

        response = requests.post(url=url, json=payload, headers=self.headers, verify=self.verify)
        
        vresponse = Response(status=response.status_code)

        if vresponse.status == 200:
            data = response.json().get("data")

            if not data:
                return None

            created = data[0]["create_time"]

            vresponse.content = list(filter(lambda voucher: voucher.note == note, self.get(created).content))
        
        return vresponse
    
    def get(self, created:int=None):
        self.login()

        url = f"https://{self.host}/api/s/{self.site}/stat/voucher"

        payload = {}

        if created:
            payload["create_time"] = created

        response = requests.get(url=url, json=payload, headers=self.headers, verify=self.verify)
        
        vresponse = Response(status=response.status_code)

        if vresponse.status == 200:
            all_vouchers_raw = response.json().get("data")
            vouchers = list()

            for raw_voucher in all_vouchers_raw:
                voucher:Voucher = Voucher()
                update(voucher, raw_voucher)
                vouchers.append(voucher)
            
            vresponse.content = vouchers
        
        return vresponse
    
    def delete(self, identifier:int):
        self.login()

        url = f"https://{self.host}/api/s/{self.site}/cmd/hotspot"

        payload = {
            "_id":identifier,
            "cmd":"delete-voucher"
        }

        response = requests.post(url=url, json=payload, headers=self.headers, verify=self.verify)

        return Response(status=response.status_code)