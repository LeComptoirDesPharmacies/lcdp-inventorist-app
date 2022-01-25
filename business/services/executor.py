import logging
from business.exceptions import CannotCreateProduct
from business.services.laboratory import get_laboratory_by_name, create_laboratory
from business.services.product import get_product_by_barcode, create_product_with_barcode, find_product_type_by_name, \
    get_vat_by_value, create_product_from_scratch
from business.services.sale_offer import find_sale_offer, create_sale_offer, edit_sale_offer


def process_line(excel_line):
    print('can_create_sale_offer', excel_line.can_create_sale_offer())
    if excel_line.can_create_sale_offer():
        try:
            product = find_or_create_product(excel_line.sale_offer.product, excel_line.can_create_product_from_scratch())
            sale_offer = create_or_edit_sale_offer(excel_line.sale_offer, product)
            print('sale_offer', sale_offer)
        except Exception as err:
            logging.error('An error occur during line processing', err)
    return excel_line


def find_or_create_product(product, can_create_product_from_scratch):
    result_product = get_product_by_barcode(product.principal_barcode)
    if result_product:
        return result_product

    result_product = create_product_with_barcode(product.principal_barcode)
    if result_product:
        return result_product

    # Create product from scratch
    if can_create_product_from_scratch:
        product_type = find_product_type_by_name(product.product_type.name)
        print('product_type', product_type)
        laboratory = find_or_create_laboratory(product.laboratory.name)
        print('laboratory', laboratory)
        vat = get_vat_by_value(product.vat.value)
        return create_product_from_scratch(
            product,
            product_type,
            vat,
            laboratory
        )
    else:
        raise CannotCreateProduct()


def find_or_create_laboratory(laboratory_name):
    laboratory = get_laboratory_by_name(laboratory_name)
    if not laboratory:
        laboratory = create_laboratory(laboratory_name)
    return laboratory


def create_or_edit_sale_offer(sale_offer, product):
    existing_sale_offer = find_sale_offer(
     sale_offer,
     product.id
    )
    if not existing_sale_offer:
        return create_sale_offer(sale_offer, product.id)
    else:
        return edit_sale_offer(existing_sale_offer.reference, sale_offer)
