# StringFlow

StringFlow is an app to facilitate the tennis racket stringing process.

## Run with venv (python virtual environment)

```bash
# Create a virtual env.
python -m venv venv

# Activate virtual env.
source ./venv/bin/activate

# Install project dependencies.
pip install -r requirements.txt

# Run the server.
python main.py
```

## Run with Docker
```bash
# In case of not having docker-compose... install it with:
# sudo pip install docker-compose

docker-compose up --build
```

# Ports

development and production severs will be available at:
```bash
0.0.0.0:5000

# or

127.0.0.1:5000
```