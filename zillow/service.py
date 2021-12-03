import aiohttp
from utils.requests import fetch
from .prop_funcs import PropertyScraper
from xlsxcessive.workbook import Workbook
from xlsxcessive.xlsx import save

class ZillowService: 
    def __init__(self): 
        self.headers = { 
            'upgrade-insecure-requests': '1',
            'accept-language': 'en-US,en;q=0.8',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36' 
        }

    async def query(self): 
        wb = Workbook()
        sheet = wb.new_sheet('properties')
        headerfmt = wb.stylesheet.new_format()
        impfmt = wb.stylesheet.new_format()
        headerfmt.font(size=10, bold=True)
        impfmt.font(size=10, color='red', bold=True)
        scraper = PropertyScraper(sheet=sheet)
        scraper.print_header(headerfmt)

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64,verify_ssl=False), headers=self.headers, trust_env=True) as session: 
            url = "https://www.zillow.com/middlesex-county-nj/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Southesk%2C%20NB%22%2C%22mapBounds%22%3A%7B%22west%22%3A-74.69098171020507%2C%22east%22%3A-74.36928828979491%2C%22south%22%3A40.20346318696338%2C%22north%22%3A40.565918551741134%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A47755%2C%22regionType%22%3A31%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22min%22%3A100000%7D%2C%22mp%22%3A%7B%22min%22%3A335%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22mapZoom%22%3A11%7D"
            _, text = await fetch(session=session, url=url)
            await scraper.scrape(text)

        save(wb, 'property_analysis.xlsx')

        return "Zillow Service"