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
# Stop Words
# --------------------------------------------------

STOP_WORDS = {
    "and","or","the","for","with","in","on","at",
    "to","from","by","of","a","an"
}

# --------------------------------------------------
# Normalize
# --------------------------------------------------

def normalize(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# --------------------------------------------------
# Load Mapping List
# --------------------------------------------------

def load_mapping():

    print("Loading mapping file...")

    df = pd.read_csv(MAPPING_FILE)
    df.columns = df.columns.str.strip()

    items = []

    for _, row in df.iterrows():

        item = str(row.iloc[0])

        parts = item.split(":")

        clean = []

        for p in parts:

            p = normalize(p)

            if "build phase" in p:
                continue

            clean.append(p)

        clean.reverse()

        items.append({
            "item": item,
            "parts": clean
        })

    print(f"Loaded {len(items)} mapping items")

    return items


# --------------------------------------------------
# Match Item
# --------------------------------------------------

def match_item(text, items):

    text_words = set(
        w for w in normalize(text).split()
        if w not in STOP_WORDS
    )

    best_item = "Uncategorized"
    best_score = 0

    for item in items:

        score = 0

        for i, part in enumerate(item["parts"]):

            part_words = set(
                w for w in part.split()
                if w not in STOP_WORDS
            )

            overlap = text_words.intersection(part_words)

            if overlap:

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

def load_home_depot(items):

    print("Loading Home Depot...")

    df = pd.read_csv(HOME_DEPOT_FILE)
    df = df.dropna(how="all")   # <-- Added

    df.columns = df.columns.str.strip()

    df["Vendor"] = "Home Depot"

    df["Description"] = (
        df["Department Name"].fillna("") + " " +
        df["Class Name"].fillna("") + " " +
        df["Subclass Name"].fillna("") + " " +
        df["SKU Description"].fillna("")
    )

    df["MappingKey"] = (
        "HD-" +
        df["Transaction ID"].astype(str) + "-" +
        df["SKU Number"].astype(str)
    )

    mapped = df["Description"].apply(lambda x: match_item(x, items))

    df["SuggestedItem"] = mapped.apply(lambda x: x[0])
    df["Confidence"] = mapped.apply(lambda x: x[1])

    df["Source"] = "HomeDepot"

    return df[
        [
            "MappingKey",
            "Source",
            "Vendor",
            "Description",
            "SuggestedItem",
            "Confidence"
        ]
    ]


# --------------------------------------------------
# Amazon
# --------------------------------------------------

def load_amazon(items):

    print("Loading Amazon...")

    df = pd.read_csv(AMAZON_FILE)
    df = df.dropna(how="all")   # <-- Added

    df.columns = df.columns.str.strip()

    df["Vendor"] = "Amazon"
    df["Description"] = df["Product Name"]

    df["MappingKey"] = (
        "AMZ-" +
        df["Order ID"].astype(str) + "-" +
        df.index.astype(str)
    )

    mapped = df["Description"].apply(lambda x: match_item(x, items))

    df["SuggestedItem"] = mapped.apply(lambda x: x[0])
    df["Confidence"] = mapped.apply(lambda x: x[1])

    df["Source"] = "Amazon"

    return df[
        [
            "MappingKey",
            "Source",
            "Vendor",
            "Description",
            "SuggestedItem",
            "Confidence"
        ]
    ]


# --------------------------------------------------
# Mastercard
# --------------------------------------------------

def load_mastercard(items):

    print("Loading Mastercard...")

    df = pd.read_csv(MASTERCARD_FILE)
    df = df.dropna(how="all")   # <-- Added

    df.columns = df.columns.str.strip()

    df["Vendor"] = df["MERCHANT"]
    df["Description"] = df["MERCHANT"]

    df["MappingKey"] = (
        "MC-" +
        df["TRANSACTION DATE"].astype(str) + "-" +
        df["BILLING AMOUNT"].astype(str) + "-" +
        df["MERCHANT"].astype(str)
    )

    mapped = df["Description"].apply(lambda x: match_item(x, items))

    df["SuggestedItem"] = mapped.apply(lambda x: x[0])
    df["Confidence"] = mapped.apply(lambda x: x[1])

    df["Source"] = "Mastercard"

    return df[
        [
            "MappingKey",
            "Source",
            "Vendor",
            "Description",
            "SuggestedItem",
            "Confidence"
        ]
    ]


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("\n----------------------------------------")
    print("Build Master Mapping")
    print("----------------------------------------")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    items = load_mapping()

    hd = load_home_depot(items)
    amz = load_amazon(items)
    mc = load_mastercard(items)

    df = pd.concat([hd, amz, mc])

    df = df.drop_duplicates(subset=["MappingKey"])

    df.to_csv(OUTPUT_FILE, index=False)

    print("")
    print("master_mapping.csv created")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    main()