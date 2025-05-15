import pandas as pd

# Define file paths
file1 = 
/home/ubuntu/upload/vfx-keyword-list.csv
file2 = 
/home/ubuntu/upload/vfx-keyword-list-2.csv
output_file = 
/home/ubuntu/combined_keywords.csv

# Try specific encoding first, then others
encodings_to_try = ["utf-16", "utf-8", "latin1", "iso-8859-1", "cp1252"]
df1 = None
df2 = None

print(f"Attempting to load {file1}")
for enc in encodings_to_try:
    try:
        df1 = pd.read_csv(file1, encoding=enc)
        print(f"Successfully loaded {file1} with encoding {enc}")
        # Check if columns look reasonable, otherwise try next encoding
        # Ensure 'keyword' (case-insensitive) is one of the columns and there's more than one column
        if df1.shape[1] > 1 and "keyword" in [str(col).lower() for col in df1.columns]:
            print(f"Columns look reasonable for {file1} with encoding {enc}. Columns: {df1.columns.tolist()}")
            break
        else:
            print(f"Columns in {file1} with encoding {enc} do not look correct (columns: {df1.columns.tolist()}, shape: {df1.shape}), trying next encoding.")
            df1 = None # Reset df1 to ensure we don't use a malformed one
    except UnicodeDecodeError:
        print(f"Failed to load {file1} with encoding {enc} due to UnicodeDecodeError")
    except FileNotFoundError:
        print(f"File not found: {file1}")
        df1 = None # Ensure df1 is None if file not found
        break 
    except Exception as e:
        print(f"An unexpected error occurred while loading {file1} with encoding {enc}: {e}")
        df1 = None # Reset on other errors too

print(f"Attempting to load {file2}")
for enc in encodings_to_try:
    try:
        df2 = pd.read_csv(file2, encoding=enc)
        print(f"Successfully loaded {file2} with encoding {enc}")
        if df2.shape[1] > 1 and "keyword" in [str(col).lower() for col in df2.columns]:
            print(f"Columns look reasonable for {file2} with encoding {enc}. Columns: {df2.columns.tolist()}")
            break
        else:
            print(f"Columns in {file2} with encoding {enc} do not look correct (columns: {df2.columns.tolist()}, shape: {df2.shape}), trying next encoding.")
            df2 = None # Reset df2
    except UnicodeDecodeError:
        print(f"Failed to load {file2} with encoding {enc} due to UnicodeDecodeError")
    except FileNotFoundError:
        print(f"File not found: {file2}")
        df2 = None # Ensure df2 is None if file not found
        break
    except Exception as e:
        print(f"An unexpected error occurred while loading {file2} with encoding {enc}: {e}")
        df2 = None # Reset on other errors too

if df1 is not None and df2 is not None:
    print(f"Successfully loaded df1 (shape: {df1.shape}) and df2 (shape: {df2.shape}) before concatenation.")
    # Concatenate the dataframes
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # Save the combined dataframe
    combined_df.to_csv(output_file, index=False)

    print(f"Successfully combined files into {output_file}")
    print(f"Shape of combined dataframe: {combined_df.shape}")
    print(f"Columns of combined dataframe: {combined_df.columns.tolist()}")
    print(f"First 5 rows of combined dataframe:\n{combined_df.head().to_string()}")
else:
    print("Failed to load one or both CSV files correctly.")
    if df1 is None:
        print(f"df1 could not be loaded or parsed correctly with any of the attempted encodings or was not found.")
    if df2 is None:
        print(f"df2 could not be loaded or parsed correctly with any of the attempted encodings or was not found.")
