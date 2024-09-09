import os
import json

from envsubst import envsubst
from python_rest_client_codegen.codegen import generate_consumer

# Get current script dir
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def run_codegen():
    generate_consumer("auth.yaml", CURRENT_DIR)
    generate_consumer("user.yaml", CURRENT_DIR)
    generate_consumer("laboratory.yaml", CURRENT_DIR)
    generate_consumer("product.yaml", CURRENT_DIR)
    generate_consumer("sale-offer.yaml", CURRENT_DIR)
    generate_consumer("configuration.yaml", CURRENT_DIR)
    generate_consumer("catalog.yaml", CURRENT_DIR)
    generate_consumer("factory.yaml", CURRENT_DIR)


def write_config():
    config_tpl = open(os.path.join(CURRENT_DIR, 'config.json.tpl'), "r")
    config_json = json.loads(envsubst(config_tpl.read()))
    config_tpl.close()
    config_file = open(os.path.join(CURRENT_DIR, 'config.json'), "w+")
    config_file.write(json.dumps(config_json, indent=4))
    config_file.close()


if __name__ == '__main__':
    # A executer avant de package ou de run l'app
    run_codegen()
    write_config()
