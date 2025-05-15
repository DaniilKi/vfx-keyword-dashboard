import pandas as pd

# Define file paths
file1 = '/home/ubuntu/upload/vfx-keyword-list.csv'
file2 = '/home/ubuntu/upload/vfx-keyword-list-2.csv'
output_file = '/home/ubuntu/combined_keywords.csv'

# Try different encodings
encodings_to_try = ["utf-8", "latin1", "iso-8859-1", "cp1252"]
df1 = None
df2 = None

print(f"Attempting to load {file1}")
for enc in encodings_to_try:
    try:
        df1 = pd.read_csv(file1, encoding=enc)
        print(f"Successfully loaded {file1} with encoding {enc}")
        break
    except UnicodeDecodeError:
        print(f"Failed to load {file1} with encoding {enc}")
    except FileNotFoundError:
        print(f"File not found: {file1}")
        break 

print(f"Attempting to load {file2}")
for enc in encodings_to_try:
    try:
        df2 = pd.read_csv(file2, encoding=enc)
        print(f"Successfully loaded {file2} with encoding {enc}")
        break
    except UnicodeDecodeError:
        print(f"Failed to load {file2} with encoding {enc}")
    except FileNotFoundError:
        print(f"File not found: {file2}")
        break

if df1 is not None and df2 is not None:
    # Concatenate the dataframes
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # Save the combined dataframe
    combined_df.to_csv(output_file, index=False)

    print(f"Successfully combined files into {output_file}")
    print(f"Shape of combined dataframe: {combined_df.shape}")
    print(f"First 5 rows of combined dataframe:\n{combined_df.head().to_string()}")
else:
    print("Failed to load one or both CSV files with tried encodings or files not found.")
