from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
file_name = BASE_DIR / "data/flat_cut_metal_aluminum .xlsx"
# Read Excel file

def get_letters_price(country, thickness, column_number,df):
    """
    country        : "US" or "Canada"
    thickness      : "1/8", "1/4", "3/8", "1/2", "1"
    column_number  : 1, 2, 3, ...
    """
    start_row = None #Act as a keyholder to find where country starts 
    for i in range(len(df)):
        cell_value = str(df.iloc[i, 0]).strip()
        print("cell_value :- ",cell_value)
        if cell_value == country:
            start_row = i
            print("start_row :- ",start_row)
            break
        elif country == "US":
            start_row = i
            break

    if start_row is None:
        raise ValueError("Country not found")

    # STEP 2: Data starts after header row
    row = start_row + 2
    data = []
    print("Data1 :- ",data)
    while row < len(df):
        cell = str(df.iloc[row, 0]).strip()
        print("cell :- ",cell)
        # Stop if next country starts or cell is empty
        if cell in ["US", "Canada", "nan"]:
            break

        thickness_value = cell
        prices = df.iloc[row, 1:].tolist()
        data.append([thickness_value] + prices)
        row += 1

    if not data:
        raise ValueError("No pricing data found for this country")

    # STEP 3: Build DataFrame with explicit columns
    num_price_cols = len(data[0]) - 1
    columns = ["thickness"] + list(range(1, num_price_cols + 1))

    letters_df = pd.DataFrame(data, columns=columns)
    # STEP 4: Set thickness as index
    letters_df = letters_df.set_index("thickness")
    print("letters_df :- ",letters_df)
    # STEP 5: Return price
    return letters_df.loc[thickness, column_number]
def get_logos(label, row_num, col_num, df):
    """
    label   : Thickness label (e.g. '1/8 Inch', '1/4 Inch')
    row_num : Row square-inch value (e.g. 30)
    col_num : Column square-inch value (e.g. 48)
    """

    # ---------------------------------
    # STEP 1: FIND THICKNESS SECTION
    # ---------------------------------
    start_row = None
    for i in range(len(df)):
        if str(df.iloc[i, 0]).strip() == label:
            start_row = i
            break

    if start_row is None:
        raise ValueError("Logo thickness section not found")

    # ---------------------------------
    # STEP 2: READ COLUMN HEADERS
    # ---------------------------------
    header_row = start_row + 1
    col_headers = df.iloc[header_row, 1:].tolist()

    # ---------------------------------
    # STEP 3: READ DATA ROWS
    # ---------------------------------
    data = []
    row = start_row + 2

    while row < len(df):
        cell = df.iloc[row, 0]

        # stop when next thickness starts or empty row
        if isinstance(cell, str) or pd.isna(cell):
            break

        data.append([cell] + df.iloc[row, 1:].tolist())
        row += 1

    if not data:
        raise ValueError("No logo pricing data found")

    # ---------------------------------
    # STEP 4: BUILD CLEAN TABLE
    # ---------------------------------
    logo_df = pd.DataFrame(
        data,
        columns=["sq_in"] + col_headers
    ).set_index("sq_in")

    # ---------------------------------
    # STEP 5: RETURN PRICE
    # ---------------------------------
    return logo_df.loc[row_num, col_num]

def get_bars(df, depth, height, label):
    """
    Works for BOTH US and Canada sections
    Example labels:
    - "US 1/4\""
    - "Canada 1\""
    """

    # STEP 1: Decide block based on label
    if label.startswith("US"):
        block = df.iloc[:, 0:7]      # Columns A–G
    elif label.startswith("Canada"):
        block = df.iloc[:, 7:13]     # Columns H–M
    else:
        print("Invalid label")
        return None

    # STEP 2: Find where section starts
    start_row = None
    for i in range(len(block)):
        if str(block.iloc[i, 0]).strip() == label:
            start_row = i
            break

    if start_row is None:
        print("Label not found")
        return None

    # STEP 3: Read height headers (1–6)
    heights = block.iloc[start_row + 1, 1:7].tolist()

    # STEP 4: Read depth & price rows
    data = []
    row = start_row + 2

    while row < len(block) and not isinstance(block.iloc[row, 0], str):
        depth_value = block.iloc[row, 0]
        prices = block.iloc[row, 1:7].tolist()
        data.append([depth_value] + prices)
        row += 1

    # STEP 5: Create clean DataFrame
    section_df = pd.DataFrame(data, columns=["depth"] + heights)

    # STEP 6: Set depth as index
    section_df = section_df.set_index("depth")

    # STEP 7: Return price
    return section_df.loc[depth, height]

def get_sheets(sheets):
    match sheets:
        case "US-Logos":
            df = pd.read_excel(file_name, sheet_name=2)
            return get_logos("1 Inch", 10, 24, df)
        case "Letters – Aluminum":
            df = pd.read_excel(file_name, sheet_name=0,header=None)
            return get_letters_price("US", "3/8", 42, df)
        case "Bars – Aluminum":
            df = pd.read_excel(file_name, sheet_name=1,header=None)
            return get_bars(df,36,5,'US 1"')

print(get_sheets("US-Logos"))
print(get_sheets("Letters – Aluminum"))
print(get_sheets("Bars – Aluminum"))

