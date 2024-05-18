import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote
from htmlmin import minify


def generate_description(row, additional_text=""):
    template_path = './template.html'
    with open(template_path, 'r') as file:
        html_text = file.read()

    template_soup = BeautifulSoup(html_text, 'html.parser')
    description_template_soup = template_soup.select_one(
        '#bajux-item-description')

    text_description_template = "%s.%s Número de parte: %s. Código de barras: %s."

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
        row["Nombre"], " Marca: " + row[brand] + "." if brand else "", row["SKU"], row["SKU"])
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

    print("Product hasn't addtional details")
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
    product["Descripción"] = product.apply(
        lambda row: generate_description(row), axis=1)
    product["Descripción"] = product.apply(
        lambda row: add_details(row["Descripción"], row["productDetails"]), axis=1)
    product["Descripción"] = product.apply(
        lambda row: add_extra_data(row["Descripción"], extra_html), axis=1)
    product.to_csv("test-product-output.csv",
                   encoding="UTF-8", index=False)


if __name__ == "__main__":
    main()
