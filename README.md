# [cs50-finance](https://cs50finance.mothercodesbest.dev)
My CS50 finance web application which you can manage portfolios of stocks.
 
## Setup
### asdf
* Install [asdf](https://asdf-vm.com/guide/getting-started.html#_2-download-asdf)
* Install Python
```bash
asdf install python 3.10.5
```
* Install [editorconfig](https://editorconfig.org/#download)
* Install [poetry](https://python-poetry.org/docs/)

### Poetry
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
* `.editorconfig` enforces code formatting automatically after being installed
  * Can also be added at root-level vs. repos via `root = true`
* `.dockerignore` prevents files and directories from being captured in images during builds
* Add `.env` file with API_KEY
* Run Flask server
```bash
poetry run python -m flask run --host=0.0.0.0
```

## TODO
* Document API key generation and usage
* Add `python-decouple` to read from `.env` file or env vars

## Further Reading
[EditorConfig](https://editorconfig.org/#example-file)

[Dockerfile reference | Docker Documentation](https://docs.docker.com/engine/reference/builder/#dockerignore-file)

[python_template](https://github.com/pythoninthegrass/python_template)
