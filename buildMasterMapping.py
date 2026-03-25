import pandas as pd
import os
import re

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = r"C:\Rons Documents\Rons Personal Stuff\20961 Skyler Road (Florida)\Invoices"

INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

HOME_DEPOT_FILE = os.path.join(INPUT_DIR, "1.HomeDepotPurchases.csv")
AMAZON_FILE = os.path.join(INPUT_DIR, "3.AmazonOrderHistory.csv")
MASTERCARD_FILE = os.path.join(INPUT_DIR, "4.BMOMastercardTransactions.csv")
MAPPING_FILE = os.path.join(INPUT_DIR, "6.Mapping.csv")

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "master_mapping.csv")


# --------------------------------------------------
# Normalize text
# --------------------------------------------------

def normalize(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# --------------------------------------------------
# Load mapping items
# --------------------------------------------------

def load_mapping():

    print("Loading Mapping File...")

    df = pd.read_csv(MAPPING_FILE)

    items = []

    for _, row in df.iterrows():

        item = str(row[0])

        words = set(normalize(item).split())

        items.append({
            "item": item,
            "words": words
        })

    print(f"Loaded {len(items)} mapping items")

    return items


# --------------------------------------------------
# Match item
# --------------------------------------------------

def match_item(text, items):

    words = set(normalize(text).split())

    best_item = "Uncategorized"
    best_score = 0

    for item in items:

        overlap = words.intersection(item["words"])

        score = len(overlap)

        if score > best_score:
            best_score = score
            best_item = item["item"]

    return best_item, best_score


# --------------------------------------------------
# Load Home Depot
# --------------------------------------------------

def load_home_depot():

    print("Loading Home Depot...")

    df = pd.read_csv(HOME_DEPOT_FILE)
    df.columns = df.columns.str.strip()

    df["Description"] = (
        df["Department Name"].astype(str) + " " +
        df["Class Name"].astype(str) + " " +
        df["Subclass Name"].astype(str) + " " +
        df["SKU Description"].astype(str)
    )

    df["Vendor"] = "Home Depot"

    return df[["Vendor", "Description"]]


# --------------------------------------------------
# Load Amazon
# --------------------------------------------------

def load_amazon():

    print("Loading Amazon...")

    df = pd.read_csv(AMAZON_FILE)
    df.columns = df.columns.str.strip()

    df["Vendor"] = "Amazon"
    df["Description"] = df["Product Name"]

    return df[["Vendor", "Description"]]


# --------------------------------------------------
# Load Mastercard
# --------------------------------------------------

def load_mastercard():

    print("Loading Mastercard...")

    df = pd.read_csv(MASTERCARD_FILE)
    df.columns = df.columns.str.strip()

    df["Vendor"] = df["MERCHANT"]
    df["Description"] = df["MERCHANT"]

    return df[["Vendor", "Description"]]


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    items = load_mapping()

    hd = load_home_depot()
    amz = load_amazon()
    mc = load_mastercard()

    df = pd.concat([hd, amz, mc])

    df = df.drop_duplicates()

    print(f"Unique rows: {len(df)}")

    suggestions = []

    for i, row in df.iterrows():

        item, score = match_item(row["Description"], items)

        suggestions.append({
            "ID": i,
            "Source": "",
            "Vendor": row["Vendor"],
            "Description": row["Description"],
            "SuggestedItem": item,
            "Confidence": score
        })

    result = pd.DataFrame(suggestions)

    result.to_csv(OUTPUT_FILE, index=False)

    print("master_mapping.csv created")


if __name__ == "__main__":
    main()