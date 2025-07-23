------------------DATA CLEANING AND VALIDATION-----------------------
import pandas as pd
df = pd.read_csv("sales_data.csv")
print(df.head())
df.rename(columns={'catégorie': 'category'}, inplace=True)
print(df.head())
category_map = {
    "Vêtements": "Clothing",
    "Alimentation": "Food",
    "Électronique": "Electronics",
    "Sports": "Sports"
}
df['category'] = df['category'].map(category_map).fillna(df['category'])
print(df.head())
import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "Partha@123")
DB_NAME = os.getenv("DB_NAME", "salesdb")


# Step 3 — Clean/transform columns
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Purchase Address'] = df['Purchase Address'].str.strip()
df['Product'] = df['Product'].str.strip()

# Step 4 — Remove duplicates on Order ID
df.drop_duplicates(subset='Order ID', inplace=True)

# Step 5 — Validate turnover
df['calc_turnover'] = df['Quantity Ordered'] * df['Price Each']
turnover_diff = (df['turnover'] - df['calc_turnover']).abs().sum()
if turnover_diff > 1e-6:
    print(f"WARNING: Turnover mismatch total difference: {turnover_diff:.2f}")
df['turnover'] = df['calc_turnover']

# Step 6 — Validate margin
df['calc_margin'] = df['turnover'] - (df['Quantity Ordered'] * df['Cost price'])
margin_diff = (df['margin'] - df['calc_margin']).abs().sum()
if margin_diff > 1e-6:
    print(f"WARNING: Margin mismatch total difference: {margin_diff:.2f}")
df['margin'] = df['calc_margin']

# Drop helper columns
df.drop(columns=['calc_turnover', 'calc_margin'], inplace=True)

# Step 7 — Optional: Split purchase address
df[['street', 'city', 'state_zip']] = df['Purchase Address'].str.split(',', expand=True)
df['city'] = df['city'].str.strip()
df['state'] = df['state_zip'].str.strip().str[:2]
df['zip'] = df['state_zip'].str.strip().str[-5:]
df.drop(columns=['state_zip'], inplace=True)

print(df.head())
df.to_csv("sales_data_cleaned.csv", index=False)
print("Cleaned data saved to sales_data_cleaned.csv")
