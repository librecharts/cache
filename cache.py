import os
import ssl
from fastapi import FastAPI, HTTPException, Request
import httpx
from datetime import datetime, timedelta
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

cache = FastAPI(docs_url=None, redoc_url=None)

cache.add_middleware(
    CORSMiddleware,
    allow_origins=["librecharts.org", "librecharts.com"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

CHARTS_DIRECTORY = os.getcwd() + '/charts'

if not os.path.exists(CHARTS_DIRECTORY):
    os.mkdir(CHARTS_DIRECTORY)

cached_files: list[str] = os.listdir(CHARTS_DIRECTORY)


@cache.get("/chart/{url:path}")
async def index(url: str) -> FileResponse:
    filename = url.split('/')[-1]
    file_path = CHARTS_DIRECTORY + '/' + filename

    async def __do_update_from_internet() -> None:

        ssl_context = httpx.create_ssl_context()
        ssl_context.options |= 0x4

        async with httpx.AsyncClient(verify=ssl_context) as client:
            headers: dict[str, str] = {
                'User-Agent': 'LibreCharts Proxy Service'
            }

            cookies: dict[str, str] = {}

            if url.startswith('https://www.aip.net.nz/'):
                cookies['disclaimer'] = '1'
            try:
                response = await client.get(url, headers=headers, cookies=cookies, timeout=15.0)
            except ssl.SSLCertVerificationError:
                async with httpx.AsyncClient(verify=False) as non_verify_client:
                    response = await non_verify_client.get(url, headers=headers, cookies=cookies, timeout=15.0)
            if 'application/pdf' not in response.headers.get('content-type') or response.status_code != 200:
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


@cache.get("/status/health")
async def health() -> dict[str, bool]:
    return {"healthy": True}


@cache.exception_handler(httpx.ConnectTimeout)
async def unicorn_exception_handler(request: Request, exc: httpx.ConnectTimeout):
    raise HTTPException(status_code=408, detail='Timed out fetching PDF file')