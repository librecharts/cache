import os
from fastapi import FastAPI, HTTPException
import httpx
from datetime import datetime, timedelta
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

cache = FastAPI(docs_url=None, redoc_url=None)

cache.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

CHARTS_DIRECTORY = os.getcwd() + '/charts'

if not os.path.exists(CHARTS_DIRECTORY):
    os.mkdir(CHARTS_DIRECTORY)

cached_files: list[str] = os.listdir(CHARTS_DIRECTORY)


@cache.get("/{url:path}")
async def index(url: str) -> FileResponse:
    if not url.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Not a valid PDF file provided")
    else:
        filename = url.split('/')[-1]
        file_path = CHARTS_DIRECTORY + '/' + filename

        async def __do_update_from_internet() -> None:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers={'User-Agent': 'LibreCharts Proxy Service'})
                if response.headers.get('content-type') != 'application/pdf' or response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail='Failed fetching a valid PDF file')

                with open(file_path, 'wb') as chart_file:
                    chart_file.write(response.content)

                cached_files.append(filename)

        if filename not in cached_files:
            await __do_update_from_internet()
        elif datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path)) > timedelta(days=1):
            await __do_update_from_internet()

        return FileResponse(
            path=file_path,
            headers={
                'content-type': 'application/pdf'
            }
        )


@cache.get('/health')
async def health() -> dict:
    return {'healthy': True}
