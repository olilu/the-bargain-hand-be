from bs4 import BeautifulSoup,SoupStrainer
from typing import List
import requests
import asyncio
import aiohttp
import re

from pydantic_models.wishlist_game import WishlistGameFull
from service.utilities.shop import ShopUtilities

class PlayStationUtilities(ShopUtilities):
    def __init__(self, wishlist_uuid: str, country_code: str, language_code: str):
        super().__init__(wishlist_uuid, country_code, language_code)
        self.base_url = "https://store.playstation.com"
        self.country_language_code = f"{language_code.lower()}-{country_code.lower()}"
        self.search_url = f"{self.base_url}/{self.country_language_code}/search/"
    
    def search(self, query: str) -> List[WishlistGameFull]:
        search_results = self.scrape_playstation_search_results(query)
        return search_results
    
    def get_game_info_by_id(self, game_id: str, img_url: str) -> WishlistGameFull:
        url = f"{self.base_url}/{self.country_language_code}/product/{game_id}"
        return self.scrape_playstation_game_info(url, img_url)
    

    def scrape_playstation_search_results(self, query: str) -> List[WishlistGameFull]:
        r = requests.get(self.search_url+query)
        soup = BeautifulSoup(r.text, 'html.parser', parse_only=SoupStrainer("section","search-results"))
        links = [link["href"] for link in soup.find_all("a", "psw-content-link")]
        img_links = [link["src"] for link in soup.find_all('img', 'psw-top-left psw-l-fit-cover')]
        if len(links) != len(img_links):
            raise ValueError("Number of links and images does not match")
        # for better performance, we only want to scrape the first 10 results
        if len(links) > 10:
            links = links[:10]
            img_links = img_links[:10]
        loop = asyncio.get_event_loop()
        games = loop.run_until_complete(self.scrape_playstation_games_async(links, img_links))
        return games
    
    async def scrape_playstation_games_async(self, links: List[str], img_links: List[str]) -> List[WishlistGameFull]:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for index, link in enumerate(links):
                url = f"{self.base_url}{link}"
                img_url = img_links[index]
                tasks.append(asyncio.ensure_future(self.scrape_playstation_game_info_async(session, url, img_url)))
            games = await asyncio.gather(*tasks)
            return games
        
    async def scrape_playstation_game_info_async(self, session: aiohttp.ClientSession, url: str, img_url: str) -> WishlistGameFull:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser', parse_only=SoupStrainer("main"))
            price_info = soup.select('span[data-qa="mfeCtaMain#offer0#finalPrice"]')[0].decode_contents()
            price_info, price_index = retrieve_price_info(soup)
            currency = price_info[0]
            price_new = price_info[1]
            # if a price could not be found, the on sale flag is set to false
            if currency == "-" and price_new == 0.0:
                on_sale = False
            else:
                # if there is discount info displayed on the target offering, the game is on sale
                on_sale = bool(soup.select(f'span[data-qa="mfeCtaMain#offer{price_index}#discountInfo"]'))
            if on_sale:
                # as there are some further spans in the inner HTML, we need to split and get the last element
                price_old = soup.select(f'span[data-qa="mfeCtaMain#offer{price_index}#originalPrice"]')[0].decode_contents().split(" ")[-1]
            else:
                price_old = price_new
            
            ps_game = WishlistGameFull(
                wishlist_uuid=self.wishlist_uuid,
                game_id=url.split("/")[-1],
                name=soup.select('h1[data-qa="mfe-game-title#name"]')[0].decode_contents(),
                shop="PlayStation",
                link=url,
                img_link=img_url,
                price_new=price_new,
                price_old=price_old,
                on_sale=on_sale,
                currency=currency
            )
            return ps_game

    def scrape_playstation_game_info(self, url: str, img_url: str) -> WishlistGameFull:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser', parse_only=SoupStrainer("main"))
        price_info = soup.select('span[data-qa="mfeCtaMain#offer0#finalPrice"]')[0].decode_contents()
        price_info, price_index = retrieve_price_info(soup)
        currency = price_info[0]
        price_new = price_info[1]
        # if a price could not be found, the on sale flag is set to false
        if currency == "-" and price_new == 0.0:
            on_sale = False
        else:
            # if there is discount info displayed on the target offering, the game is on sale
            on_sale = bool(soup.select(f'span[data-qa="mfeCtaMain#offer{price_index}#discountInfo"]'))
        if on_sale:
            # as there are some further spans in the inner HTML, we need to split and get the last element
            price_old = soup.select(f'span[data-qa="mfeCtaMain#offer{price_index}#originalPrice"]')[0].decode_contents().split(" ")[-1]
        else:
            price_old = price_new
        
        ps_game = WishlistGameFull(
            wishlist_uuid=self.wishlist_uuid,
            game_id=url.split("/")[-1],
            name=soup.select('h1[data-qa="mfe-game-title#name"]')[0].decode_contents(),
            shop="PlayStation",
            link=url,
            img_link=img_url,
            price_new=price_new,
            price_old=price_old,
            on_sale=on_sale,
            currency=currency
        )
        return ps_game
        
    #def scrape_playstation_search_results_sync(self, query: str) -> List[WishlistGameFull]:
    #    r = requests.get(self.search_url+query)
    #    soup = BeautifulSoup(r.text, 'html.parser', parse_only=SoupStrainer("section","search-results"))
    #    links = [link["href"] for link in soup.find_all("a", "psw-content-link")]
    #    img_links = [link["src"] for link in soup.find_all('img', 'psw-top-left psw-l-fit-cover')]
    #    if len(links) != len(img_links):
    #        raise ValueError("Number of links and images does not match")
    #    # for better performance, we only want to scrape the first 10 results
    #    if len(links) > 10:
    #        links = links[:10]
    #        img_links = img_links[:10]
    #    games = []
    #    for index, link in enumerate(links):
    #        print("working on:", link)
    #        url = f"{self.base_url}{link}"
    #        img_url = img_links[index]
    #        game = self.scrape_playstation_game_info(url, img_url)
    #        games.append(game)
    #    return games
    
def retrieve_price_info(soup: BeautifulSoup) -> (tuple, int):
    i = 0
    price_info = soup.select(f'span[data-qa="mfeCtaMain#offer{i}#finalPrice"]')[0].decode_contents()
    # check if the price info contains a currency and a price
    match = re.search(r'([\D]+)([\d.]+)', price_info.replace(" ",""))
    # if not, check the next price info (sometimes there are free test versions available without price info)
    while not match or i == 5:
        i += 1
        try:
            price_info = soup.select(f'span[data-qa="mfeCtaMain#offer{i}#finalPrice"]')[0].decode_contents()
            match = re.search(r'([\D]+)([\d.]+)', price_info.replace(" ",""))
        except IndexError:
            # if there is no price info at all, the game is free or not available and we return a tuple with a "-" and a 0.0
            break
    if match:
        return (match.group(1), match.group(2)), i
    else:
        return ("-", 0.0), i