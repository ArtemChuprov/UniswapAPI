from setuptools import setup

setup(
    name="DEX_API",
    version="0.0.1",
    author="Blockers",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Ubuntu",
    ],
    packages=["ClientTools"],
    install_requires=["web3"],
    python_requires=">=3.9",
)
