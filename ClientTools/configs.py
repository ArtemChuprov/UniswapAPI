import json

POOL_ABI = json.loads(
    """
[
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "name": "sender", "type": "address"},
            {"indexed": true, "name": "recipient", "type": "address"},
            {"indexed": false, "name": "amount0", "type": "int256"},
            {"indexed": false, "name": "amount1", "type": "int256"},
            {"indexed": false, "name": "sqrtPriceX96", "type": "uint160"},
            {"indexed": false, "name": "liquidity", "type": "uint128"},
            {"indexed": false, "name": "tick", "type": "int24"}
        ],
        "name": "Swap",
        "type": "event"
    }
]
"""
)


POOL_ADDRESS = {"eth_usdt": "0x11b815efb8f581194ae79006d24e0d814b7697f6"}
