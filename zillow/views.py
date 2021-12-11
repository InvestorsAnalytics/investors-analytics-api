import aiohttp
from django.http.response import HttpResponse
from django.shortcuts import render
from .service import ZillowService
import asyncio


zillow_service = ZillowService()
loop = asyncio.get_event_loop()

def index(request): 
    url = request.GET.get('url', None)
    try: 
         response = loop.run_until_complete(zillow_service.query(url))
    except aiohttp.InvalidURL: 
        return HttpResponse("Invalid URL")
    except Exception: 
        return HttpResponse("Internal Server Error")
    return response