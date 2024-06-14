import pandas as pd
import re
from bs4 import BeautifulSoup
from htmlmin import minify
from urllib.parse import quote, unquote


def custom_encode(input_string):
    # URL-encode the input string
    encoded_string = quote(input_string, safe='')
    # Replace % with --
    custom_encoded_string = encoded_string.replace('%', '--')
    return custom_encoded_string


def custom_decode(custom_encoded_string):
    # Replace -- back with %
    encoded_string = custom_encoded_string.replace('--', '%')
    # URL-decode the string
    decoded_string = unquote(encoded_string)
    return decoded_string


def generate_provider_code(provider_name):
    # Split the provider name into words
    words = provider_name.split()
    num_words = len(words)

    if num_words == 1:
        # Case: 1 word, take the first 4 letters of the word
        base_code = words[0][:4].upper()
    elif num_words == 2:
        # Case: 2 words, take 2 letters from each word
        base_code = (words[0][:2] + words[1][:2]).upper()
    elif num_words == 3:
        # Case: 3 words, take 2 letters from the first word and 1 letter from each subsequent word
        base_code = (words[0][:2] + words[1][0] + words[2][0]).upper()
    else:
        # Case: 4 or more words, take the first letter from the first 4 words
        base_code = ''.join(word[0] for word in words[:4]).upper()

    return base_code


def generate_new_sku(provider_code, original_sku, prefix=""):
    return f"{prefix}{provider_code}-{original_sku}"


def update_price(price):
    if (price >= 0 & price < 500):
        return price * 1.2
    if (price >= 500 & price < 1000):
        return price * 1.15
    if (price >= 1000 & price < 1500):
        return price * 1.1
    return price * 1.05


def parse_scientific_notation(x):
    if pd.isna(x) or x == '':
        return ''
    # Regular expression to match valid scientific notation with a '+' sign
    scientific_notation_regex = re.compile(r'^-?\d+(\.\d+)?[eE]\+\d+$')
    if isinstance(x, str) and scientific_notation_regex.match(x):
        try:
            # Try to convert the value to a float
            num = float(x)
            # If successful, format it without scientific notation
            return '{:.0f}'.format(num)
        except ValueError:
            # If it raises a ValueError, it's already a string
            return x
    elif isinstance(x, (float, int)):
        return '{:.0f}'.format(x)
    else:
        return x


def generate_description(row):
    template_path = './template.html'
    with open(template_path, 'r') as file:
        html_text = file.read()

    template_soup = BeautifulSoup(html_text, 'html.parser')
    description_template_soup = template_soup.select_one(
        '#bajux-item-description')

    text_description_template = "%s.%s Número de parte: %s.%s"

    # Check if either "Nombre de propiedad 1" or "Nombre de propiedad 2" or "Nombre de propiedad 3" are not NaN and are equal to "marca"
    if not pd.isna(row["Nombre de propiedad 1"]) and str(row["Nombre de propiedad 1"]).strip().lower() == "marca":
        brand = "Valor de propiedad 1"
    elif not pd.isna(row["Nombre de propiedad 2"]) and str(row["Nombre de propiedad 2"]).strip().lower() == "marca":
        brand = "Valor de propiedad 2"
    elif not pd.isna(row["Nombre de propiedad 3"]) and str(row["Nombre de propiedad 3"]).strip().lower() == "marca":
        brand = "Valor de propiedad 3"
    else:
        brand = ""

    p_tag = template_soup.new_tag('p')
    p_tag.string = text_description_template % (
        row["Nombre"], " Marca: " + row[brand] + "." if brand else "", row["SKU"], " Código de barras: " + row["Código de barras"] + "." if row["Código de barras"] else "")
    placeholder_div = description_template_soup.find(
        'div', id='bajux-item-placehoder')
    placeholder_div.clear()
    placeholder_div.append(p_tag)

    return minify(str(description_template_soup), remove_optional_attribute_quotes=False)


def add_details(description, product_details=""):
    if product_details:
        print("Product has addtional details" + product_details)
        description_soup = BeautifulSoup(description, 'html.parser')
        new_details_soup = BeautifulSoup(product_details, 'html.parser')
        details_div = description_soup.find(
            'div', id='bajux-item-details')
        details_div.clear()
        details_div.append(new_details_soup)

        return minify(str(description_soup), remove_optional_attribute_quotes=False)

    return description


def add_extra_data(description, extra_html_string):
    description_soup = BeautifulSoup(description, 'html.parser')
    extra_html_soup = BeautifulSoup(extra_html_string, 'html.parser')
    details_div = description_soup.find(
        'div', id='bajux-item-description')
    details_div.append(extra_html_soup)

    return minify(str(description_soup), remove_optional_attribute_quotes=False)


def main():
    product = pd.read_csv("test-product.csv", encoding="UTF-8", sep=';')
    product["SKU"] = "ABC123XYZ"
    product["productDetails"] = ""
    extra_html = """<div class="extra-details mt-4">
        <div class="banner bajux-tuning-banner-1 mb-4"></div>
        <div class="banner bajux-tuning-banner-2 mb-4"></div>
        <div class="banner bajux-tuning-banner-3 mb-4"></div>
        <div class="banner bajux-tuning-banner-4"></div>
    </div>
"""
    product["Código de barras"] = '2E0127401'
    product["Código de barras"] = product["Código de barras"].apply(
        parse_scientific_notation)
    # Step 4: Ensure the 'values_str' column is of type string
    product['Código de barras'] = product['Código de barras'].astype(str)
    print(product["Código de barras"])
    product["Descripción"] = product.apply(
        lambda row: generate_description(row), axis=1)
    product["Descripción"] = product.apply(
        lambda row: add_details(row["Descripción"], row["productDetails"]), axis=1)
    product["Descripción"] = product.apply(
        lambda row: add_extra_data(row["Descripción"], extra_html), axis=1)
    product.to_csv("test-product-output.csv",
                   encoding="UTF-8", index=False)

    with open('./template_test.html', mode="+w") as template_test:
        template_path = './template.html'
        description_text = product.loc[0]['Descripción']
        with open(template_path, 'r') as file:
            html_text = file.read()

        template_soup = BeautifulSoup(html_text, 'html.parser')
        new_description_soup = BeautifulSoup(description_text, 'html.parser')
        description_template_soup = template_soup.select_one(
            '#bajux-item-description')
        description_template_soup.replace_with(new_description_soup)
        template_test.write(minify(str(template_soup)))


if __name__ == "__main__":
    main()
