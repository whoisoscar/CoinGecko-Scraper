import time
import requests
from bs4 import BeautifulSoup
import json
from discord_webhook import DiscordWebhook, DiscordEmbed


#Load settings from file
with open("settings.json", "r") as settings_file:
    loaded_json = json.loads(settings_file.read())
    discord_webhook_url = loaded_json["discordWebhook"]
    min_price_change = loaded_json["minPriceChange"]
    max_price_change = loaded_json["maxPriceChange"]
    min_mrkt_cap = loaded_json["minMarketCap"]
    max_mrkt_cap = loaded_json["maxMarketCap"]
    coins_per_cat = loaded_json["coinsPerCategory"]
    exchanges = loaded_json["exchanges"]
    trade_currency = loaded_json["tradeCurrency"]

    if min_price_change == "na":
        min_price_change = 0
    
    if max_price_change == "na":
        max_price_change = 9999999

    if min_mrkt_cap == "na":
        min_mrkt_cap = 0
    
    if max_mrkt_cap == "na":
        max_mrkt_cap = 9999999999999


found_coins = []
searched_coins = []

def coin_specifics(url, category_url, category_name, price_change_24, price_change_7, cat_mrkt_cap, market_cap, global_rank, cat_rank):
    
    #Get coin url for api symbol and extra info
    r = s.get(url)

    parsed_html = BeautifulSoup(r.text, "lxml")
    api_symbol = parsed_html.body.find("div", attrs={"class":"tradingview-widget-container"})["data-coin-api-symbol"]

    #Get API for listed excahnges info
    headers = {'accept': 'application/json'}
    r = s.get(f"https://api.coingecko.com/api/v3/coins/{api_symbol}?tickers=true&market_data=false&community_data=false&developer_data=false&sparkline=false", headers=headers)
    parsed_api_response = json.loads(r.text)    

    #Filter by exchange
    found_exchange_status = False
    found_exchange = []
    for result in parsed_api_response['tickers']:
        for exchange in exchanges:
            if exchange == result['market']['identifier']:
                if trade_currency == result['target']:
                    found_exchange_status = True
                    found_exchange.append(exchange)

    if not found_exchange_status:
        return

    #Get all aditional info for webhook 
    coin_img = parsed_html.body.find("img", attrs={"class":"tw-rounded-full"})["src"]
    try:
        coin_title = parsed_html.body.find("h1", attrs={"class":"mr-md-3"}).text.strip()
    except:
        coin_title = parsed_html.body.find("div", attrs={"class":"mr-md-3"}).text.strip()
    
    coin_price = parsed_html.body.find_all("span", attrs={"data-target":"price.price"})[2].text
    coin_price_details = parsed_html.body.find("table", attrs={"class":"table b-b"}).find_all("td")

    coin_price = coin_price_details[0].text.replace("\n","")

    if len(coin_price_details) == 10:
        all_time_high = coin_price_details[8].text.replace("\n\n","")
    elif len(coin_price_details) == 11:
        all_time_high = coin_price_details[9].text.replace("\n\n","")
    else:
        all_time_high = "N/A, check code"
    
    categories = parsed_html.body.find("div", attrs={"data-controller":"category-tags"}).text.replace("Hide\n","").replace("Show All\n","").strip().replace("\n\n\n\n\n\n","\n")
    
    ticker = coin_title[coin_title.find("(")+1:-1]

    link_found_exchange = found_exchange[0]
    if link_found_exchange == "crypto_com":
        try:
            link_found_exchange = found_exchange[1]
        except:
            link_found_exchange = ""

    description = f"[CoinGecko: {coin_title}]({url})\n[Tradingview: {ticker}/USDT](https://www.tradingview.com/chart/?symbol={link_found_exchange.upper()}%3A{ticker}USDT)\n[Category: {category_name}]({category_url})"
    
    mrkt_cap_dominance = str(round(float(market_cap.replace("\n","").replace("$","").replace(",",""))/float(cat_mrkt_cap)*100,2))+"%"

    #Store found coins for sorting before sending
    found_coins.append(
        {
            "img":coin_img,
            "description":description,
            "tags":categories,
            "mrktCap":market_cap,
            "mrktCapDominance":mrkt_cap_dominance,
            "exchange":found_exchange,
            "globalRank":global_rank,
            "ath":all_time_high,
            "ppc":coin_price,
            "24h":price_change_24,
            "7d":price_change_7
        }
    )

