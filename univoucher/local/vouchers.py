import requests
from random import randint
from math import inf as infinity
from .. import models

MAX_NONCE = 99999999999999999999999999999999999999999999999

def update(voucher:models.Voucher, json:dict):
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

class Client(models.Client):
    netloc:str
    username:str
    password:str
    verify:bool = True
    ssl:bool = True

    _cookie = None

    def __init__(self, netloc:str, username:str, password:str):
        self.netloc = netloc
        self.username = username
        self.password = password

    @property
    def _headers(self):
        if self._cookie is None:
            return dict()
        else:
            return {"Cookie":self._cookie}
    
    @property
    def _scheme(self):
        return "https" if self.ssl else "http"

    @property
    def _site(self):
        return "default"

    def _login(self):
        url = f"{self._scheme}://{self.netloc}/api/self/sites"

        # 401 Not logged in
        # 200 Logged in

        response = requests.get(url=url, headers=self._headers, verify=self.verify)
        status=response.status_code

        if status != 200:
            payload = {
                "username":self.username,
                "password":self.password,
                "for_hotspot":True,
                "site_name":self._site
            }

            url = f"{self._scheme}://{self.netloc}/api/login"

            response = requests.post(url=url, json=payload, verify=self.verify)
            status = response.status_code
            
            if status != 200: 
                raise LoginException(response)

            self._cookie = response.headers.get("Set-Cookie")

    def fetch(self, amount:int, duration:int, uses:int):
        self._login()

        note = f"Univoucher.{str(randint(0, MAX_NONCE))}"

        payload = {
            "cmd":"create-voucher",
            "expire":int(duration),
            "n":int(amount),
            "quota":(0 if uses == infinity else int(uses)),
            "note":note
        }

        url = f"{self._scheme}://{self.netloc}/api/s/{self._site}/cmd/hotspot"
        response = requests.post(url=url, json=payload, headers=self._headers, verify=self.verify)
        status = response.status_code

        if status != 200:
            raise CreateException(response)
        
        data = response.json().get("data")

        if not data: return None # ???

        time_created = data[0]["create_time"]

        url = f"{self._scheme}://{self.netloc}/api/s/{self._site}/stat/voucher"

        payload = {"create_time":time_created}
        response = requests.get(url=url, json=payload, headers=self._headers, verify=self.verify)
        
        status=response.status_code

        if status != 200: 
            raise RetrieveException(response)

        all_vouchers_raw = response.json().get("data")

        for raw_voucher in all_vouchers_raw:
            voucher:models.Voucher = models.Voucher()
            update(voucher, raw_voucher)

            if voucher.note == note:
                yield voucher