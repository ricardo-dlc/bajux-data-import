import pandas as pd
from tqdm import tqdm
from product import generate_description, parse_scientific_notation, add_extra_data


def main():
    filename = "afinacion.csv"
    products = pd.read_csv(filename, encoding="UTF-8", sep=',')

    extra_html = """<div class="extra-details mt-4">
        <div class="banner bajux-tuning-banner-1 mb-4"></div>
        <div class="banner bajux-tuning-banner-2 mb-4"></div>
        <div class="banner bajux-tuning-banner-3 mb-4"></div>
        <div class="banner bajux-tuning-banner-4"></div>
    </div>"""

    # Check data type of 'Costo' column
    # print("Data type of 'Costo' column:", products['Precio'].dtype)

    # Backup 'Precio'
    products['PrecioAnterior'] = products['Precio']
    # Convert 'Precio' column to numeric
    products['Precio'] = pd.to_numeric(
        products['Precio'].str.replace(',', ''), errors='coerce')

    # Check data type of 'Costo' column
    # print("Data type of 'Costo' column:", products['Precio'].dtype)

    # # Check for unexpected non-numeric values
    # non_numeric_values = products[~products['Precio'].apply(lambda x: isinstance(x, (int, float)))]
    # print("Non-numeric values in 'Precio' column:", non_numeric_values)

    # print(products[(products["Precio"].notna())]["Precio"])
    # print(products[(products["Precio"].isna())]["Precio"])
    tqdm.pandas()
    products["Costo"] = products["Precio"]
    products["Precio"] = products["Precio"] * 1.10
    products["MPN (Número de pieza del fabricante)"] = products["SKU"]
    products["Envío sin cargo"] = products["Precio"].progress_apply(
        lambda x: "SÍ" if x > 999.00 else "NO")
    products["Código de barras"] = products["Código de barras"].progress_apply(
        parse_scientific_notation)
    products["Descripción"] = products.progress_apply(
        lambda row: generate_description(row), axis=1)
    products["Descripción"] = products.progress_apply(
        lambda row: add_extra_data(row["Descripción"], extra_html), axis=1)
    products.to_csv("output-"+filename, encoding="UTF-8", index=False)


if __name__ == "__main__":
    main()
