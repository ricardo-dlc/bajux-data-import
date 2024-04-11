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
from htmlmin import minify

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

file_path = './template.html'

with open(file_path, 'r') as file:
    html_text = file.read()

minified_html = minify(html_text)

def url_encode(text):
    return quote(text)

def get_description_from_sku(sku):
    # URL of the webpage
    base_url = 'https://todorefacciones.mx'
    url = f'{base_url}/search?q={sku}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Check if search has results
    product_articles = soup.select('main#collection > div.row > article.product')
    if product_articles:
        # If results found, extract the URL of the first product
        first_product = product_articles[0]
        product_url = first_product.find('a')['href']

        if product_url:
            product_url = base_url + product_url

            # Make a request to the product page
            product_response = requests.get(product_url)
            product_soup = BeautifulSoup(product_response.content, 'html.parser')

            description = product_soup.select_one('#single-description > div')
            del description['class']
            return str(description)
    else:
        print("No results found for SKU:", sku)


def build_description(sku):
    delay = random.randint(1, 5)  # Random delay between 1 to 5 seconds
    time.sleep(delay)
    description = get_description_from_sku(sku)
    if description:
        new_description = BeautifulSoup(description, 'html.parser')
        brand = new_description.find('p', string=lambda text: text and "MARCA:" in text.upper())
        if brand:
            brand = brand.string.replace("MARCA:", "", 1).strip()
        else:
            print('No brand has been found.')
            print(brand)
            brand = None

        original_description = BeautifulSoup(minified_html, 'html.parser')

        # Find the div with id "description"
        description_div = original_description.find('div', id='bjx-item-description')
        description_div.insert_after(new_description.div)
        return {'brand': brand, 'description': str(original_description)}
    else:
        return {'brand': None, 'description': minified_html}


def main():
    data = pd.read_excel('catalog.xlsx', skiprows=5)
    products = pd.read_csv('products.csv', sep=';')

    products["Nombre"] = data["DESCRIPCION"].values
    products["Identificador de URL"] = products["Nombre"].str.replace(' ', '-')
    products["Identificador de URL"] = products["Identificador de URL"].apply(url_encode)
    products["Categorías"] = "Tiendas oficiales > Grupo Refaccionario TR > " + data["GRUPO"] + " > " + data["ARMADORA"]
    products["Nombre de propiedad 1"] = "Armadora"
    products["Valor de propiedad 1"] = data["ARMADORA"]
    products["Nombre de propiedad 2"] = "Grupo"
    products["Valor de propiedad 2"] = data["GRUPO"]
    products["Nombre de propiedad 3"] = "Distribuidor"
    products["Valor de propiedad 3"] = "Grupo TR"
    products["Precio"] = (data["PRECIO + IVA"] * 1.16) * 1.56
    products["Peso (kg)"] = 4
    products["Description_and_brand"] =  data["SKU"].apply(build_description)
    products[['Alto (cm)', 'Ancho (cm)', 'Profundidad (cm)']] = 30
    products["Stock"] = 10
    products["MPN (Número de pieza del fabricante)"] = data["SKU"]
    products["SKU"] = data["SKU"]
    products["Mostrar en tienda"] = "SÍ"
    products["Producto Físico"] = "SÍ"
    products["Envío sin cargo"] = "NO"

    products.to_csv(sep=';', index=False, path_or_buf='new_data.csv')

    print(products)



if __name__ == "__main__":
    main()