def send_all_coins(found_coins):
    #Sort found coins based on their global rank
    found_coins = sorted(found_coins, key=lambda d: d['globalRank']) 
    for coin in found_coins:
        webhook = DiscordWebhook(url=discord_webhook_url)
        embed = DiscordEmbed(title="New coin found!",description=coin["description"],color=6533573)
        embed.set_thumbnail(url=coin["img"])
        
        embed.add_embed_field(name='Tags',value=coin["tags"],inline=True)
        embed.add_embed_field(name='Mrkt Cap',value=coin["mrktCap"],inline=True)
        embed.add_embed_field(name='Category Mrkt Cap Dominance',value=str(coin["mrktCapDominance"]),inline=True)
        embed.add_embed_field(name='Exchange',value=str(list(set(coin["exchange"]))),inline=True)
        embed.add_embed_field(name='Global rank',value=str(coin["globalRank"]),inline=True)
        #embed.add_embed_field(name='Category rank',value=str(coin["catRank"]+1),inline=True)
        embed.add_embed_field(name='ATH',value=coin["ath"],inline=True)
        embed.add_embed_field(name='PPC',value=coin["ppc"],inline=True)
        embed.add_embed_field(name='24h',value=f'{round(coin["24h"],2)}%',inline=True)
        embed.add_embed_field(name='7d',value=f'{round(coin["7d"],2)}%',inline=True)
        
        embed.set_footer(text='CoinGecko Scraper by whoisoscar',icon_url='https://avatars.githubusercontent.com/u/39652888?v=4')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
        time.sleep(0.5)


with requests.Session() as s:
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36'
    }
    r = s.get("https://www.coingecko.com/en/categories", headers=headers)

    parsed_html = BeautifulSoup(r.text, "lxml")
    
    #Check how many tables in HTML - some have additional info and have 3 tables; we want the last one always
    if len(parsed_html.body.find_all("tbody")) == 1:
        table_rows = parsed_html.body.find("tbody").find_all("tr")
    elif len(parsed_html.body.find_all("tbody")) == 3:
        table_rows = parsed_html.body.find_all("tbody")[2].find_all("tr")

    #Loop through all categories
    for cat_row in table_rows:
        cat_name = cat_row.find("td", attrs={'class':'coin-name'})['data-sort']
        cat_mrkt_cap = cat_row.find_all("td", attrs={"class":"coin-name"})[5]['data-sort']
        cat_url = f'https://www.coingecko.com{cat_row.find("td", attrs={"class":"coin-name"}).find("a")["href"]}'

        #Get each category page
        print(f'Getting cat: {cat_name}')
        r = s.get(cat_url)

        parsed_html = BeautifulSoup(r.text, "lxml")

        
        #Check if category has coins - some newly created categories will be empty or return a 404 page
        try:
            table_rows = parsed_html.body.find("tbody").find_all("tr")
        except:
            continue
        
        #Loop through desired ammount of coins per category - coinsPerCategory settings
        for i in range(coins_per_cat):
            try:
                row = table_rows[i]
            except:
                break
                #Catch error if coins in category < desired coinsPerCategory
            
            coin_url = f'https://www.coingecko.com{row.find("td", attrs={"class":"coin-name"}).find("a")["href"]}'
            if coin_url in searched_coins:
                #Skip already searched coins
                continue        

            searched_coins.append(coin_url)
            #Get details for 2 different page formats
            try:
                market_cap = row.find_all("td", attrs={'class':'td-market_cap'})[0].text
                price_change_24 = float(row.find("td", attrs={'class':'td-change24h'})['data-sort'])
                price_change_7 = float(row.find("td", attrs={'class':'td-change7d'})['data-sort'])
            except:
                try:
                    price_change_24 = float(row.find_all("td", attrs={'class':'stat-percent'})[1].text.replace("%",""))
                    price_change_7 = float(row.find_all("td", attrs={'class':'stat-percent'})[2].text.replace("%",""))
                except:
                    #Skp coins that don't have price changes (stablecoins)
                    continue
            
            if market_cap == "\n?\n":
                #Skip coins with unknown market cap
                continue
            
            try:
                global_rank = int(row.find("td", attrs={'class':'table-number'}).text)
            except:
                #If coin has no rank, assign large value for sorting
                global_rank = 99999
            
            stripped_market_cap = float(market_cap.replace("\n","").replace("$","").replace(",",""))
            #Apply configurations
            if price_change_24 >= min_price_change and price_change_24 <= max_price_change and stripped_market_cap >= min_mrkt_cap and stripped_market_cap <= max_mrkt_cap:
                coin_specifics(coin_url, cat_url, cat_name, price_change_24, price_change_7, cat_mrkt_cap, market_cap, global_rank, i)


    send_all_coins(found_coins)


webhook = DiscordWebhook(url=discord_webhook_url)
embed = DiscordEmbed(title="CoinGecko Scraper Log",color=6533573)

embed.add_embed_field(name='Coins Found',value=str(len(found_coins)),inline=True)
embed.add_embed_field(name='Min Price Change',value=f'{min_price_change}%',inline=True)
embed.add_embed_field(name='Min MrktCap',value=f'${"{:,}".format(min_mrkt_cap)}',inline=True)
embed.add_embed_field(name='Exchange Search',value=str(exchanges),inline=True)
embed.add_embed_field(name='Trade Pair Search',value=trade_currency,inline=True)

embed.set_footer(text='CoinGecko Scraper by whoisoscar',icon_url='https://avatars.githubusercontent.com/u/39652888?v=4')
embed.set_timestamp()
webhook.add_embed(embed)
webhook.execute()