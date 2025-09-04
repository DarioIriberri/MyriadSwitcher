MyriadSwitcher
==============

A Myriadcoin Auto-switching mining software

MyriadSwitcher is a python app designed to mine the crypto-currency known as Myriadcoin. Unlike most cryptos out there, Myriadcoin uses 5 different algorithms to mine the coin, namely SHA-256, Scrypt, Groestl, Skein and Qubit.
MyriadSwitcher fetches the web to determine which of the 4 GPU minable algos is the most profitable one (Scrypt, Groestl, Skein or Qubit) and automates the switching of your GPUs to mining the most profitable algo at all times. You can aim for maximum coins per day, maximum coins per watt, or mine in an hybrid mode that's anything in between the aforementioned modes.
It monitors your miners and automatically restarts them if they crash or freeze, and it can also generate an html output log to monitor your mining progress remotely.