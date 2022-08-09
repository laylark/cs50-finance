# [cs50-finance](https://cs50finance.mothercodesbest.dev)
My CS50 finance web application which you can manage portfolios of stocks.
 
## Setup
### asdf
* Install [asdf](https://asdf-vm.com/guide/getting-started.html#_2-download-asdf)
* Install Python
```bash
asdf install python 3.10.5
```

### Poetry
* Install [poetry](https://python-poetry.org/docs/)
* Setup virtual environment
```bash
# install requirements.txt
poetry add `cat requirements.txt`

# update dependencies
poetry add python-decouple

# update requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Usage
* Add `.env` file with API_KEY
* Run Flask server
```bash
poetry run python -m flask run --host=0.0.0.0
```

## TODO
* Document API key generation and usage
* Add `python-decouple` to read from `.env` file or env vars

## Further Reading
[python_template](https://github.com/pythoninthegrass/python_template)
