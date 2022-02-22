import logging

from api.consume.gen.sale_offer.model.sale_offer_creation_parameters import SaleOfferCreationParameters
from api.consume.gen.sale_offer.model.sale_offer_update_parameters import SaleOfferUpdateParameters
from business.exceptions import CannotCreateSaleOffer, SaleOfferNotFoundByReference
from business.mappers.sale_offer import distribution_to_dto, stock_to_dto
from business.models.update_policy import UpdatePolicy
from business.services.providers import get_manage_sale_offer_api, get_search_sale_offer_api
from business.services.security import get_api_key
from business.utils import clean_none_from_dict


def create_sale_offer(sale_offer, product):
    logging.info(f'product {sale_offer.product.principal_barcode} : '
                 f'No sale offer is already exist, create sale offer')
    return __create_sale_offer(sale_offer, product.id)


def find_sale_offer(sale_offer, product):
    logging.info(f'product {sale_offer.product.principal_barcode} : Try to find existing sale offer')
    existing_sale_offer = None
    if sale_offer.update_policy == UpdatePolicy.PRODUCT_BARCODE.value:
        existing_sale_offer = __find_sale_offer(
            sale_offer,
            product.id
        )
    elif sale_offer.update_policy == UpdatePolicy.SALE_OFFER_REFERENCE.value and sale_offer.reference:
        existing_sale_offer = __get_sale_offer(
            sale_offer.reference
        )
    return existing_sale_offer


def edit_sale_offer(existing_sale_offer, sale_offer):
    logging.info(f'product {sale_offer.product.principal_barcode} : '
                 f'Sale offer already exist, edit existing sale offer')
    return __edit_sale_offer(existing_sale_offer.reference, sale_offer)


def create_or_edit_sale_offer(sale_offer, product, can_create_sale_offer):
    existing_sale_offer = find_sale_offer(sale_offer, product)

    if existing_sale_offer:
        return edit_sale_offer(existing_sale_offer, sale_offer)
    elif not existing_sale_offer and can_create_sale_offer:
        return create_sale_offer(sale_offer, product)
    else:
        raise CannotCreateSaleOffer()


def __find_sale_offer(sale_offer, product_id):
    api = get_search_sale_offer_api()
    sale_offers = api.get_sale_offers(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        p_eq=[product_id],
        o_eq=[sale_offer.owner_id],
        st_eq=['ENABLED', 'WAITING_FOR_PRODUCT', 'ASKING_FOR_INVOICE', 'HOLIDAY'],
        p=0,
        pp=1,
    )
    return next(iter(sale_offers.records), None)


def __get_sale_offer(reference):
    api = get_search_sale_offer_api()
    sale_offer = api.get_sale_offer(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        sale_offer_reference=reference
    )
    if not sale_offer:
        raise SaleOfferNotFoundByReference()
    return sale_offer


def __create_sale_offer(sale_offer, product_id):
    api = get_manage_sale_offer_api()
    result = api.create_sale_offer(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        sale_offer_creation_parameters=SaleOfferCreationParameters(
            owner_id=sale_offer.owner_id,
            description=sale_offer.description,
            product_id=product_id,
            rank=sale_offer.rank,
            distribution_mode=distribution_to_dto(sale_offer.distribution),
            stock=stock_to_dto(sale_offer.stock)
        )
    )
    return result


def __edit_sale_offer(reference, sale_offer):
    api = get_manage_sale_offer_api()
    payload = clean_none_from_dict({
        'description': sale_offer.description,
        'rank': sale_offer.rank,
        'distribution_mode': distribution_to_dto(sale_offer.distribution),
        'stock': stock_to_dto(sale_offer.stock)
    })
    result = api.create_sale_offer_version(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        sale_offer_reference=reference,
        sale_offer_update_parameters=SaleOfferUpdateParameters(**payload)
    )
    return result

