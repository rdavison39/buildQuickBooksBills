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
ITEM_FILE = os.path.join(INPUT_DIR, "2.QuickBooksItemList.csv")
AMAZON_FILE = os.path.join(INPUT_DIR, "3.AmazonOrderHistory.csv")
MASTERCARD_FILE = os.path.join(INPUT_DIR, "4.BMOMastercardTransactions.csv")

CUSTOMER_JOB = "20961 Skyler Road"


# --------------------------------------------------
# Text normalization
# --------------------------------------------------

def normalize(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# --------------------------------------------------
# Load QuickBooks Items
# --------------------------------------------------

def load_items():

    print("\nLoading QuickBooks Items...")

    df = pd.read_csv(ITEM_FILE)
    df.columns = df.columns.str.strip()

    items = []

    current_item = None

    for _, row in df.iterrows():

        if str(row.iloc[0]) == "Item Name/Number":
            current_item = str(row.iloc[1])

        if str(row.iloc[0]) == "Description":

            description = str(row.iloc[1])

            search = normalize(current_item + " " + description)

            words = set(search.split())

            items.append({
                "item": current_item,
                "words": words
            })

    print(f"Loaded {len(items)} items")

    return items


# --------------------------------------------------
# Match item
# --------------------------------------------------

def match_item(text, items):

    text_norm = normalize(text)
    text_words = set(text_norm.split())

    best_match = None
    best_score = 0

    for item in items:

        overlap = text_words.intersection(item["words"])
        score = len(overlap)

        if score > best_score:
            best_score = score
            best_match = item["item"]

    if best_match:
        return best_match, "Word Match"

    return "Uncategorized", "No Match"


# --------------------------------------------------
# Home Depot
# --------------------------------------------------

def load_home_depot(items):

    print("\nLoading Home Depot...")

    df = pd.read_csv(HOME_DEPOT_FILE)
    df.columns = df.columns.str.strip()

    print(f"Home Depot rows: {len(df)}")
    print("Columns:", df.columns.tolist())

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Description"] = (
        df["Department Name"].astype(str) + " " +
        df["Class Name"].astype(str) + " " +
        df["Subclass Name"].astype(str) + " " +
        df["SKU Description"].astype(str)
    )

    mapped = df["Description"].apply(lambda x: match_item(x, items))

    df["Item"] = mapped.apply(lambda x: x[0])
    df["MappingReason"] = mapped.apply(lambda x: x[1])

    df["Vendor"] = "Home Depot"

    # Clean Amount
    df["Amount"] = (
        df["Extended Retail (before discount)"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    print("Home Depot Amount Sample:")
    print(df["Amount"].head())

    # remove negative / zero
    df = df[df["Amount"] > 0]

    df["BillID"] = df["Transaction ID"]
    df["Source"] = "HomeDepot"

    mapped_count = (df["Item"] != "Uncategorized").sum()

    print(f"Home Depot mapped: {mapped_count} / {len(df)}")

    return df


# --------------------------------------------------
# Amazon
# --------------------------------------------------

def load_amazon(items):

    print("\nLoading Amazon...")

    df = pd.read_csv(AMAZON_FILE)
    df.columns = df.columns.str.strip()

    print(f"Amazon rows: {len(df)}")

    df["Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    df["Description"] = df["Product Name"]

    df["Amount"] = pd.to_numeric(df["Total Amount"], errors="coerce")

    df = df[df["Amount"] > 0]

    mapped = df["Description"].apply(lambda x: match_item(x, items))

    df["Item"] = mapped.apply(lambda x: x[0])
    df["MappingReason"] = mapped.apply(lambda x: x[1])

    df["Vendor"] = "Amazon"
    df["BillID"] = df["Order ID"]
    df["Source"] = "Amazon"

    mapped_count = (df["Item"] != "Uncategorized").sum()

    print(f"Amazon mapped: {mapped_count} / {len(df)}")

    return df


# --------------------------------------------------
# Mastercard
# --------------------------------------------------

def load_mastercard(items):

    print("\nLoading Mastercard...")

    df = pd.read_csv(MASTERCARD_FILE)
    df.columns = df.columns.str.strip()

    print(f"Mastercard rows: {len(df)}")

    df["Date"] = pd.to_datetime(df["TRANSACTION DATE"], errors="coerce")

    df["Description"] = df["MERCHANT"]

    df["Amount"] = pd.to_numeric(df["BILLING AMOUNT"], errors="coerce")

    df = df[df["Amount"] > 0]

    mapped = df["Description"].apply(lambda x: match_item(x, items))

    df["Item"] = mapped.apply(lambda x: x[0])
    df["MappingReason"] = mapped.apply(lambda x: x[1])

    df["Vendor"] = df["MERCHANT"]
    df["BillID"] = ["MC-" + str(i) for i in range(len(df))]
    df["Source"] = "Mastercard"

    df = df[~df["Vendor"].str.contains("Amazon", case=False)]
    df = df[~df["Vendor"].str.contains("Home Depot", case=False)]

    mapped_count = (df["Item"] != "Uncategorized").sum()

    print(f"Mastercard mapped: {mapped_count} / {len(df)}")

    return df


# --------------------------------------------------
# Combine
# --------------------------------------------------

def combine():

    items = load_items()

    hd = load_home_depot(items)
    amz = load_amazon(items)
    mc = load_mastercard(items)

    df = pd.concat([hd, amz, mc])

    print(f"\nTotal combined rows: {len(df)}")

    return df


# --------------------------------------------------
# Review
# --------------------------------------------------

def write_review(df):

    print("\nWriting review file...")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    review = os.path.join(OUTPUT_DIR, "review_bills.csv")

    review_df = df[
        [
            "Date",
            "Vendor",
            "Item",
            "Description",
            "Amount",
            "BillID",
            "Source"
        ]
    ].copy()

    review_df["CustomerJob"] = CUSTOMER_JOB

    review_df = review_df[
        [
            "Date",
            "Vendor",
            "Item",
            "Description",
            "Amount",
            "CustomerJob",
            "BillID",
            "Source"
        ]
    ]

    review_df.to_csv(review, index=False)


# --------------------------------------------------
# IIF
# --------------------------------------------------

def write_iif(df):

    print("\nWriting IIF...")

    iif = os.path.join(OUTPUT_DIR, "quickbooks_bills.iif")

    with open(iif, "w", encoding="utf-8") as f:

        f.write("!TRNS\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\n")
        f.write("!SPL\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\tMEMO\tCLASS\n")
        f.write("!ENDTRNS\n")

        for bill, group in df.groupby("BillID"):

            total = group["Amount"].sum()

            vendor = group.iloc[0]["Vendor"]
            date = group.iloc[0]["Date"].strftime("%m/%d/%Y")

            f.write(
                f"TRNS\tBILL\t{date}\tAccounts Payable\t{vendor}\t-{total}\n"
            )

            for _, r in group.iterrows():

                desc = str(r["Description"]).encode("ascii", "ignore").decode()

                f.write(
                    f"SPL\tBILL\t{date}\t{r['Item']}\t{vendor}\t{r['Amount']}\t{bill}\t{desc}\t{CUSTOMER_JOB}\n"
                )

            f.write("ENDTRNS\n")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("\n----------------------------------------")
    print("QuickBooks Bill Builder")
    print("----------------------------------------")

    df = combine()

    write_review(df)
    write_iif(df)

    print("\nDone.")


if __name__ == "__main__":
    main()