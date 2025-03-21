import pandas as pd
import re

def clean_numeric(series):
    
    def convert_value(x):
        if pd.isna(x):
            return pd.NA

        # Removing 'US ', '$', and commas
        x = re.sub(r'^(US\s*)?\$', '', str(x)).replace(',', '').strip()

        try:
            #turning values to floats
            return float(x)
        except ValueError:
            return pd.NA

    return series.apply(convert_value)


def clean_data():
    df = pd.read_csv("ebay_tech_deals.csv", dtype=str)

    df = df.dropna(subset=['Title'])

    #cleaning price and original price columns
    df['Price'] = clean_numeric(df['Price'])
    df['Original Price'] = clean_numeric(df['Original Price'])

    #replacing missing original prices with prices
    df['Original Price'] = df['Original Price'].fillna(df['Price'])

    # Cleaning shipping
    df['Shipping'] = df['Shipping'].replace(['N/A', '', None], 'Shipping info unavailable').str.strip()

    # discount percentage
    df['discount_percentage'] = (
        ((df['Original Price'] - df['Price']) / df['Original Price']) * 100
    ).round(2)

    df.to_csv("cleaned_ebay_deals.csv", index=False)


if __name__ == "__main__":
    clean_data()
