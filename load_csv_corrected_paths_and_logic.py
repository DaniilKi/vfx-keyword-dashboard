import pandas as pd

# Define file paths
file1 = '/home/ubuntu/upload/vfx-keyword-list.csv'
file2 = '/home/ubuntu/upload/vfx-keyword-list-2.csv'
output_file = '/home/ubuntu/combined_keywords.csv'

def check_columns(df):
    if df is None or df.empty:
        return False
    cols = [str(col).lower().strip().replace('"', '') for col in df.columns]
    # Check for presence of 'keyword' and some other expected column fragment
    has_keyword = any("keyword" in c for c in cols) # Covers 'keyword', 'search term keyword', etc.
    has_avg_searches = any("avg. monthly searches" in c or "average monthly searches" in c for c in cols)
    has_cpc_or_bid = any("cpc" in c or "bid" in c for c in cols)
    has_competition = any("competition" in c for c in cols)
    
    # We need at least 'keyword' and one other major metric column, and more than 1 column total
    return df.shape[1] > 1 and has_keyword and (has_avg_searches or has_cpc_or_bid or has_competition)

def load_single_csv_with_skiprows(filepath):
    print(f"Attempting to load {filepath} with advanced logic...")
    df_loaded = None
    
    # Prioritize utf-16 due to BOM
    print(f"Trying encoding: utf-16 for {filepath}")
    for skip in range(7): # Try skipping 0 to 6 lines
        print(f"  Trying with encoding: utf-16, skiprows: {skip}")
        try:
            # Try with comma separator
            df_temp = pd.read_csv(filepath, encoding='utf-16', skiprows=skip, sep=',')
            print(f"    Loaded with utf-16, skiprows {skip}, sep ','. Shape: {df_temp.shape}, Columns: {df_temp.columns.tolist()}")
            if check_columns(df_temp):
                print(f"    SUCCESS: Columns look reasonable for {filepath} with utf-16, skiprows {skip}, sep ','.")
                df_loaded = df_temp
                break # Found correct parameters

            # If comma didn't work well (e.g. single column), try tab
            if df_temp.shape[1] == 1 and df_loaded is None:
                 print(f"    Comma sep resulted in 1 column. Trying tab sep for utf-16, skiprows {skip}.")
                 df_temp_tab = pd.read_csv(filepath, encoding='utf-16', skiprows=skip, sep='\t')
                 print(f"    Loaded with utf-16, skiprows {skip}, sep '\t'. Shape: {df_temp_tab.shape}, Columns: {df_temp_tab.columns.tolist()}")
                 if check_columns(df_temp_tab):
                     print(f"    SUCCESS: Columns look reasonable for {filepath} with utf-16, skiprows {skip}, sep '\t'.")
                     df_loaded = df_temp_tab
                     break # Found correct parameters
        
        except pd.errors.ParserError as pe:
            print(f"    ParserError with utf-16, skiprows {skip}: {pe}. Might be delimiter or malformed line.")
        except pd.errors.EmptyDataError:
            print(f"    EmptyDataError with utf-16, skiprows {skip}. Likely skipped too many lines.")
        except UnicodeDecodeError as ude:
             print(f"    UnicodeDecodeError with utf-16, skiprows {skip}: {ude}.")
             # If utf-16 decoding fails fundamentally, break from skiprows for this encoding attempt
             break 
        except Exception as e:
            print(f"    Other error with utf-16, skiprows {skip}: {e}")

        if df_loaded is not None:
            break
    
    if df_loaded is not None:
        return df_loaded

    # Fallback to other encodings if utf-16 failed
    print(f"UTF-16 loading failed for {filepath}. Trying other encodings (without skiprows iteration).")
    other_encodings = ["utf-8", "latin1", "iso-8859-1", "cp1252"]
    for enc in other_encodings:
        print(f"  Trying encoding: {enc} for {filepath}")
        try:
            df_temp = pd.read_csv(filepath, encoding=enc, sep=',')
            if check_columns(df_temp):
                print(f"    SUCCESS: Columns look reasonable for {filepath} with {enc}, sep ','.")
                df_loaded = df_temp
                break
            
            if df_temp.shape[1] == 1 and df_loaded is None:
                 df_temp_tab = pd.read_csv(filepath, encoding=enc, sep='\t')
                 if check_columns(df_temp_tab):
                     print(f"    SUCCESS: Columns look reasonable for {filepath} with {enc}, sep '\t'.")
                     df_loaded = df_temp_tab
                     break
        except Exception as e:
            print(f"    Error with {enc}: {e}")
        if df_loaded is not None:
            break
            
    return df_loaded

df1 = load_single_csv_with_skiprows(file1)
df2 = load_single_csv_with_skiprows(file2)

if df1 is not None and df2 is not None:
    print(f"Successfully loaded df1 (shape: {df1.shape}, columns: {df1.columns.tolist()}) and df2 (shape: {df2.shape}, columns: {df2.columns.tolist()})")
    combined_df = pd.concat([df1, df2], ignore_index=True)
    combined_df.to_csv(output_file, index=False)
    print(f"Successfully combined files into {output_file}")
    print(f"Shape of combined dataframe: {combined_df.shape}")
    print(f"Columns of combined dataframe: {combined_df.columns.tolist()}")
    print(f"First 5 rows of combined dataframe:\n{combined_df.head().to_string()}")
else:
    print("Failed to load one or both CSV files correctly with advanced logic.")
    if df1 is None:
        print(f"df1 ('{file1}') could not be loaded or parsed correctly.")
    if df2 is None:
        print(f"df2 ('{file2}') could not be loaded or parsed correctly.")

