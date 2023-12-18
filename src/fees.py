import requests
import json


class Fees:
    max_fees: int
    medium_fees: int
    low_fees: int
    no_priority: int

    def __init__(self):
        
        response = requests.get('https://mempool.space/api/v1/fees/recommended')
        fees = json.loads(response.content)

        self.max_fees = fees['fastestFee']
        self.medium_fees = fees['halfHourFee']
        self.low_fees = fees['hourFee']

        self.no_priority = fees['minimumFee']

    def update(self):
        self = Fees()

    def get_max_fees(self) -> int :
        return self.max_fees


