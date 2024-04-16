import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import quote
from htmlmin import minify
import ast

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

file_path = './template.html'

with open(file_path, 'r') as file:
    html_text = file.read()

minified_html = minify(html_text)


def get_description_from_sku(sku):
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
        brand = new_description.find(
            'p', string=lambda text: text and "MARCA:" in text.upper())
        if brand:
            brand = brand.string.replace("MARCA:", "", 1).strip()
        else:
            brand = False

        original_description = BeautifulSoup(minified_html, 'html.parser')

        # Find the div with id "description"
        description_div = original_description.find(
            'div', id='bjx-item-description')
        description_div.insert_after(new_description.div)
        return {'brand': brand, 'description': str(original_description)}
    else:
        return {'brand': None, 'description': minified_html}


# Define a function to convert string representation of dictionary to dictionary
def str_to_dict(s):
    try:
        # s.replace('\\n', '')
        return ast.literal_eval(s)  # Convert string to dictionary
    except ValueError:
        print('None')
        return None  # Return None if parsing fails


def extract_brand(data):
    brand = data.get('brand')
    if brand == None:
        description = BeautifulSoup(data.get('description'), 'html.parser')
        new_brand = description.find(
            string=lambda text: text and "MARCA:" in text.upper())
        if new_brand:
            new_brand = new_brand.split("MARCA:", 1)[-1].strip()
            # print(f'Brand {new_brand}')
            # data.set('brand', new_brand)
            data['brand'] = new_brand
        # else:
        #     print('No brand found')
        # print(data.get('brand'))
    return data


def clean_text(data):
    html_string = data.get('description')
    modified_html_string = html_string.replace('\\n', '')
    modified_html_string = minify(modified_html_string)

    # Parse the modified HTML string
    # soup = BeautifulSoup(modified_html_string, 'html.parser')

    # # Get the modified HTML string
    # modified_html_string = str(soup)

    data['description'] = modified_html_string

    return data

#  E3750MI


def clean_html(data):
    html = data.get('description')
    soup = BeautifulSoup(html, 'html.parser')
    # Find all br tags and remove their attributes
    for tag in soup.find_all(attrs={"data-mce-fragment": True}):
        del tag['data-mce-fragment']

    data['description'] = minify(str(soup))
    return data


def main():
    df = pd.read_csv('new_data_3.csv', sep=';', converters={
                     'Description_and_brand': str_to_dict})
    df['Description_and_brand'] = df['Description_and_brand'].apply(clean_html)
    df['Descripción'] = df['Description_and_brand'].apply(
        lambda x: x['description'])
    del df['Description_and_brand']
    # df['Description_and_brand'] = df['Description_and_brand'].apply(clean_text)
    # df['Descripción'] = df['Description_and_brand'].apply(lambda x: x['description'])

    # filtered_df = df[df['Description_and_brand'].apply(lambda x: x.get('brand') == None)]
    # filtered_df['Description_and_brand'] = filtered_df['Description_and_brand'].apply(extract_brand)
    # filtered_df['Description_and_brand'] = filtered_df['SKU'].apply(build_description)
    # df.loc[filtered_df.index, 'Description_and_brand'] = filtered_df['Description_and_brand']

    # df['Identificador de URL'] = df['Identificador de URL'].str.lower()
    # df['Nombre'] = df['Nombre'].str.title()
    # df['Valor de propiedad 1'] = df['Valor de propiedad 1'].str.title()
    # df['Valor de propiedad 2'] = df['Valor de propiedad 2'].str.title()
    # df["Categorías"] = "Tiendas oficiales > Grupo Refaccionario TR > " + df["Valor de propiedad 2"] + " > " + df["Valor de propiedad 1"]

    df.to_csv(sep=';', index=False, path_or_buf='new_data_4.csv')


if __name__ == "__main__":
    main()
