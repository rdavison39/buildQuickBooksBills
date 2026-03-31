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
MAPPING_FILE = os.path.join(OUTPUT_DIR, "master_mapping.csv")

CUSTOMER_JOB = "20961 Skyler"
DEFAULT_SPL_ACCOUNT = "Ask My Accountant"

# Vendors to ignore from Mastercard
IGNORE_MASTERCARD_VENDORS = [
    "AMAZON",
    "HOME DEPOT"
]

# --------------------------------------------------
# Clean Text
# --------------------------------------------------

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text)
    text = text.replace("\t", " ")
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# --------------------------------------------------
# Clean Money
# --------------------------------------------------

def clean_money(series):

    return pd.to_numeric(
        series.astype(str)
        .replace(r'[\$,]', '', regex=True)
        .replace(r'\((.*)\)', r'-\1', regex=True),
        errors="coerce"
    )

# --------------------------------------------------
# Load Mapping
# --------------------------------------------------

def load_mapping():

    print("Loading master mapping...")

    df = pd.read_csv(MAPPING_FILE)
    df = df.dropna(how="all")

    mapping = dict(zip(df["MappingKey"], df["SuggestedItem"]))

    print(f"Loaded {len(mapping)} mappings")

    return mapping

# --------------------------------------------------
# Home Depot
# --------------------------------------------------

def load_home_depot():

    print("Loading Home Depot...")

    df = pd.read_csv(HOME_DEPOT_FILE)
    df = df.dropna(how="all")

    df.columns = df.columns.str.strip()

    df["Source"] = "Home Depot"
    df["Vendor"] = "Home Depot"

    df["Description"] = (
        df["Department Name"].fillna("") + " " +
        df["Class Name"].fillna("") + " " +
        df["Subclass Name"].fillna("") + " " +
        df["SKU Description"].fillna("")
    )

    df["Description"] = df["Description"].apply(clean_text)

    df["MappingKey"] = (
        "HD-" +
        df["Transaction ID"].astype(str) + "-" +
        df["SKU Number"].astype(str)
    )

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    amount_col = None
    for col in df.columns:
        if "extended" in col.lower():
            amount_col = col
            break

    print(f"Using amount column: {amount_col}")

    df["Amount"] = clean_money(df[amount_col])

    df = df[df["Amount"] > 0]

    df["BillID"] = df["Transaction ID"]

    return df

# --------------------------------------------------
# Amazon
# --------------------------------------------------

def load_amazon():

    print("Loading Amazon...")

    df = pd.read_csv(AMAZON_FILE)
    df = df.dropna(how="all")

    df.columns = df.columns.str.strip()

    df["Source"] = "Amazon"
    df["Vendor"] = "Amazon"

    df["Description"] = df["Product Name"].apply(clean_text)

    df["MappingKey"] = (
        "AMZ-" +
        df["Order ID"].astype(str) + "-" +
        df.index.astype(str)
    )

    df["Date"] = pd.to_datetime(
        df["Order Date"],
        errors="coerce"
    ).dt.tz_localize(None)

    df["Amount"] = clean_money(df["Total Amount"])

    df = df[df["Amount"] > 0]

    df["BillID"] = df["Order ID"]

    return df

# --------------------------------------------------
# Mastercard
# --------------------------------------------------

def load_mastercard():

    print("Loading Mastercard...")

    df = pd.read_csv(MASTERCARD_FILE)
    df = df.dropna(how="all")

    df.columns = df.columns.str.strip()

    df["Vendor"] = df["MERCHANT"]

    before = len(df)

    for vendor in IGNORE_MASTERCARD_VENDORS:
        df = df[~df["Vendor"].str.contains(vendor, case=False, na=False)]

    removed = before - len(df)

    print(f"Removed {removed} Mastercard rows (ignored vendors)")

    df["Source"] = "Mastercard"
    df["Description"] = df["MERCHANT"]

    df["MappingKey"] = (
        "MC-" +
        df["TRANSACTION DATE"].astype(str) + "-" +
        df["BILLING AMOUNT"].astype(str) + "-" +
        df["MERCHANT"].astype(str)
    )

    df["Date"] = pd.to_datetime(
        df["TRANSACTION DATE"].astype(str).str.strip(),
        errors="coerce"
    )

    df["Amount"] = clean_money(df["BILLING AMOUNT"])
    df["Amount"] = df["Amount"].abs()

    df = df[df["Amount"] > 0]

    df["BillID"] = ["MC-" + str(i) for i in range(len(df))]

    return df

