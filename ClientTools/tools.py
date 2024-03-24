from web3 import Web3
import json
from datetime import datetime
import math


def get_block_by_timestamp(web3, target_timestamp, start_block, end_block):
    """
    Perform a binary search to find the block number closest to the target timestamp.

    Parameters:
    - web3: A Web3 instance connected to an Ethereum node.
    - target_timestamp: The timestamp to search for, as an integer.
    - start_block, end_block: The block range to search within.

    Returns:
    The block number closest to the target timestamp.
    """
    while start_block <= end_block:
        mid_block = (start_block + end_block) // 2
        mid_block_timestamp = web3.eth.get_block(mid_block).timestamp

        if mid_block_timestamp < target_timestamp:
            start_block = mid_block + 1
        elif mid_block_timestamp > target_timestamp:
            end_block = mid_block - 1
        else:
            return mid_block  # Exact match found

    # Closest block (if exact match not found, choose the block closer to the target)
    if abs(web3.eth.get_block(start_block).timestamp - target_timestamp) < abs(
        web3.eth.get_block(end_block).timestamp - target_timestamp
    ):
        return start_block
    else:
        return end_block


def find_blocks_in_time_range(web3, start_time, end_time):
    """
    Find block numbers mined within a specified time range using binary search.

    Parameters:
    - web3: A Web3 instance connected to an Ethereum node.
    - start_time, end_time: The start and end of the time range as datetime objects.

    Returns:
    A tuple containing the start and end block numbers corresponding to the time range.
    """
    # Convert datetime objects to timestamps
    start_timestamp = int(start_time.timestamp())
    end_timestamp = int(end_time.timestamp())

    # Define the initial search range
    latest_block = web3.eth.block_number
    start_block = (
        1  # Assuming block 1 as the start (change based on the chain's context)
    )
    end_block = latest_block

    # Find the start and end blocks for the range
    start_block_number = get_block_by_timestamp(
        web3, start_timestamp, start_block, end_block
    )
    end_block_number = get_block_by_timestamp(
        web3, end_timestamp, start_block_number, end_block
    )

    return (start_block_number, end_block_number)


def convert_swap_event_data(event):
    """
    Convert and decode event data to a more readable format, adjusting for token decimals.

    ETH generally has 18 decimal places.
    USDT (and many stablecoins) have 6 decimal places.

    Parameters:
    - event_args: The 'args' attribute from a swap event log.

    Returns:
    A dictionary containing decoded and converted swap event data.
    """

    event_args = event["args"]
    block_number = event["blockNumber"]
    # Constants for decimals
    ETH_DECIMALS = 18
    USDT_DECIMALS = 6

    # Adjust amounts by their decimal places
    amount0_adjusted = event_args["amount0"] / (10**ETH_DECIMALS)
    amount1_adjusted = event_args["amount1"] / (10**USDT_DECIMALS)

    # Calculate price as per the given formula
    price = (event_args["sqrtPriceX96"] ** 2) / (2**192)

    price = price * (10 ** (ETH_DECIMALS - USDT_DECIMALS))

    return {
        "sender": event_args["sender"],
        "recipient": event_args["recipient"],
        "amountETH": amount0_adjusted,  # ETH amount adjusted
        "amountUSDT": amount1_adjusted,  # USDT amount adjusted
        "price": price,
        "liquidity": event_args["liquidity"],
        "tick": event_args["tick"],
        "block_number": int(block_number),
    }
