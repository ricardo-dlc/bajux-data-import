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

    if additional_text:
        new_details_soup = BeautifulSoup(additional_text, 'html.parser')
        for tag in new_details_soup.find_all(attrs={"data-mce-fragment": True}):
            del tag['data-mce-fragment']
        details_div = description_template_soup.find(
            'div', id='bajux-item-details')
        details_div.clear()
        details_div.append(new_details_soup)
    print(minify(str(description_template_soup)))
    return minify(str(description_template_soup))


def main():
    addtional = "<p>Nueva descripción</p><br data-mce-fragment=true>Otro texto más."
    product = pd.read_csv("test-product.csv", encoding="UTF-8", sep=';')
    product["SKU"] = "ABC123XYZ"
    product["Descripción"] = product.apply(
        lambda row: generate_description(row, additional_text=addtional), axis=1)

    product.to_csv("test-product-output.csv",
                   encoding="UTF-8", index=False)


if __name__ == "__main__":
    main()
