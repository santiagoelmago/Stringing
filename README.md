# StringFlow

StringFlow is an app to facilitate the tennis racket stringing process.

## Run for Development
```bash
# In case of not having docker-compose... install it with:
# sudo pip install docker-compose

docker-compose up --build
```

> run a local auto-reload service.

## Run for Production
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```
> Run a Gunicorn server ready for production and database resiliency.

## Ports
development and production severs will be available at:
```bash
0.0.0.0:5000 or 127.0.0.1:5000
```