# --------------------------------------------------
# Combine
# --------------------------------------------------

def combine():

    mapping = load_mapping()

    hd = load_home_depot()
    amz = load_amazon()
    mc = load_mastercard()

    df = pd.concat([hd, amz, mc])

    df["Item"] = df["MappingKey"].map(mapping)
    df["Item"] = df["Item"].fillna("Uncategorized")

    df = df.dropna(subset=["Date"])

    df["CustomerJob"] = CUSTOMER_JOB
    df["Approved"] = ""

    return df

# --------------------------------------------------
# Review File
# --------------------------------------------------

def write_review(df):

    review_file = os.path.join(OUTPUT_DIR, "review_bills.csv")

    review = df.copy()

    review = review[
        [
            "Approved",
            "Source",
            "Vendor",
            "Date",
            "BillID",
            "Item",
            "Description",
            "Amount",
            "CustomerJob"
        ]
    ]

    review = review.sort_values(["Vendor", "Date"])

    review.to_csv(review_file, index=False)

    print(f"review_bills.csv created ({len(review)} rows)")

# --------------------------------------------------
# Write IIF  (NEW)
# --------------------------------------------------

def write_iif(df):

    print("Building QuickBooks IIF...")

    iif_file = os.path.join(OUTPUT_DIR, "quickbooks_bills.iif")

    df = df.sort_values(["Vendor", "BillID", "Date"])

    with open(iif_file, "w", encoding="utf-8") as f:

        f.write("!TRNS\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\n")
        f.write("!SPL\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\tMEMO\tINVITEM\tQNTY\tPRICE\tCLASS\n")
        f.write("!ENDTRNS\n")

        grouped = df.groupby(["Vendor", "BillID"])

        for (vendor, bill), g in grouped:

            date = g["Date"].iloc[0].strftime("%m/%d/%Y")

            total = g["Amount"].sum()

            f.write(
                f"TRNS\tBILL\t{date}\tAccounts Payable\t{vendor}\t{-total:.2f}\t{bill}\n"
            )

            for _, row in g.iterrows():

                desc = clean_text(row["Description"])

                f.write(
                    f"SPL\tBILL\t{date}\t\t{vendor}\t{row['Amount']:.2f}\t{bill}\t"
                    f"{desc}\t{row['Item']}\t1\t{row['Amount']:.2f}\t{row['CustomerJob']}\n"
                )

            f.write("ENDTRNS\n")

    print("quickbooks_bills.iif created")

# --------------------------------------------------
# Stats
# --------------------------------------------------

def print_stats(df):

    print("\n----------------------------------------")
    print("Summary Statistics")
    print("----------------------------------------")

    for source in df["Source"].unique():

        sub = df[df["Source"] == source]

        items = len(sub)
        bills = sub["BillID"].nunique()
        matched = (sub["Item"] != "Uncategorized").sum()
        total = sub["Amount"].sum()

        print(f"\n{source}")
        print(f"  Line Items : {items:,}")
        print(f"  Bills      : {bills:,}")
        print(f"  Matched    : {matched:,}")
        print(f"  Total      : ${total:,.2f}")

    print("\n----------------------------------------")
    print(f"Grand Total: ${df['Amount'].sum():,.2f}")
    print("----------------------------------------")

# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("\n----------------------------------------")
    print("Build QuickBooks Bills")
    print("----------------------------------------")

    df = combine()

    write_review(df)

    write_iif(df)   # <-- Added

    print_stats(df)

    print("\nDone.")

if __name__ == "__main__":
    main()