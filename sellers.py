import pandas as pd
from product import update_price, generate_new_sku, generate_provider_code, generate_description, add_details, custom_encode


def main():
    store_name = "Filtros y Aceites Jamis"
    provider_code = generate_provider_code(store_name)

    data = pd.read_excel('Filtros y Aceites Jamis.xlsx')
    products = pd.read_csv('products.csv', sep=';')

    data["Nombre"] = data["Nombre"].str.title()
    data["Nombre"] = data["Nombre"].str.strip()
    # data["Marca"] = data["Marca"].str.title()

    products["Nombre"] = data["Nombre"]
    products["Identificador de URL"] = "BJX" + provider_code + "-" + data["SKU"].astype(str) + "-" + \
        products["Nombre"].str.replace(' ', '-')
    # products["Identificador de URL"] = products["Identificador de URL"].apply(
    #     lambda url: provider_code + "-" + url)
    products["Identificador de URL"] = products["Identificador de URL"].apply(
        lambda url: custom_encode(url))
    products["Identificador de URL"] = products["Identificador de URL"].str.lower()
    products["Categorías"] = f"Tiendas oficiales > {
        store_name} > " + data["Marca"]
    products["Costo"] = data["Precio"]
    products["Precio"] = data["Precio"].apply(update_price)
    products["SKU"] = data["SKU"].apply(
        lambda sku: generate_new_sku(provider_code, sku, "BJX"))
    products["Envío sin cargo"] = products["Precio"].apply(
        lambda x: "SÍ" if x > 999.00 else "NO")
    products[["Producto Físico", "Mostrar en tienda"]] = "SÍ"
    products["MPN (Número de pieza del fabricante)"] = data["SKU"]
    products["Marca"] = data["Marca"]
    products["Nombre de propiedad 1"] = "Familia"
    products["Valor de propiedad 1"] = "Tienda Oficial"
    products["Nombre de propiedad 2"] = "Marca"
    products["Valor de propiedad 2"] = data["Marca"]
    products[["Alto (cm)", "Ancho (cm)", "Profundidad (cm)"]] = 30
    products["Peso (kg)"] = 4
    products["Stock"] = 10
    products["Detalles"] = data["Descripcion"]
    print(products["Detalles"])
    print(products["Código de barras"])
    products["Descripción"] = products.apply(
        lambda row: generate_description(row), axis=1)
    products["Descripción"] = products.apply(
        lambda row: add_details(row["Descripción"], row["Detalles"]), axis=1)
    del products["Detalles"]

    print(products)
    products.to_csv(f"{store_name.replace(' ', '')}-output.csv",
                    encoding="UTF-8", index=False)


if __name__ == "__main__":
    main()
