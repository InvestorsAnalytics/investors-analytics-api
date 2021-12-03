from bs4 import BeautifulSoup
import asyncio, aiohttp
import re
from utils.requests import fetch

semaphore = asyncio.Semaphore(value=10)

class PropertyScraper: 
    def __init__(self, sheet): 
        self.sheet = sheet
        self.headers = { 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36' }

    async def scrape(self, text): 
        links = self.scrape_properties(text)
        coros = [ self.scrape_property_safe(link) for link in links ]
        asyncio.Semaphore(value=10)
        response = await asyncio.gather(*coros)
        self.save(response)

    async def scrape_property_safe(self, link): 
        async with semaphore: 
            return await self.scrape_property(link)

    def save(self, data): 
        for row, property in enumerate(data, start=1): 
            for col, (_, value) in enumerate(property.items()): 
                self.sheet.cell(coords=(row, col), value=value)

    def scrape_properties(self, text, max=None): 
        soup = BeautifulSoup(text, features="html.parser")
        properties = tuple(soup.find_all("article", { "class": "list-card" }))
        if not max is None and isinstance(max, int): 
            properties = properties[:max] if max < len(properties) else properties[:len(properties) - 1]
        property_links = [ self.scrape_link(prop) for prop in properties ]
        return property_links

    async def scrape_property(self, link): 
        property = {}
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64,verify_ssl=False), headers=self.headers, trust_env=True) as session: 
            try: 
                _, text = await fetch(session=session, url=link)
                soup = BeautifulSoup(text, features="html.parser")
                property['address'] = self.scrape_address(soup)
                property['price'] = self.scrape_price(soup)
                property['zestimate'] = self.scrape_zestimate(soup)
                property['bedrooms'] = self.scrape_bedrooms(soup)
                property['bathrooms'] = self.scrape_bathrooms(soup)
                property['type'] = self.scrape_property_type(soup)
                property['year_built'] = self.scrape_year_built(soup)
                property['lot'] = self.scrape_lot(soup)
                property['price_per_sqft'] = self.scrape_price_per_sqft(soup)
                property['sqft'] = self.scrape_sqft(soup)
                property['link'] = link
            except Exception: return property
        return property

    def scrape_price(self, soup): 
        try: 
            price = soup.find("div", { 'class': "ds-summary-row" }).find("span").text
            price = re.sub('[\s]', '', price); 
            return price
        except Exception: return None

    def scrape_property_type(self, soup): 
        try:
           type = soup.find("span", text="Type:").find_next_siblings("span")[0].text
           return type if type else None
        except Exception: return None

    def scrape_year_built(self, soup): 
        try:
            elem = soup.find("span", text="Year built:")
            year_built = elem.find_next_siblings("span")[0].text
            return year_built if year_built else None
        except Exception: return None
    
    def scrape_price_per_sqft(self, soup): 
        try:
            elem = soup.find("span", text="Price/sqft:")
            detail = elem.find_next_siblings("span")[0].text
            return detail if detail else None
        except Exception: return None
    
    def scrape_lot(self, soup): 
        try:
            elem = soup.find("span", text="Lot:")
            detail = elem.find_next_siblings("span")[0].text
            return detail if detail else None
        except Exception: return None

    def scrape_sqft(self, soup): 
        try: 
           details = soup.find("span", { "class": "ds-bed-bath-living-area-container"})
           count, detail = details.findChildren("span" , recursive=False)[3].findAll("span")
           sqft = count.text
           return sqft if "sqft" in detail.text.lower() else None
        except Exception: return None

    def scrape_bedrooms(self, soup): 
        try: 
           details = soup.find("span", { "class": "ds-bed-bath-living-area-container"})
           count, detail = tuple(details.find("span").findAll("span"))
           bedrooms = count.text
           return bedrooms if "bd" in detail.text.lower() else None
        except Exception: return None

    def scrape_bathrooms(self, soup): 
        try: 
           details = soup.find("span", { "class": "ds-bed-bath-living-area-container"})
           count, detail = tuple(details.find("button").find("span").findAll("span"))
           bathrooms = count.text
           return bathrooms if "ba" in detail.text.lower() else None
        except Exception: return None

    def scrape_address(self, soup): 
        try: 
            address = soup.find("h1", { 'id': "ds-chip-property-address" }).text
            return address
        except Exception: return None

    def scrape_zestimate(self, soup):
        try: 
            zestimate_button = soup.findAll("button", { "id": "ds-primary-zestimate-tooltip" })
            zestimate = zestimate_button[0].find_next_siblings("div")[0].text
            #zestimate = re.sub('[\s]', '', zestimate); 
            return zestimate
        except Exception: return None

    def scrape_link(self, prop) -> None | str: 
        try:
            container = prop.find("div", { "class": "list-card-top" })
            link = container.find("a", { "class": "list-card-link" }).attrs['href']
            return link
        except AttributeError and Exception:
            return None

    def print_header(self, headerfmt):
        header = ["Address", "Price", "Zestimate", "Bedrooms", "Bathrooms", "Type", "Year Built", "Lot", "Price/sqft", "Square Feet", "Link"]
        for col, label in enumerate(header):
            self.sheet.cell(coords=(0,col), value=label, format=headerfmt)