from api.consume.gen.sale_offer.model.any_distribution_mode import AnyDistributionMode
from api.consume.gen.sale_offer.model.sale_offer_creation_parameters import SaleOfferCreationParameters
from api.consume.gen.sale_offer.model.sale_offer_update_parameters import SaleOfferUpdateParameters
from business.services.providers import get_manage_sale_offer_api, get_search_sale_offer_api
from business.services.security import get_api_key


def find_sale_offer(sale_offer, product_id):
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


def create_sale_offer(sale_offer, product_id):
    api = get_manage_sale_offer_api()
    result = api.create_sale_offer(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        sale_offer_creation_parameters=SaleOfferCreationParameters(
            owner_id=sale_offer.owner_id,
            product_id=product_id,
            rank=sale_offer.rank,
            distribution_mode=AnyDistributionMode(
                type='UNITARY',
                unit_price=sale_offer.distribution.discounted_price,
                minimal_quantity=sale_offer.distribution.sold_by
            )
        )
    )
    return result


def edit_sale_offer(reference, sale_offer):
    api = get_manage_sale_offer_api()
    result = api.create_sale_offer_version(
        _request_auth=api.api_client.create_auth_settings("apiKeyAuth", get_api_key()),
        sale_offer_reference=reference,
        sale_offer_update_parameters=SaleOfferUpdateParameters(
            rank=sale_offer.rank,
            distribution_mode=AnyDistributionMode(
                type='UNITARY',
                unit_price=sale_offer.discounted_price,
                minimal_quantity=sale_offer.sold_by
            )
        )
    )
    return result

