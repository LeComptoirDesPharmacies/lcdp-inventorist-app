# LCDP-Inventorist-app

This is an app for **Le Comptoir Des Pharmacies** personal use.

This app permit to manage sale offer and product massively with excel import.

## Features

- Create/Update sale offer for PharmLab users
- Create/Update product


## Requirements

- Access to LCDP gemfury (token exported as `UV_INDEX_FURY_USERNAME`, empty `UV_INDEX_FURY_PASSWORD`)
- [uv](https://docs.astral.sh/uv/) **>= 0.11.22** (dependency manager — enforced by `pyproject.toml`)
- Python **3.12**

> Dependencies are pinned in `uv.lock` (committed). The supply-chain policy (LDS-5825) —
> ignore PyPI releases younger than 1 week, internal packages exempt — is declared in
> `pyproject.toml` `[tool.uv]` and frozen into the lock. To add/upgrade a dep:
> `uv add <pkg>` then commit the updated `uv.lock`.

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

`uv sync --frozen`

#### Prepare
Run `prepare.py` before start the app to generate codegen and 
create `config.json` file :

`uv run python prepare.py`

#### Start

Then start the app with : 

`uv run python main.py`

### Test
Run :

`uv run python prepare.py`

And then :

`uv run python -m nose2 tests -v`


## TODO

- Create/Update sale offer for Destock users