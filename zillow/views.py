from django.http.response import HttpResponse
from django.shortcuts import render
from .service import ZillowService
import asyncio


zillow_service = ZillowService()
loop = asyncio.get_event_loop()

def index(request): 
    response = loop.run_until_complete(zillow_service.query())
    return HttpResponse(response)