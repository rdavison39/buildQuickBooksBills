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

CUSTOMER_JOB = "20961 Skyler Road"


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

    mapping = dict(zip(df["MappingKey"], df["SuggestedItem"]))

    print(f"Loaded {len(mapping)} mappings")

    return mapping


# --------------------------------------------------
# Home Depot
# --------------------------------------------------

def load_home_depot():

    print("Loading Home Depot...")

    df = pd.read_csv(HOME_DEPOT_FILE)
    df.columns = df.columns.str.strip()

    df["Source"] = "Home Depot"
    df["Vendor"] = "Home Depot"

    df["Description"] = (
        df.get("Department Name","").fillna("").astype(str) + " " +
        df.get("Class Name","").fillna("").astype(str) + " " +
        df.get("Subclass Name","").fillna("").astype(str) + " " +
        df.get("SKU Description","").fillna("").astype(str)
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
        if "extended" in col.lower() and "retail" in col.lower():
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
    df.columns = df.columns.str.strip()

    df["Source"] = "Amazon"
    df["Vendor"] = "Amazon"

    df["Description"] = df["Product Name"].apply(clean_text)

    df["MappingKey"] = (
        "AMZ-" +
        df["Order ID"].astype(str) + "-" +
        df.index.astype(str)
    )

    df["Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

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
    df.columns = df.columns.str.strip()

    df["Source"] = "Mastercard"
    df["Vendor"] = df["MERCHANT"].apply(clean_text)

    df["Description"] = df["MERCHANT"].apply(clean_text)

    df["MappingKey"] = (
        "MC-" +
        df["TRANSACTION DATE"].astype(str) + "-" +
        df["BILLING AMOUNT"].astype(str) + "-" +
        df["MERCHANT"].astype(str)
    )

    df["Date"] = pd.to_datetime(df["TRANSACTION DATE"], errors="coerce")

    df["Amount"] = clean_money(df["BILLING AMOUNT"])

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

    return df


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
# Write IIF (Bulletproof)
# --------------------------------------------------

def write_iif(df):

    iif = os.path.join(OUTPUT_DIR, "quickbooks_bills.iif")

    with open(iif, "w", encoding="utf-8") as f:

        f.write("!TRNS\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\n")
        f.write("!SPL\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\tMEMO\tCLASS\n")
        f.write("!ENDTRNS\n")

        for bill, group in df.groupby("BillID"):

            total = round(group["Amount"].sum(), 2)

            vendor = clean_text(group.iloc[0]["Vendor"])

            date = group.iloc[0]["Date"].strftime("%m/%d/%Y")

            f.write(
                f"TRNS\tBILL\t{date}\tAccounts Payable\t{vendor}\t-{total}\t{bill}\n"
            )

            for _, r in group.iterrows():

                desc = clean_text(r["Description"])

                amount = round(r["Amount"], 2)

                item = clean_text(r["Item"])

                f.write(
                    f"SPL\tBILL\t{date}\t{item}\t{vendor}\t{amount}\t{bill}\t{desc}\t{CUSTOMER_JOB}\n"
                )

            f.write("ENDTRNS\n")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("\n----------------------------------------")
    print("Build QuickBooks Bills")
    print("----------------------------------------")

    df = combine()

    write_iif(df)

    print_stats(df)

    print("\nDone.")


if __name__ == "__main__":
    main()