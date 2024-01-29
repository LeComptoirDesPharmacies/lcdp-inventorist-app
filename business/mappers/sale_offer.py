from api.consume.gen.sale_offer.model.any_distribution_mode import AnyDistributionMode
from api.consume.gen.sale_offer.model.distribution_range import DistributionRange
from api.consume.gen.sale_offer.model.stock import Stock
from business.models.sale_offer import UNITARY_DISTRIBUTION, RANGE_DISTRIBUTION, QUOTATION_DISTRIBUTION
from business.utils import clean_none_from_dict


def distribution_to_dto(distribution):
    if distribution and not distribution.is_empty():
        if distribution.type == UNITARY_DISTRIBUTION:
            return AnyDistributionMode(
                type='UNITARY',
                unit_price=distribution.discounted_price,
                sold_by=distribution.sold_by,
                minimal_quantity=1,
                maximal_quantity=distribution.maximal_quantity
            )
        elif distribution.type == RANGE_DISTRIBUTION:
            return AnyDistributionMode(
                type='RANGE',
                minimal_quantity=1,
                maximal_quantity=distribution.maximal_quantity,
                ranges=list(map(__range_to_dto, distribution.ranges)),
            )
        elif distribution.type == QUOTATION_DISTRIBUTION:
            return AnyDistributionMode(
                type='QUOTATION',
                sold_by=1,
                minimal_quantity=1,
                maximal_quantity=distribution.maximal_quantity
            )
    return None


def __range_to_dto(sale_offer_range):
    return DistributionRange(
        quantity=sale_offer_range.sold_by,
        unit_price=sale_offer_range.discounted_price,
        free_units=sale_offer_range.free_unit if sale_offer_range.free_unit else 0
    )


def stock_to_dto(stock):
    if stock and not stock.is_empty():
        return Stock(
            remaining_quantity=stock.remaining_quantity,
            lapsing_date=stock.lapsing_date,
            batch=stock.batch
        )
    return Stock()

def stock_to_patch_dto(stock):
    if stock and not stock.is_empty():
        return Stock(**clean_none_from_dict({
                'remaining_quantity': stock.remaining_quantity,
                'lapsing_date': stock.lapsing_date,
                'batch': stock.batch
            })
        )
    return None
