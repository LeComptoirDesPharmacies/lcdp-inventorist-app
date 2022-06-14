# LCDP-Inventorist-app

This is an app for **Le Comptoir Des Pharmacies** personal use.

This app permit to manage sale offer and product massively with excel import.

## Features

- Create/Update sale offer for PharmLab users
- Create/Update product


## Requirements

- Access to LCDP jfrog Artifactory
- Jfrog CLI or `pip.conf` with jfrog extra index url
- Python **3.8**

## Configure

### Environment variables

| Name                  | Description | Default value |
| :---                  |    :----:   |          ---: |
| LCDP_ENVIRONMENT      | Where app is running, should be : **prod**, **staging** or **dev**       | _dev_   |
| PROVIDER_HOST         | Url of the server to request        | _localhost_     |
| IS_PROVIDER_SECURE    | Should use https        | _False_      |
| SENTRY_DSN            | Sentry url        |       |

Default values can be changed in `config.json.tpl`

## Run

#### Install dependencies

- With jfrog cli : `jfrog pip install -r requirements.txt`
- With pip.conf : `pip install -r requirements.txt`

#### Prepare
Run `prepare.py` before start the app to generate codegen and 
create `config.json` file :

`python prepare.py`

#### Start

Then start the app with : 

`python main.py`

### Test
Run :

`python prepare.py`

And then :

`python -m nose2 tests -v`


## TODO

- Create/Update sale offer for Destock users