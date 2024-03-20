from numpy.core.multiarray import array as array
from web3 import Web3
from abc import ABC, abstractmethod
import numpy as np
from .configs import POOL_ABI, POOL_ADDRESS
from web3 import Web3
from .tools import convert_swap_event_data, find_blocks_in_time_range
from datetime import datetime, timedelta
import pandas as pd

POOL_KEYS = {"eth_usd": "2f1c7a49727a459fa525610c8a03856d"}


class SimpleClient(ABC):
    def __init__(self, client_api_key: str):
        self.client_api_key = client_api_key
        self.web3 = Web3(
            Web3.HTTPProvider("https://mainnet.infura.io/v3/" + client_api_key)
        )

    # @abstractmethod
    # def provide_liquidity(
    #     self, symbol_1: str, symbol_2: str, amount_1: float, amount_2: float
    # ):
    #     pass

    @abstractmethod
    def get_trades(self) -> np.array:
        pass

    @abstractmethod
    def create_candles(self):
        pass

    # @abstractmethod
    # def get_contract_address(self, symbol_1: str, symbol_2: str) -> str:
    #     pass

    # @abstractmethod
    # def get_balances(self) -> dict:
    #     pass


class UniswapClient(SimpleClient):
    def get_trades(
        self,
        symbol_1: str,
        symbol_2: str,
        from_datetime: datetime,
        to_datetime: datetime,
    ) -> np.array:
        pair_name = symbol_1.lower() + "_" + symbol_2.lower()
        address = POOL_ADDRESS[pair_name]
        pool_contract = self.web3.eth.contract(
            address=Web3.to_checksum_address(address), abi=POOL_ABI
        )
        # Find start and end blocks for the given time range
        start_block, end_block = find_blocks_in_time_range(
            self.web3, from_datetime, to_datetime
        )

        # Fetch Swap events within the block range
        swap_events_filter = pool_contract.events.Swap.create_filter(
            fromBlock=start_block, toBlock=end_block
        )
        swap_events = swap_events_filter.get_all_entries()

        # Decode and convert each swap event
        trades = [convert_swap_event_data(event) for event in swap_events]
        # trades = [event for event in swap_events]

        return trades

    def create_candles(
        self,
        symbol_1: str,
        symbol_2: str,
        from_datetime: datetime,
        to_datetime: datetime,
    ):
        trades = self.get_trades(symbol_1, symbol_2, from_datetime, to_datetime)

        df = pd.DataFrame(trades)[["amount0", "amount1", "block_number"]].abs()
        df["price"] = df["amount0"] / df["amount1"]
        df["volume"] = df["amount1"].copy()

        df = df.drop(columns=["amount0", "amount1"])

        df["block_number"].nunique()

        ohlcv = df.groupby("block_number").agg(
            {"price": ["first", "max", "min", "last"], "volume": "sum"}
        )

        ohlcv.columns = ["open", "high", "low", "close", "volume"]
        return ohlcv
