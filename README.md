<p align="center"><img src="https://raw.githubusercontent.com/librecharts/branding/main/raster/logo_transparent.png" alt="project-image" style="width: 150px"></p>
<h1 align="center" id="title">LibreCharts Cache Server</h1>
<p align="center">
    <a href="#setting-up-for-development">Developing</a>
     • 
    <a href="#contribution-guidelines">Contributing</a>
     • 
    <a href="#production">Production</a>

</p>

Simple FastAPI-powered local caching for PDF files. Provides 1 day caching for PDF chart files for the LibreCharts infrastructure.

# Features

- 1 day caching of relevant chart files to ensure speed
- Fully asynchronous operation using `httpx` and `fastapi`

## Contributing

### Setting up for development

You can set up the webpage for development as follows. We recommend using a Python virtual environment:


```shell
pip install -r requirements.txt
uvicorn cache:cache --reload
```

### Contribution guidelines

You may view the contrubition guidelines in [CONTRIBUTING.md](.github/CONTRIBUTING.md).

If you wish to contribute charts please see the [charts repository](https://github.com/librecharts/charts) if you wish to contribute towards the webpage please see the [webpage repository](https://github.com/librecharts/webpage) 


## Production

We provide a `docker-compose.yaml` file for running in production, you can run it as follows:

Summarized: 

```shell
docker compose up -d
```

In our infrastructure we expose the cache to port `8000` which is then reverse-proxied to coincide with the appropriate domain.
If you'd like to run the cache on its own (at port 80) change `docker-compose.yaml`
from
```yaml
    ports:
      - 8000:8000
```
to
```yaml
    ports:
      - 8000:80
```
