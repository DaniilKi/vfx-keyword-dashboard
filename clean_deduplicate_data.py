import pandas as pd
import numpy as np

input_file = '/home/ubuntu/combined_keywords.csv'
output_file = '/home/ubuntu/cleaned_deduplicated_keywords.csv'

print(f"Loading combined keywords from {input_file}")
df = pd.read_csv(input_file)

print(f"Shape of dataframe before cleaning and deduplication: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Standardize Keyword column
if "Keyword" in df.columns:
    df["Keyword"] = df["Keyword"].astype(str).str.lower().str.strip()
else:
    print("Error: 'Keyword' column not found.")
    # Exit or handle error appropriately if Keyword column is critical
    exit()

# Deduplicate based on the standardized Keyword column
original_row_count = len(df)
df.drop_duplicates(subset=["Keyword"], keep='first', inplace=True)
deduplicated_row_count = len(df)
print(f"Number of rows before deduplication: {original_row_count}")
print(f"Number of rows after deduplication: {deduplicated_row_count}")
print(f"Number of duplicate rows removed: {original_row_count - deduplicated_row_count}")

# Select and rename relevant columns
columns_to_keep_and_rename = {
    "Keyword": "keyword",
    "Avg. monthly searches": "avg_monthly_searches",
    "Top of page bid (low range)": "cpc_low",
    "Top of page bid (high range)": "cpc_high",
    "Competition (indexed value)": "competition_score",
    "Competition": "competition_text", # Keeping the text version as well
    "Currency": "currency"
}

# Filter out columns that are not present in the DataFrame to avoid KeyError
actual_columns_to_select = {k: v for k, v in columns_to_keep_and_rename.items() if k in df.columns}
missing_columns = set(columns_to_keep_and_rename.keys()) - set(df.columns)
if missing_columns:
    print(f"Warning: The following expected columns were not found and will be skipped: {missing_columns}")

df_cleaned = df[list(actual_columns_to_select.keys())].copy() # Use .copy() to avoid SettingWithCopyWarning
df_cleaned.rename(columns=actual_columns_to_select, inplace=True)

# Ensure numerical columns are numeric, coercing errors
# For 'avg_monthly_searches', 'cpc_low', 'cpc_high', 'competition_score'
numeric_cols = ["avg_monthly_searches", "cpc_low", "cpc_high", "competition_score"]
for col in numeric_cols:
    if col in df_cleaned.columns:
        # Check if the column is already numeric to avoid unnecessary conversion
        if not pd.api.types.is_numeric_dtype(df_cleaned[col]):
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
            print(f"Converted column {col} to numeric. NaN count: {df_cleaned[col].isnull().sum()}")
        else:
            print(f"Column {col} is already numeric.")
    else:
        print(f"Warning: Numeric column {col} not found in cleaned dataframe.")

# Add a 'cpc' column, for simplicity using cpc_low for now, or average if both exist
if "cpc_low" in df_cleaned.columns and "cpc_high" in df_cleaned.columns:
    df_cleaned["cpc"] = (df_cleaned["cpc_low"] + df_cleaned["cpc_high"]) / 2
    print("Created 'cpc' column as average of 'cpc_low' and 'cpc_high'.")
elif "cpc_low" in df_cleaned.columns:
    df_cleaned["cpc"] = df_cleaned["cpc_low"]
    print("Created 'cpc' column using 'cpc_low'.")

print(f"Shape of dataframe after cleaning and selection: {df_cleaned.shape}")
print(f"Columns in cleaned dataframe: {df_cleaned.columns.tolist()}")
print(f"First 5 rows of cleaned dataframe:\n{df_cleaned.head().to_string()}")

# Save the cleaned dataframe
df_cleaned.to_csv(output_file, index=False)
print(f"Cleaned and deduplicated data saved to {output_file}")

