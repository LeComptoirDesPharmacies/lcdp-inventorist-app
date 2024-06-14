import logging

from api.consume.gen.sale_offer import ApiException
from api.consume.gen.sale_offer.model.sale_offer_creation_parameters import SaleOfferCreationParameters
from api.consume.gen.sale_offer.model.sale_offer_new_version_parameters import SaleOfferNewVersionParameters
from api.consume.gen.sale_offer.model.sale_offer_status import SaleOfferStatus
from api.consume.gen.sale_offer.model.sale_offer_update_parameters import SaleOfferUpdateParameters
from business.exceptions import CannotCreateSaleOffer, SaleOfferNotFoundByReference, CannotUpdateSaleOfferStatus
from business.mappers.sale_offer import distribution_to_dto, stock_to_dto, stock_to_patch_dto
from business.models.update_policy import UpdatePolicy
from business.services.providers import get_manage_sale_offer_api, get_search_sale_offer_api
from business.services.security import get_api_key
from business.utils import clean_none_from_dict


def __create_sale_offer_from_scratch(sale_offer, product):
    logging.info(f'product {sale_offer.product.principal_barcode} : '
                 f'No sale offer is already exist, create sale offer')
    return __create_sale_offer(sale_offer, product.id)


def __find_existing_sale_offer(prefetched_sale_offers, sale_offer, product):
    logging.info(f'product {sale_offer.product.principal_barcode} : Try to find existing sale offer')
    existing_sale_offer = None
    if sale_offer.update_policy == UpdatePolicy.PRODUCT_BARCODE.value:
        existing_sale_offer = __find_sale_offer_for_version(
            prefetched_sale_offers,
            sale_offer.owner_id,
            product.id
        )
    elif sale_offer.update_policy == UpdatePolicy.SALE_OFFER_REFERENCE.value and sale_offer.reference:
        existing_sale_offer = __get_sale_offer(
            prefetched_sale_offers,
            sale_offer.reference
        )
    return existing_sale_offer


def __edit_existing_sale_offer(existing_sale_offer, sale_offer):
    logging.info(f'product {sale_offer.product.principal_barcode} : '
                 f'Sale offer already exist, edit existing sale offer')
    return __edit_sale_offer(existing_sale_offer, sale_offer)


def __clone_existing_sale_offer(existing_sale_offer, sale_offer):
    logging.info(f'product {sale_offer.product.principal_barcode} : '
                 f'Sale offer already exist, clone existing sale offer')
    return __clone_sale_offer(existing_sale_offer, sale_offer)


def create_or_edit_sale_offer(prefetched_sale_offers, sale_offer, product, can_create_sale_offer):
    new_sale_offer = None

    if sale_offer:
        existing_sale_offer = __find_existing_sale_offer(prefetched_sale_offers, sale_offer, product)

        if existing_sale_offer:
            if not existing_sale_offer.status.value == 'DISABLED':
                new_sale_offer = __edit_existing_sale_offer(existing_sale_offer, sale_offer)
            else:
                new_sale_offer = __clone_existing_sale_offer(existing_sale_offer, sale_offer)

        elif not existing_sale_offer and product and can_create_sale_offer:
            new_sale_offer = __create_sale_offer_from_scratch(sale_offer, product)

        if new_sale_offer:
            change_sale_offer_status(sale_offer.status, new_sale_offer.reference)
            return new_sale_offer

    raise CannotCreateSaleOffer()


def __find_sale_offer_for_version(prefetched_sale_offers, owner_id, product_id):
    if (owner_id, product_id) in prefetched_sale_offers:
        return prefetched_sale_offers[(owner_id, product_id)]

    logging.info(f'Sale offer by (owner_id, product_id) {(owner_id, product_id)} not found in cache, search in API')

    return __find_sale_offer_for_status(product_id, owner_id, ['ENABLED']) or \
        __find_sale_offer_for_status(product_id, owner_id, ['WAITING_FOR_PRODUCT', 'ASKING_FOR_INVOICE',
                                                            'HOLIDAY', 'DISABLED'])


def __find_sale_offer_for_status(product_id, owner_id, status):
    api = get_search_sale_offer_api()
    sale_offers = api.get_sale_offers(
        _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
        p_eq=[product_id],
        o_eq=[owner_id],
        st_eq=status,
        order_by=['CREATED_AT:desc'],
        p=0,
        pp=1,
    )
    return next(iter(sale_offers.records), None)


def __get_latest_sale_offers(product_ids, owner_id, status):
    api = get_search_sale_offer_api()

    try:
        sale_offers = api.get_sale_offers(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            p_eq=product_ids,
            o_eq=[owner_id],
            st_eq=status,
            order_by=['CREATED_AT:desc'],
            distinct_by='PRODUCT:LATEST_CREATED',
            p=0,
            pp=len(product_ids),
        )
    except Exception as exc:
        logging.error(f'Error while searching sale offers by product ids {product_ids}', exc)
        return []

    return sale_offers.records if sale_offers else []


def __get_sale_offers(references):
    api = get_search_sale_offer_api()

    try:
        sale_offers = api.get_sale_offers(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            ref_eq=references,
            p=0,
            pp=len(references)
        )
    except Exception as exc:
        logging.error(f'Error while searching sale offers by references {references}', exc)
        return []

    return sale_offers.records if sale_offers else []


