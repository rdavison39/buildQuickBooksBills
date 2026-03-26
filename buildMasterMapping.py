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

    # remove numbers
    text = re.sub(r'\d+', ' ', text)

    # remove punctuation
    text = re.sub(r'[^a-z ]', ' ', text)

    # collapse spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# --------------------------------------------------
# Load Mapping
# --------------------------------------------------

def load_mapping():

    print("Loading mapping file...")

    df = pd.read_csv(MAPPING_FILE)
    df.columns = df.columns.str.strip()

    items = []

    for _, row in df.iterrows():

        item = str(row.iloc[0])

        # Split hierarchy
        parts = item.split(":")

        parts = [normalize(p) for p in parts]

        parts.reverse()  # most specific first

        items.append({
            "item": item,
            "parts": parts
        })

    print(f"Loaded {len(items)} mapping items")

    return items


# --------------------------------------------------
# Match item
# --------------------------------------------------

def match_item(text, items):

    text_words = set(normalize(text).split())

    best_item = "Uncategorized"
    best_score = 0

    for item in items:

        score = 0

        for i, part in enumerate(item["parts"]):

            part_words = set(part.split())

            overlap = text_words.intersection(part_words)

            if overlap:

                # weighted scoring
                if i == 0:
                    score += 5 * len(overlap)
                elif i == 1:
                    score += 3 * len(overlap)
                else:
                    score += 1 * len(overlap)

        if score > best_score:
            best_score = score
            best_item = item["item"]

    return best_item, best_score

# --------------------------------------------------
# Home Depot
# --------------------------------------------------

def load_home_depot():

    print("Loading Home Depot...")

    df = pd.read_csv(HOME_DEPOT_FILE)
    df.columns = df.columns.str.strip()

    df["Vendor"] = "Home Depot"

    df["Description"] = (
        df["Department Name"].fillna("").astype(str) + " " +
        df["Class Name"].fillna("").astype(str) + " " +
        df["Subclass Name"].fillna("").astype(str) + " " +
        df["SKU Description"].fillna("").astype(str)
    )

    return df[["Vendor", "Description"]]


# --------------------------------------------------
# Amazon
# --------------------------------------------------

def load_amazon():

    print("Loading Amazon...")

    df = pd.read_csv(AMAZON_FILE)
    df.columns = df.columns.str.strip()

    df["Vendor"] = "Amazon"
    df["Description"] = df["Product Name"].fillna("")

    return df[["Vendor", "Description"]]


# --------------------------------------------------
# Mastercard
# --------------------------------------------------

def load_mastercard():

    print("Loading Mastercard...")

    df = pd.read_csv(MASTERCARD_FILE)
    df.columns = df.columns.str.strip()

    df["Vendor"] = df["MERCHANT"]
    df["Description"] = df["MERCHANT"].fillna("")

    return df[["Vendor", "Description"]]


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("")
    print("------------------------------------")
    print("Building Master Mapping")
    print("------------------------------------")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    items = load_mapping()

    hd = load_home_depot()
    amz = load_amazon()
    mc = load_mastercard()

    df = pd.concat([hd, amz, mc])

    df = df.drop_duplicates()

    print(f"Unique descriptions: {len(df)}")

    results = []

    for i, row in df.iterrows():

        suggested, score = match_item(row["Description"], items)

        results.append({
            "ID": i,
            "Vendor": row["Vendor"],
            "Description": row["Description"],
            "SuggestedItem": suggested,
            "Confidence": score
        })

    result = pd.DataFrame(results)

    result.to_csv(OUTPUT_FILE, index=False)

    print("")
    print("master_mapping.csv created")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()