from numpy.core.multiarray import array as array
from web3 import Web3
from abc import ABC, abstractmethod
import numpy as np
from web3 import Web3
from .tools import convert_swap_event_data, find_blocks_in_time_range
from datetime import datetime, timedelta
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv(".envrc")

POOL_ADDRESS = json.loads(os.environ["POOL_ADDRESS"])
POOL_ABI = json.loads(os.environ["POOL_ABI"])


class SimpleClient(ABC):
    def __init__(self, client_api_key: str):
        self.client_api_key = client_api_key
        self.web3 = Web3(
            Web3.HTTPProvider("https://mainnet.infura.io/v3/" + client_api_key)
        )
        self.account = self.web3.eth.account.privateKeyToAccount(client_api_key)

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
    def get_address(self, symbol_1: str, symbol_2: str = None) -> str:
        pass


class UniswapClient(SimpleClient):
    def provide_liquidity(
        self,
        symbol_1: str,
        symbol_2: str,
        amount_1: float,
        amount_2: float,
        slippage=0.5,
    ):
        """
        Provide liquidity to a Uniswap pool for two ERC-20 tokens.

        Parameters:
        - web3: Instance of Web3 connected to an Ethereum node.
        - account: The account providing liquidity (Web3.py account object).
        - router_contract: The Uniswap Router contract object.
        - token_a_contract, token_b_contract: Contract objects for the two ERC-20 tokens.
        - token_a_address, token_b_address: Addresses of the two ERC-20 tokens.
        - amount_a, amount_b: Amounts of token A and token B to provide as liquidity.
        - slippage: Acceptable slippage percentage.
        """

        contract_address = self.get_address(symbol_1, symbol_2)
        token_1_address = self.get_address(symbol_1)
        token_2_address = self.get_address(symbol_2)

        token_1_contract = self.web3.eth.contract(address=token_1_address, abi=POOL_ABI)
        token_2_contract = self.web3.eth.contract(address=token_2_address, abi=POOL_ABI)
        router_contract = self.web3.eth.contract(address=contract_address, abi=POOL_ABI)

        def approve_token(token_contract, amount):
            approve_tx = token_contract.functions.approve(
                contract_address, amount
            ).buildTransaction(
                {
                    "from": self.account.address,
                    "nonce": self.web3.eth.getTransactionCount(self.client_api_key),
                }
            )
            signed_tx = self.account.signTransaction(approve_tx)
            return self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        # Approve the router to spend tokens
        approve_token(token_1_contract, amount_1)
        approve_token(token_2_contract, amount_2)

        # Calculate minimum amounts based on slippage
        amount_a_min = amount_1 * (1 - slippage / 100)
        amount_b_min = amount_2 * (1 - slippage / 100)
        deadline = (
            self.web3.eth.getBlock("latest")["timestamp"] + 10 * 60
        )  # 10 minutes from now

        # Provide liquidity
        tx = router_contract.functions.addLiquidity(
            token_1_address,
            token_2_address,
            amount_1,
            amount_2,
            amount_a_min,
            amount_b_min,
            self.account.address,
            deadline,
        ).buildTransaction(
            {
                "from": self.account.address,
                "nonce": self.web3.eth.getTransactionCount(self.account.address),
            }
        )

        signed_tx = self.account.signTransaction(tx)
        return self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

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

        # for now candles are built by blocks
        ohlcv = df.groupby("block_number").agg(
            {"price": ["first", "max", "min", "last"], "volume": "sum"}
        )

        ohlcv.columns = ["open", "high", "low", "close", "volume"]
        return ohlcv

    def get_address(self, symbol_1: str, symbol_2: str = None) -> str:
        if symbol_2 is not None:
            return POOL_ADDRESS[symbol_1.lower() + "_" + symbol_2.lower()]
        else:
            return POOL_ADDRESS[symbol_1.lower()]
