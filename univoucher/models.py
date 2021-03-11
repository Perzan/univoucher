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

from typing import Iterable
class Client:
    def __init__(self):
        raise NotImplementedError()

    def fetch(self, amount:int, duration:int, uses:int) -> Iterable[Voucher]:
        raise NotImplementedError()