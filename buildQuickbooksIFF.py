import pandas as pd
import os
import re

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = r"C:\Rons Documents\Rons Personal Stuff\20961 Skyler Road (Florida)\Invoices"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

REVIEW_FILE = os.path.join(OUTPUT_DIR, "review_bills.csv")
IIF_FILE = os.path.join(OUTPUT_DIR, "quickbooks_bills.iif")

# Default Account (Required for IIF import)
DEFAULT_SPL_ACCOUNT = "Cost of Goods Sold"

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

    # NEW FIXES (do not remove anything else)
    text = text.replace('"', '')   # Fix QuickBooks parsing issue
    text = text.replace(",", " ")  # Safer for IIF

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# --------------------------------------------------
# Write IIF
# --------------------------------------------------

def write_iif():

    print("Loading review file...")

    df = pd.read_csv(REVIEW_FILE, encoding="cp1252")

    df["Approved"] = (
        df["Approved"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df = df[df["Approved"] == "Y"]

    print(f"Approved rows: {len(df)}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    with open(IIF_FILE, "w", encoding="utf-8") as f:

        # TRNS header
        f.write("!TRNS\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\n")

        # SPL header (Added CLASS column)
        f.write(
            "!SPL\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\tMEMO\tINVITEM\tQNTY\tPRICE\tCLASS\n"
        )

        f.write("!ENDTRNS\n")

        for bill, group in df.groupby("BillID"):

            total = round(group["Amount"].sum(), 2)

            vendor = clean_text(group.iloc[0]["Vendor"])
            date = group.iloc[0]["Date"].strftime("%m/%d/%Y")

            # TRNS Line
            f.write(
                f"TRNS\tBILL\t{date}\tAccounts Payable\t{vendor}\t-{total}\t{bill}\n"
            )

            # SPL Lines
            for _, r in group.iterrows():

                desc = clean_text(r["Description"])
                amount = round(r["Amount"], 2)
                item = clean_text(r["Item"])
                job = clean_text(r["CustomerJob"])

                f.write(
                    f"SPL\tBILL\t{date}\t{DEFAULT_SPL_ACCOUNT}\t{vendor}\t{amount}\t{bill}\t"
                    f"{desc}\t{item}\t1\t{amount}\t{job}\n"
                )

            f.write("ENDTRNS\n")

    print("quickbooks_bills.iif created")


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    print("----------------------------------------")
    print("Build QuickBooks IIF")
    print("----------------------------------------")

    write_iif()

    print("Done.")