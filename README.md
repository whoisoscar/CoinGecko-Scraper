**Background**
--
With over 12 thousand coins listed on CoinGecko in an evergrowing multi-trillion dollar industry, it can be quite hard to track them all. This tool aims to help filter all these coins to find possible gems to add to your portfolio.

![Image](https://i.imgur.com/FnFbakm.png)
**Installation**
--
To install files:
`````
git clone https://github.com/whoisoscar/CoinGecko-Scraper
`````
To Install Required Modules:
`````
pip install -r requirements.txt
`````

**Usage**
--
`````
cd CoinGecko-Scraper
python3 main.py
`````
Configurations are done within the settings.json file.
These configurations include:

* Discord Webhook integration for sending results `discordWebhook`
* Minimum and maximum price change (24h) `minPriceChange` , `maxPriceChange`
    * *Values set as "na" default to 0 and ∞ respectively*
* Minimum and maximum market cap `minMarketCap` , `maxMarketCap`
    * *Values set as "na" default to 0 and ∞ respectively*
* Limit amount of coins per category `coinsPerCategory`
* Supported exchanges (list) `exchanges`
    * *Find correct exchange syntax in exchanges.txt*
* Trade currency `tradeCurrency`

Given the parameters set in the settings file, the script will go through all categories on CoinGecko, then go through the first `coinsPerCategory` coins in the category. For each of the coins, it will apply the parameters in the settings file.

Once successfully ran, it will send the found coins to the discord webhook in ascending market cap order with additional information about the coin such as:
* Tags
* Market cap
* Category market cap dominance
* Listed desired exchanges
* Global rank
* Information about the ATH
* Price per coin
* 24h and 7d % change

Additionally, the script will send a webhook with a summary of what was ran and how many coins were found.

**To-do**
--
- [ ] Replace parts of code with official CoinGecko API for easier readability and stability
- [ ] Add hyperlinks to found exchanges for easier accessability
