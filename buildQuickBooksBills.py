import pandas as pd
import os
import glob
from datetime import datetime, timedelta

INPUT_DIR = "input"
OUTPUT_DIR = "output"

HOME_DEPOT_FILE = os.path.join(INPUT_DIR, "1.HomeDepotPurchases.csv")
AMAZON_FILE = os.path.join(INPUT_DIR, "3.AmazonOrderHistory.csv")
ITEM_FILE = os.path.join(INPUT_DIR, "QuickBooksItemList.csv")
VENDOR_FILE = os.path.join(INPUT_DIR, "VendorListFromQuickbooks.csv")

MASTERCARD_DIR = os.path.join(INPUT_DIR, "mastercard")

CUSTOMER_JOB = "20961 Skyler Road"

# --------------------------------------------------
# Vendor normalization
# --------------------------------------------------

def normalize_vendor(v):
    v = str(v).upper()

    if "AMZN" in v or "AMAZON" in v:
        return "Amazon"

    if "HOME DEPOT" in v or "HD" in v:
        return "Home Depot"

    return v.title()

# --------------------------------------------------
# Categorization Rules
# --------------------------------------------------

CATEGORY_RULES = {
    "Lumber": ["2x", "stud", "plywood", "lumber"],
    "Paint": ["paint", "primer"],
    "Electrical": ["wire", "switch", "outlet"],
    "Plumbing": ["pipe", "pvc", "valve"],
    "Hardware": ["nail", "screw", "bolt"],
    "Tools": ["drill", "saw", "tool"]
}

def categorize(desc):
    d = str(desc).lower()

    for cat, keywords in CATEGORY_RULES.items():
        for k in keywords:
            if k in d:
                return cat

    return "Uncategorized"

# --------------------------------------------------
# Load Home Depot
# --------------------------------------------------

def load_home_depot():

    df = pd.read_csv(HOME_DEPOT_FILE)

    df["Vendor"] = "Home Depot"
    df["Source"] = "HomeDepot"
    df["Item"] = df["SKU Description"].apply(categorize)
    df["Description"] = df["SKU Description"]
    df["BillID"] = df["Transaction ID"]

    df["Date"] = pd.to_datetime(df["Date"])

    df = df.rename(columns={"Extended Price": "Amount"})

    df = df[df["Amount"] > 0]

    return df[[
        "BillID",
        "Vendor",
        "Date",
        "Item",
        "Description",
        "Amount",
        "Source"
    ]]

# --------------------------------------------------
# Load Amazon
# --------------------------------------------------

def load_amazon():

    df = pd.read_csv(AMAZON_FILE)

    df["Vendor"] = "Amazon"
    df["Source"] = "Amazon"

    df["Item"] = df["Title"].apply(categorize)
    df["Description"] = df["Title"]

    df["BillID"] = df["Order ID"]

    df["Date"] = pd.to_datetime(df["Order Date"])

    df = df.rename(columns={"Item Total": "Amount"})

    df = df[df["Amount"] > 0]

    return df[[
        "BillID",
        "Vendor",
        "Date",
        "Item",
        "Description",
        "Amount",
        "Source"
    ]]

# --------------------------------------------------
# Load Mastercard
# --------------------------------------------------

def load_mastercard():

    files = glob.glob(os.path.join(MASTERCARD_DIR, "*.csv"))

    dfs = []

    for f in files:
        df = pd.read_csv(f)
        dfs.append(df)

    df = pd.concat(dfs)

    df["Vendor"] = df["Description"].apply(normalize_vendor)
    df["Source"] = "Mastercard"

    df["Date"] = pd.to_datetime(df["Transaction Date"])

    df["Amount"] = df["Amount"].astype(float)

    df = df[df["Amount"] > 0]

    df = df[~df["Vendor"].str.contains("Amazon", case=False)]
    df = df[~df["Vendor"].str.contains("Home Depot", case=False)]

    df["Item"] = df["Description"].apply(categorize)
    df["Description"] = df["Description"]

    df["BillID"] = ["MC-" + str(i) for i in range(len(df))]

    return df[[
        "BillID",
        "Vendor",
        "Date",
        "Item",
        "Description",
        "Amount",
        "Source"
    ]]

# --------------------------------------------------
# Combine All
# --------------------------------------------------

def combine():

    hd = load_home_depot()
    amz = load_amazon()
    mc = load_mastercard()

    df = pd.concat([hd, amz, mc])

    return df

# --------------------------------------------------
# Write Review CSV
# --------------------------------------------------

def write_review(df):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    review_file = os.path.join(OUTPUT_DIR, "review_bills.csv")

    df = df.sort_values(["Date", "Vendor"])

    df.to_csv(review_file, index=False)

# --------------------------------------------------
# Write IIF
# --------------------------------------------------

def write_iif(df):

    iif_file = os.path.join(OUTPUT_DIR, "quickbooks_bills.iif")

    with open(iif_file, "w") as f:

        f.write("!TRNS\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\n")
        f.write("!SPL\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\tMEMO\tCLASS\n")
        f.write("!ENDTRNS\n")

        for bill_id, group in df.groupby("BillID"):

            total = group["Amount"].sum()

            vendor = group.iloc[0]["Vendor"]
            date = group.iloc[0]["Date"].strftime("%m/%d/%Y")

            f.write(
                f"TRNS\tBILL\t{date}\tAccounts Payable\t{vendor}\t-{total}\n"
            )

            for _, row in group.iterrows():

                item = row["Item"]
                desc = row["Description"]
                amt = row["Amount"]

                f.write(
                    f"SPL\tBILL\t{date}\t{item}\t{vendor}\t{amt}\t{bill_id}\t{desc}\t{CUSTOMER_JOB}\n"
                )

            f.write("ENDTRNS\n")

# --------------------------------------------------
# Summary
# --------------------------------------------------

def write_summary(df):

    summary = df.groupby("Item")["Amount"].sum().reset_index()

    summary_file = os.path.join(OUTPUT_DIR, "category_summary.csv")

    summary.to_csv(summary_file, index=False)

# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    df = combine()

    write_review(df)
    write_iif(df)
    write_summary(df)

    print("Done.")
    print("Files created:")
    print(" - review_bills.csv")
    print(" - quickbooks_bills.iif")
    print(" - category_summary.csv")

if __name__ == "__main__":
    main()