import fastapi
import xmltodict

async def payload(request: fastapi.Request):
    return xmltodict.parse(await request.body())
