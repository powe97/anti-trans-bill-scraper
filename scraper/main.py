import asyncio
import aiohttp
import bs4
import requests
from lxml import html
import json

BeautifulSoup = lambda data: bs4.BeautifulSoup(data, features="lxml")
BASE_URL = "https://translegislation.com"


async def get_states():
    global session
    url_list = []
    async with session.get(BASE_URL) as data:
        soup = BeautifulSoup(await data.text())
        url_list = [
            link["href"] for link in soup.find("g", {"class": "outlines"}).findAll("a")
        ]
        return url_list


async def scrape_state(url):
    global session
    async with session.get(f"{BASE_URL}{url}") as data:
        soup = BeautifulSoup(await data.text())
        body = soup.find("div", {"class": "css-13pzbwb"})
        return {
            entry.find("a").get_text(): {
                "status": entry.find("span").get_text(),
                "title": entry.find("p").get_text(),
                "description": entry.findAll("p")[1].get_text(),
                "url": entry.find("a")["href"],
            }
            for entry in body.findAll("div", {"class": "css-8wmofp"})
        }


async def main():
    global session
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=5)
    ) as session:
        bills = {
            state.split("/")[-1]: await scrape_state(state)
            for state in await get_states()
        }
        with open(f"bills.json", "w") as bills_json:
            json.dump(bills, bills_json, sort_keys=True, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
