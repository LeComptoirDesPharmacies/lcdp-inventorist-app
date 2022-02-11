import os

from python_openapi_generator_cli.codegen import generate_consumer

# Get current script dir
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def run_codegen():
    generate_consumer("auth.yaml", CURRENT_DIR)
    generate_consumer("user.yaml", CURRENT_DIR)
    generate_consumer("laboratory.yaml", CURRENT_DIR)
    generate_consumer("product.yaml", CURRENT_DIR)
    generate_consumer("sale-offer.yaml", CURRENT_DIR)
    generate_consumer("configuration.yaml", CURRENT_DIR)


if __name__ == '__main__':
    # A executer avant de package l'app
    run_codegen()
