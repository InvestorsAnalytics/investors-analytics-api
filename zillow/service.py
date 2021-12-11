import aiohttp
from utils.requests import fetch
from .prop_funcs import PropertyScraper
from xlsxcessive.workbook import Workbook
from xlsxcessive.xlsx import save
from django.http.response import HttpResponse

class ZillowService: 
    def __init__(self): 
        self.headers = { 
            'upgrade-insecure-requests': '1',
            'accept-language': 'en-US,en;q=0.8',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36' 
        }

    async def query(self, url): 
        wb = Workbook()
        sheet = wb.new_sheet('properties')
        headerfmt = wb.stylesheet.new_format()
        impfmt = wb.stylesheet.new_format()
        headerfmt.font(size=10, bold=True)
        impfmt.font(size=10, color='red', bold=True)
        scraper = PropertyScraper(sheet=sheet)
        scraper.print_header(headerfmt)

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64,verify_ssl=False), headers=self.headers, trust_env=True) as session: 
            _, text = await fetch(session=session, url=url)
            await scraper.scrape(text)

        save(wb, 'sheets/property_analysis.xlsx')
        
        with open("sheets/property_analysis.xlsx", "rb") as excel:
            data = excel.read()
        response = HttpResponse(data, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="property_analysis.xlsx"'

        return response