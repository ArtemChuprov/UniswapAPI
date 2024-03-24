# Motivation

Current DEX, like Uniswap, provide very advanced interface and big variety of possible actions (trading and liquidity providing). But it's API Python interface is very poor and often doesn't let to perform some of these actions. 

So, we decided to start builging our own API. It has to be useful to build future strategies.

The API interface is built on the Web3 base.

# Code structure

In .envrc file environmental variables are declared. For now it's POOL_ABI form and addresses for contracts to make requests easier.

In ClientTools main code is done. In client.py API interface is built and in tools.py there are just some helping functions.

In test.ipynb example there is an example of code usage.

# Current features

- **provide_liquidity** function provides liquidity: you just have to specify symbols and amounts you want to provide for each one.

- **get_trades function** gets symbols and dates and then returns trades made in this time frame. To achieve this requests to blockhain system is used.

- **create_candles** function builds japaneese candles based on trades made. This is useful mathematical model.

- **get_address** function provides an address to contract or a specific symbol. These addresses will be collected based on https://www.geckoterminal.com/eth/uniswap_v3/pools site. 