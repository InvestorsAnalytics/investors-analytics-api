async def fetch(session, method="GET", *args, **kwargs): 
    if method == "GET":
        async with session.get(*args, **kwargs) as response:
            return response, await response.text()
    elif method == "POST": 
        async with session.post(*args, **kwargs) as response:
            return response