def __get_sale_offer(prefetched_sale_offers, reference):
    if reference in prefetched_sale_offers:
        return prefetched_sale_offers[reference]

    logging.info(f'Sale offer {reference} not found in cache, search in API')

    api = get_search_sale_offer_api()
    sale_offer = api.get_sale_offer(
        _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
        sale_offer_reference=reference
    )
    if not sale_offer:
        raise SaleOfferNotFoundByReference()
    return sale_offer


def __create_sale_offer(sale_offer, product_id):
    api = get_manage_sale_offer_api()
    result = api.create_sale_offer(
        _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
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


def sale_offer_is_different_from_sale_offer(sale_offer, sale_offer_excel):
    distribution = distribution_to_dto(sale_offer_excel.distribution)
    stock = stock_to_dto(sale_offer_excel.stock)

    distribution_is_different = distribution is not None and (
            sale_offer.distribution_mode.get('maximalQuantity', None) != distribution.get('maximal_quantity', None)
            or sale_offer.distribution_mode.get('soldBy', None) != distribution.get('sold_by', None)
            or sale_offer.distribution_mode.get('type', None) != distribution.get('type', None)
            or sale_offer.distribution_mode.get('unitPrice', None) != distribution.get('unit_price', None))

    ranges_are_different = False
    ranges = sale_offer.distribution_mode.get('ranges', None)
    if ranges is not None and distribution.get('ranges', None):
        # example sale_offer.ranges [{'quantity': 2, 'unitPrice': 5.02, 'freeUnits': 1, 'id': 188506, 'rebate': 62}]
        # example distribution.ranges [{'free_units': 1, 'quantity': 2, 'unit_price': 5.02}]
        ranges_mapped = list(map(lambda r:
                                 {
                                     'free_units': r.get('freeUnits', None),
                                     'quantity': r.get('quantity', None),
                                     'unit_price': r.get('unitPrice', None),
                                 },
                                 ranges))
        pairs = zip(ranges_mapped, distribution.get('ranges', None))
        ranges_are_different = not any(x != y for x, y in pairs)

    # sale_offer.stock can be None if distribution is RANGE
    stock_is_different = (sale_offer.get('stock', None) is not None
                          and ((stock.get('lapsing_date', None) is not None
                                and sale_offer.stock.get('lapsing_date', None) != stock.get('lapsing_date', None))
                               or (stock.get('remaining_quantity', None) is not None
                                   and sale_offer.stock.get('remaining_quantity', None) != stock.get(
                                'remaining_quantity', None))
                               or (stock.get('batch', None) is not None
                                   and sale_offer.stock.get('batch', None) != stock.get('batch', None))))

    return (sale_offer.rank != sale_offer_excel.rank
            or sale_offer.description != sale_offer_excel.description
            or distribution_is_different
            or stock_is_different
            or ranges_are_different)


def __edit_sale_offer(old_sale_offer, new_sale_offer):
    if sale_offer_is_different_from_sale_offer(old_sale_offer, new_sale_offer):
        try:
            api = get_manage_sale_offer_api()
            payload = clean_none_from_dict({
                'description': new_sale_offer.description,
                'rank': new_sale_offer.rank,
                'distribution_mode': distribution_to_dto(new_sale_offer.distribution),
                'stock': stock_to_patch_dto(new_sale_offer.stock)
            })
            result = api.create_sale_offer_version(
                _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
                sale_offer_reference=old_sale_offer.reference,
                sale_offer_new_version_parameters=SaleOfferNewVersionParameters(**payload)
            )
        except ApiException as apiError:
            if str(apiError.status) == '417' or str(apiError.status) == '409':
                return old_sale_offer
            raise apiError
        return result

    return old_sale_offer


def __clone_sale_offer(old_sale_offer, new_sale_offer):
    try:
        api = get_manage_sale_offer_api()
        payload = clean_none_from_dict({
            'description': new_sale_offer.description,
            'rank': new_sale_offer.rank,
            'distribution_mode': distribution_to_dto(new_sale_offer.distribution),
            'stock': stock_to_patch_dto(new_sale_offer.stock)
        })
        result = api.create_sale_offer(
            _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
            _from=old_sale_offer.reference,
            sale_offer_creation_parameters=SaleOfferCreationParameters(**payload)
        )
    except ApiException as apiError:
        raise apiError
    return result


def delete_deprecated_sale_offers(owner_id):
    api = get_manage_sale_offer_api()
    api.delete_sale_offers(
        _request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
        o_eq=[owner_id],
        st_eq=['ENABLED', 'WAITING_FOR_PRODUCT', 'ASKING_FOR_INVOICE', 'HOLIDAY'],
    )


def change_sale_offer_status(sale_offer_status_excel, sale_offer_reference):
    if sale_offer_status_excel is not None:
        status = sale_offer_status_excel.upper()
        logging.info(f'Change sale offer {sale_offer_reference} status to {status}')
        __update_sale_offer_status(sale_offer_reference, status)


def __update_sale_offer_status(sale_offer_reference, status):
    try:
        api = get_manage_sale_offer_api()
        status = SaleOfferStatus(status)
        api.update_sale_offer(_request_auths=[api.api_client.create_auth_settings("apiKeyAuth", get_api_key())],
                              sale_offer_reference=sale_offer_reference,
                              sale_offer_update_parameters=SaleOfferUpdateParameters(status=status))
    except Exception:
        raise CannotUpdateSaleOfferStatus()
