import logging

from api.consume.gen.sale_offer.model.sale_offer_creation_parameters import SaleOfferCreationParameters
from api.consume.gen.sale_offer.model.sale_offer_update_parameters import SaleOfferUpdateParameters
from business.exceptions import CannotCreateSaleOffer
from business.mappers.sale_offer import distribution_to_dto
from business.services.providers import get_manage_sale_offer_api, get_search_sale_offer_api
from business.services.security import get_api_key
from business.utils import clean_none_from_dict


def create_sale_offer(sale_offer, product):
    logging.info(f'product {sale_offer.product.principal_barcode} : '
                 f'No sale offer is already exist, create sale offer')
    return __create_sale_offer(sale_offer, product.id)


def create_or_edit_sale_offer(sale_offer, product, can_create_sale_offer):
    logging.info(f'product {sale_offer.product.principal_barcode} : Try to find existing sale offer')
    existing_sale_offer = __find_sale_offer(
     sale_offer,
     product.id
    )
    if not existing_sale_offer and can_create_sale_offer:
        return create_sale_offer(sale_offer, product)
    elif existing_sale_offer:
        logging.info(f'product {sale_offer.product.principal_barcode} : '
                     f'Sale offer already exist, edit existing sale offer')
        return __edit_sale_offer(existing_sale_offer.reference, sale_offer)
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


def __create_sale_offer(sale_offer, product_id):
    api = get_manage_sale_offer_api()
    result = api.create_sale_offer(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        sale_offer_creation_parameters=SaleOfferCreationParameters(
            owner_id=sale_offer.owner_id,
            description=sale_offer.description,
            product_id=product_id,
            rank=sale_offer.rank,
            distribution_mode=distribution_to_dto(sale_offer.distribution)
        )
    )
    return result


def __edit_sale_offer(reference, sale_offer):
    api = get_manage_sale_offer_api()
    payload = clean_none_from_dict({
        'description': sale_offer.description,
        'rank': sale_offer.rank,
        'distribution_mode': distribution_to_dto(sale_offer.distribution)
    })
    result = api.create_sale_offer_version(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        sale_offer_reference=reference,
        sale_offer_update_parameters=SaleOfferUpdateParameters(**payload)
    )
    return result

