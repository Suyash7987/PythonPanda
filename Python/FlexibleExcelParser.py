import json
import pandas as pd

# -------------------------------
# LOAD CONFIG
# -------------------------------
with open("config.json", "r") as f:
    CONFIG = json.load(f)


# ===============================
# MAIN DISPATCHER (NEW)
# ===============================

def get_price(category, sheet_name, params, product=None):

    cat_cfg = CONFIG["file_structures"][category]

    # -----------------------------
    # CASE 1: category → product → sheets
    # -----------------------------
    if product is not None:
        if product not in cat_cfg:
            raise ValueError(f"Product '{product}' not found in category '{category}'")
        product_cfg = cat_cfg[product]

    # -----------------------------
    # CASE 2: category → sheets directly
    # -----------------------------
    else:
        if "file_pattern" not in cat_cfg:
            raise ValueError(f"Product must be provided for category '{category}'")
        product_cfg = cat_cfg

    file_name = product_cfg["file_pattern"]
    sheet_cfg = product_cfg["sheets"][sheet_name]
    sheet_type = sheet_cfg["type"]

    df = pd.read_excel(file_name, sheet_name=sheet_name, header=None)

    if sheet_type == "letters_price":
        return parse_letters(df, sheet_cfg, params)

    elif sheet_type == "bars":
        return parse_bars(df, sheet_cfg, params)

    elif sheet_type == "logos":
        return parse_logos(df, sheet_cfg, params)

    elif sheet_type == "Canada_logos":
        return parse_logos(df, sheet_cfg, params)

    else:
        raise ValueError("Unknown sheet type: " + sheet_type)


# ===============================
# LETTERS PARSER
# ===============================

def parse_letters(df, cfg, params):

    country = params["country"]
    thickness = params["thickness"]
    column_number = params["column"]

    country_col = cfg["country_column"]

    # --- find country row ---
    start_row = None
    for i in range(len(df)):
        cell = str(df.iloc[i, country_col]).strip()
        if cell == country:
            start_row = i
            break

    if start_row is None:
        raise ValueError("Country not found")

    # --- read REAL header values ---
    header_row = start_row + cfg["header_row_offset"]
    headers = df.iloc[header_row, cfg["price_start_column"]:].tolist()

    # --- read data rows ---
    row = start_row + cfg["data_start_offset"]
    data = []

    while row < len(df):
        cell = str(df.iloc[row, country_col]).strip()

        if cell in cfg["stop_conditions"]:
            break

        prices = df.iloc[row, cfg["price_start_column"]:].tolist()
        data.append([cell] + prices)
        row += 1

    if not data:
        raise ValueError("No pricing data found")

    columns = ["thickness"] + headers
    table = pd.DataFrame(data, columns=columns).set_index("thickness")

    return table.loc[thickness, column_number]


# ===============================
# BARS PARSER
# ===============================

def parse_bars(df, cfg, params):

    label = params["label"]
    depth = params["depth"]
    height = params["height"]

    if label.startswith("US"):
        start_col, end_col = cfg["us_columns"]
    else:
        start_col, end_col = cfg["canada_columns"]

    block = df.iloc[:, start_col:end_col]

    start_row = None
    for i in range(len(block)):
        if str(block.iloc[i, 0]).strip() == label:
            start_row = i
            break

    if start_row is None:
        raise ValueError("Bar section not found")

    header_row = start_row + cfg["header_row_offset"]
    heights = block.iloc[header_row, 1:7].tolist()

    data = []
    row = start_row + cfg["data_start_offset"]

    while row < len(block) and not isinstance(block.iloc[row, 0], str):
        data.append([block.iloc[row, 0]] + block.iloc[row, 1:7].tolist())
        row += 1

    table = pd.DataFrame(data, columns=["depth"] + heights).set_index("depth")

    return table.loc[depth, height]


# ===============================
# LOGOS PARSER (US & CANADA)
# ===============================

def parse_logos(df, cfg, params):

    label = params["label"]
    row_val = params["row"]
    col_val = params["col"]

    thickness_col = cfg["thickness_column"]

    start_row = None
    for i in range(len(df)):
        if str(df.iloc[i, thickness_col]).strip() == label:
            start_row = i
            break

    if start_row is None:
        raise ValueError("Logo thickness not found")

    header_row = start_row + cfg["header_row_offset"]
    headers = df.iloc[header_row, cfg["price_start_column"]:].tolist()

    data = []
    row = start_row + cfg["data_start_offset"]

    while row < len(df):
        cell = df.iloc[row, thickness_col]
        if isinstance(cell, str) or pd.isna(cell):
            break
        data.append([cell] + df.iloc[row, cfg["price_start_column"]:].tolist())
        row += 1

    table = pd.DataFrame(data, columns=["sq"] + headers).set_index("sq")

    return table.loc[row_val, col_val]


# ===============================
# TEST CALLS
# ===============================

print("ALUMINUM LOGOS:",
      get_price(
          "flat_cut_metal",
          "US-Logos",
          {"label": "1/8 Inch", "row": 10, "col": 24},
          "flat_cut_metal_aluminum",
      ))

print("PVC LETTERS:",
      get_price(
          "flat_cut_pvc",
          "Letters PVC",
          {"country": "US", "thickness": "1-1/2", "column": 2}
      ))

print("GEMLEAF BARS:",
      get_price(
          "gemleaf",
          "Bars",
          {"label": 'US 1/8"', "depth": 36, "height": 5}
      ))
print("Laminate on Foam LETTERS:",
      get_price(
          "laminate_on_foam",
          "Letters",
          {"country": "us", "thickness": "1-1/2", "column": 4},
      ))