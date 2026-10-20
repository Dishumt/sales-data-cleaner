import sys
import sqlite3
import time
import numpy as np
import pandas as pd


def main():
    df = get_file()
    removed, cleaned = clean_data(df)
    save_to_csv_db(removed, cleaned)
    report(df, removed, cleaned)    






def get_file():
    
    required_headers = ["Invoice", "StockCode", "Quantity", "Price"]

    if len(sys.argv) != 2 or not sys.argv[1].endswith('.csv'):
        sys.exit("Usage: python project.py <filename.csv>")   
    try:
        df = pd.read_csv(sys.argv[1], encoding='latin-1')
        for col in ["Price", "Quantity"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        if all(header in df.columns for header in required_headers):
            return df
        else:
            sys.exit(f"The table must contain required headers: {', '.join(required_headers)}")
    except FileNotFoundError:
        sys.exit("Error: File not found.")
    except pd.errors.EmptyDataError:
        sys.exit("Error: File is empty.")
    except Exception as e:
        sys.exit(f"Error reading CSV file: {e}")



def clean_data(df):
    reasons = pd.Series("", index=df.index)

    critical = ["Invoice", "StockCode", "Price", "Quantity"]

    other_columns = df.columns.difference(critical)

    for col in other_columns:
        df[col] = df[col].fillna("Unknown")
        
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip().replace("", "Unknown")

    #missing
    reasons.loc[df["Invoice"].isna()] += "Invoice_missing; "
    reasons.loc[df["StockCode"].isna()] += "StockCode_missing; "
    reasons.loc[df["Price"].isna()] += "Price_missing; "
    reasons.loc[df["Quantity"].isna()] += "Quantity_missing; "

    #anomal data
    reasons.loc[df["Quantity"] <= 0] += "Anomal_quantity; "
    reasons.loc[df["Invoice"].str.startswith("C", na=False)] += "Canceled_operation; "
    reasons.loc[df["Price"] <= 0] += "Anomal_price; "

    #duplicates
    duplicate_mask = df.duplicated()
    reasons.loc[duplicate_mask] += "duplicate; "

    bad_mask = reasons.str.strip() != ""

    cleaned = df.loc[~bad_mask].copy()
    removed = df.loc[bad_mask].copy()
    removed["Removal reason"] = reasons.loc[bad_mask].str.strip()

    
    
    return removed, cleaned

def report(initial, removed, cleaned):

    total = len(initial)

    percents_rem = (len(removed) / total * 100) if total > 0 else 0.0
    percents_clean = (len(cleaned) / total * 100) if total > 0 else 0.0

    
    print("=" * 45)
    print(" DATA CLEANING SUMMARY REPORT ".center(45))
    print("=" * 45)
    print(f"Initial number of rows: {len(initial)}")
    print(f"rows removed: {len(removed)} ({percents_rem:.2f}%)")
    print(f"rows left: {len(cleaned)} ({percents_clean:.2f}%)")

    print("-" * 45)
    print("BREAKDOWN BY REMOVAL REASONS: ")

    reasons_series = (
    removed["Removal reason"]
    .str.split(r"\s*;\s*")
    .explode()            
    .replace("", np.nan)  
    .dropna()
    )
    reason_counts = reasons_series.value_counts()

    for reason, count in reason_counts.items():
        print(f"  * {reason:<22}: {count:,} ({(count/len(reasons_series)*100):.2f}%)")              
    print("-" * 45)
    gross_turnover = round((cleaned["Price"]*cleaned["Quantity"]).sum())
    print(f"Gross Cleaned Turnover: ${gross_turnover:,}")

    print("=" * 45)


def save_to_csv_db(removed, cleaned):
  
    cleaned.to_csv("cleaned.csv", index=False)
    removed.to_csv("removed.csv", index=False)

    with sqlite3.connect("sales.db") as connection:
        cleaned.to_sql(
            "cleaned_data",
            connection,
            if_exists="replace",
            index=False,
            chunksize=30000
        )

        removed.to_sql(
            "removed_data",
            connection,
            if_exists="replace",
            index=False,
            chunksize=30000
        )










if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    elapsed_time = time.perf_counter() - start_time
    print(f"Program completed in {elapsed_time:.2f} seconds.")





"""
1. validate the sys argv
2. clear the file from rows missing critical info, repeating rows, rows with surely wrong data(wether formating or logical error), etc.
3. make sure all the deleted rows are logged in a separate file for review
4. create a new sql file with the cleaned data
5. make sure the new sql file is ready to be imported into the database
6. display a summary of the cleaning process, including the number of rows deleted, the number of rows remaining, and any other relevant statistics
7. suggest further analysis options or next steps based on the cleaned data

"""