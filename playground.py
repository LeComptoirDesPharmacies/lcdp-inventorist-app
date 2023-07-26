from api.consume.gen.product.model.barcodes import Barcodes

if __name__ == '__main__':
    sign = set([])
    codes = Barcodes(cip='MYCIP', eans=['EAN', 'EAN2'], principal='MYCIP')
    for code_name in codes.attribute_map.keys():
        if codes.get(code_name):
            if type(codes.get(code_name)) in list:
                sign.update(codes.get(code_name))
            else:
                sign.add(codes.get(code_name))
    print(sign)