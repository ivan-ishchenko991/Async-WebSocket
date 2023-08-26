import platform
import logging
import aiohttp
import asyncio
import sys
import json
from datetime import datetime, timedelta


class PrivatBankAPI:
    BASE_URL = str('https://api.privatbank.ua/p24api/exchange_rates?json&date=')

async def fetch_exchange_rates(url):

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                logging.error(f"Error status: {response.status} for {url}")
                return None

        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None
        
async def get_rates_for_dates(api, dates):
    tasks = [fetch_exchange_rates(f"{api.BASE_URL}{date}") for date in dates]
    return await asyncio.gather(*tasks)
        
def get_days_range(days, today):
    date_lst = list()
    str_date_now = today.strftime("%d.%m.%Y")
    diff = timedelta(days=1)
    date_lst.append(str_date_now)
    for _ in range(days-1):
        today -= diff
        # date = date.strftime("%d.%m.%Y")
        date_lst.append(today.strftime("%d.%m.%Y"))
    return date_lst

def format_currency_data(data):
    formatted_data = []
    for rates in data:
        formatted_rates = {}
        for rate in rates['exchangeRate']:
            if rate['currency'] in ('EUR', 'USD'):
                formatted_rates[rate['currency']] = {
                    'sale': rate['saleRate'],
                    'purchase': rate['purchaseRate']
                }
        formatted_data.append({rates['date']: formatted_rates})
    return formatted_data


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    api = PrivatBankAPI()

    if len(sys.argv) != 2:
        print("Usage: py .\\main.py <number of days>")
    try:
        days = int(sys.argv[1])
        if days > 10:
            print("Maximum number of days allowed is 10.")
    except ValueError:
        print("Invalid number of days.")
    
    date_now = datetime.today()
    date_now = date_now.date()
    dates = get_days_range(days, date_now)
    currency_data = asyncio.run(get_rates_for_dates(api, dates))
    formatted_data = format_currency_data(currency_data)
    print(json.dumps(formatted_data, indent=2))
