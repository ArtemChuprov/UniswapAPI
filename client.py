from web3 import Web3
from abc import ABC, abstractmethod
import numpy as np


class SimpleClient(ABC):
    def __init__(self, net_url: str, client_secret_key: str):
        self.net_url = net_url
        self.client_secret_key = client_secret_key

    @abstractmethod
    def provide_liquidity(
        self, symbol_1: str, symbol_2: str, amount_1: float, amount_2: float
    ):
        pass

    @abstractmethod
    def get_trades(self) -> np.array:
        pass

    @abstractmethod
    def create_candles(self):
        pass

    @abstractmethod
    def get_contract_address(self, symbol_1: str, symbol_2: str) -> str:
        pass

    @abstractmethod
    def get_balances(self) -> dict:
        pass


class UniswapClient(SimpleClient):
    def provide_liquidity(
        self, symbol_1: str, symbol_2: str, amount_1: float, amount_2: float
    ):
        web3 = Web3(
            Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID")
        )
        pair_contract_address = self.get_contract_address(
            symbol_1=symbol_1, symbol_2=symbol_2
        )  # replace with the actual pair contract address
        pair_abi = [...]  # replace with the actual ABI
        pair_contract = web3.eth.contract(address=pair_contract_address, abi=pair_abi)

        # setup your filter
        swap_filter = pair_contract.events.Swap.createFilter(
            fromBlock=0, toBlock="latest"
        )
