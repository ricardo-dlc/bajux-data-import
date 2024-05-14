# Index(['SKU', 'GRUPO', 'ARMADORA', 'DESCRIPCION', 'COD NUEVO', 'PRECIO + IVA'], dtype='object')

# Index(['Identificador de URL', 'Nombre', 'Categorías', 'Nombre de propiedad 1',
#        'Valor de propiedad 1', 'Nombre de propiedad 2', 'Valor de propiedad 2',
#        'Nombre de propiedad 3', 'Valor de propiedad 3', 'Precio',
#        'Precio promocional', 'Peso (kg)', 'Alto (cm)', 'Ancho (cm)',
#        'Profundidad (cm)', 'Stock', 'SKU', 'Código de barras',
#        'Mostrar en tienda', 'Envío sin cargo', 'Descripción', 'Tags',
#        'Título para SEO', 'Descripción para SEO', 'Marca', 'Producto Físico',
#        'MPN (Número de pieza del fabricante)', 'Sexo', 'Rango de edad',
#        'Costo'],
#       dtype='object')

import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import quote
from product import generate_description

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Define the columns for the DataFrame
columns = ['SKU']

# Create an empty DataFrame with columns defined
no_detail_products = pd.DataFrame(columns=columns)


def get_details_from_sku(sku):
    # URL of the webpage
    base_url = 'https://todorefacciones.mx'
    url = f'{base_url}/search?q={sku}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Check if search has results
    product_articles = soup.select(
        'main#collection > div.row > article.product')
    if product_articles:
        # If results found, extract the URL of the first product
        first_product = product_articles[0]
        product_url = first_product.find('a')['href']

        if product_url:
            product_url = base_url + product_url

            # Make a request to the product page
            product_response = requests.get(product_url)
            product_soup = BeautifulSoup(
                product_response.content, 'html.parser')

            product_details = product_soup.select_one(
                '#single-description > div')
            for tag in product_details.find_all(attrs={"data-mce-fragment": True}):
                del tag['data-mce-fragment']
            del product_details['class']
            return str(product_details)
    else:
        print("No results found for SKU:", sku)
        no_detail_products._append({"SKU": sku}, ignore_index=True)
        return None


def build_details(sku):
    delay = random.randint(1, 5)  # Random delay between 1 to 5 seconds
    time.sleep(delay)
    description = get_details_from_sku(sku)
    return description if description else ""


def main():
    data = pd.read_excel('catalog.xlsx', skiprows=5)
    products = pd.read_csv('products.csv', sep=';')

    products["Nombre"] = data["DESCRIPCION"].values
    products["Identificador de URL"] = products["Nombre"].str.replace(' ', '-')
    products["Identificador de URL"] = products["Identificador de URL"].apply(
        quote)
    products["Categorías"] = "Tiendas oficiales > Grupo Refaccionario TR > " + \
        data["GRUPO"] + " > " + data["ARMADORA"]
    products["Nombre de propiedad 1"] = "Armadora"
    products["Valor de propiedad 1"] = data["ARMADORA"]
    products["Nombre de propiedad 2"] = "Grupo"
    products["Valor de propiedad 2"] = data["GRUPO"]
    products["Nombre de propiedad 3"] = "Distribuidor"
    products["Valor de propiedad 3"] = "Grupo TR"
    products["Costo"] = data["PRECIO + IVA"]
    products["Precio"] = (data["PRECIO + IVA"] * 1.16) * 1.56
    products["Peso (kg)"] = 4
    products["productDetails"] = data["SKU"].apply(build_details)
    products["Descripción"] = products.apply(
        lambda row: generate_description(row, additional_text=products["productDetails"]), axis=1)
    products[['Alto (cm)', 'Ancho (cm)', 'Profundidad (cm)']] = 30
    products["Stock"] = 10
    products["MPN (Número de pieza del fabricante)"] = data["SKU"]
    products["SKU"] = data["SKU"]
    products["Mostrar en tienda"] = "SÍ"
    products["Producto Físico"] = "SÍ"
    products["Envío sin cargo"] = "NO"

    products.to_csv(sep=';', index=False, path_or_buf='data_to_import.csv')
    no_detail_products.to_csv(sep=';', index=False,
                              path_or_buf='no_detail_products_log.csv')

    print(products)


if __name__ == "__main__":
    main()
