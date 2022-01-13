import requests
import json

def get_exchange_list():

    api_symbol = "ethereum"

    exchange_list = ""
    found_exchange = []
    with requests.Session() as s:
        headers = {
            'accept': 'application/json'
        }
        r = s.get(f"https://api.coingecko.com/api/v3/coins/{api_symbol}?tickers=true&market_data=false&community_data=false&developer_data=false&sparkline=false", headers=headers)
        parsed_api_response = json.loads(r.text)
            
        for result in parsed_api_response['tickers']:
                if result['market']['identifier'] not in found_exchange:
                    found_exchange.append(result['market']['identifier'])
                    exchange_list += result['market']['identifier']+"\n"
        
        with open("exchnages.txt", "w") as outfile:
            outfile.write(exchange_list)

def get_page_status():
    with requests.Session() as s:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36'
        }
        r = s.get("https://www.coingecko.com/en/categories", headers=headers)

        print(r.status_code)
        with open("out.html", "w") as outfile:
            outfile.write(r.text)