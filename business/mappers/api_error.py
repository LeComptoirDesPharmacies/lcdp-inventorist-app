

def sale_offer_api_exception_to_muggle(api_exception):
    def get_explanation(status):
        explanation = None
        if status == 417:
            explanation = "Les données transmisent sont soit identique à une annonce déjà existante, " \
                          "soit incorrect pour la création/modification d'annonce"
        return explanation
    return api_exception_to_muggle(api_exception, get_explanation)


def product_api_exception_to_muggle(api_exception):
    def get_explanation(status):
        explanation = None
        if status == 409:
            explanation = "Le produit existe déjà sous un même CIP 13, EAN ou CIP 7"
        return explanation
    return api_exception_to_muggle(api_exception, get_explanation)


def api_exception_to_muggle(api_exception, get_explanation=None):
    to = []

    if api_exception:
        if api_exception.status:
            to.append(f"Statut : {api_exception.status} ")

            if get_explanation:
                explanation = get_explanation(api_exception.status)
                if explanation:
                    to.append(f"Explication : {explanation} ")

        if api_exception.reason:
            to.append(f"Raison : {api_exception.reason} ")

        if api_exception.body:
            to.append(f"Body : {api_exception.body} ")

    return repr(to)
