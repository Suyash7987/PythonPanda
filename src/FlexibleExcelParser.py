# import json
# import pandas as pd

# # -------------------------------
# # LOAD CONFIG
# # -------------------------------
# with open("config.json", "r") as f:
#     CONFIG = json.load(f)


# # ===============================
# # MAIN DISPATCHER
# # ===============================
# def get_price(category, sheet_name, params, product=None):

#     cat_cfg = CONFIG["file_structures"][category]

#     # -------- Case 1: category → product → sheets --------
#     if product is not None:
#         if product not in cat_cfg:
#             raise ValueError(f"Product '{product}' not found in category '{category}'")
#         product_cfg = cat_cfg[product]

#     # -------- Case 2: category → sheets directly --------
#     else:
#         if "file_pattern" not in cat_cfg:
#             raise ValueError(f"Product must be provided for category '{category}'")
#         product_cfg = cat_cfg

#     file_name = product_cfg["file_pattern"]
#     # print("Available sheets:", product_cfg["sheets"].keys())
#     # print("Requested sheet:", sheet_name)
#     sheet_cfg = product_cfg["sheets"][sheet_name]
#     sheet_type = sheet_cfg["type"]

#     df = pd.read_excel(file_name, sheet_name=sheet_name, header=None)

#     if sheet_type == "letters_price":
#         return parse_letters(df, sheet_cfg, params)

#     elif sheet_type == "bars":
#         return parse_bars(df, sheet_cfg, params)

#     elif sheet_type in ("logos", "Canada_logos"):
#         return parse_logos(df, sheet_cfg, params)

#     elif sheet_type == "letters_fonts":
#         return parse_letters_fonts(df, sheet_cfg, params)

#     elif sheet_type == "letters_size_range":
#         return parse_letters_size_range(df, sheet_cfg, params)

#     elif sheet_type == "minimum_price":
#         return parse_minimum_price(df, sheet_cfg, params)

#     else:
#         raise ValueError("Unknown sheet type: " + sheet_type)


# # ===============================
# # LETTERS (FLAT CUT, PVC, FOAM)
# # ===============================

# def parse_letters(df, cfg, params):

#     country = params["country"]
#     thickness = params["thickness"]
#     column_number = params["column"]

#     country_col = cfg["country_column"]

#     start_row = None
#     for i in range(len(df)):
#         cell = str(df.iloc[i, country_col]).strip()
#         if cell.lower() == country.lower():
#             start_row = i
#             break

#     if start_row is None:
#         raise ValueError("Country not found")

#     header_row = start_row + cfg["header_row_offset"]
#     headers = df.iloc[header_row, cfg["price_start_column"]:].tolist()

#     row = start_row + cfg["data_start_offset"]
#     data = []

#     while row < len(df):
#         cell = str(df.iloc[row, country_col]).strip()
#         if cell in cfg["stop_conditions"]:
#             break
#         prices = df.iloc[row, cfg["price_start_column"]:].tolist()
#         data.append([cell] + prices)
#         row += 1
   
#     table = pd.DataFrame(data, columns=["thickness"] + headers).set_index("thickness")
#     return table.loc[thickness, column_number]


# # ===============================
# # BARS
# # ===============================

# def parse_bars(df, cfg, params):

#     label = params["label"]
#     depth = params["depth"]
#     height = params["height"]

#     if label.startswith("US"):
#         start_col, end_col = cfg["us_columns"]
#     else:
#         start_col, end_col = cfg["canada_columns"]

#     block = df.iloc[:, start_col:end_col]

#     start_row = None
#     for i in range(len(block)):
#         if str(block.iloc[i, 0]).strip() == label:
#             start_row = i
#             break

#     if start_row is None:
#         raise ValueError("Bar section not found")

#     header_row = start_row + cfg["header_row_offset"]
#     heights = block.iloc[header_row, 1:7].tolist()

#     data = []
#     row = start_row + cfg["data_start_offset"]

#     while row < len(block) and not isinstance(block.iloc[row, 0], str):
#         data.append([block.iloc[row, 0]] + block.iloc[row, 1:7].tolist())
#         row += 1

#     table = pd.DataFrame(data, columns=["depth"] + heights).set_index("depth")
#     return table.loc[depth, height]


# # ===============================
# # LOGOS (SQ INCH TABLE)
# # ===============================

# def parse_logos(df, cfg, params):

#     label = params["label"]
#     row_val = params["row"]
#     col_val = params["col"]

#     thickness_col = cfg["thickness_column"]

#     start_row = None
#     for i in range(len(df)):
#         if str(df.iloc[i, thickness_col]).strip() == label:
#             start_row = i
#             break

#     if start_row is None:
#         raise ValueError("Logo thickness not found")

#     header_row = start_row + cfg["header_row_offset"]
#     headers = df.iloc[header_row, cfg["price_start_column"]:].tolist()

#     data = []
#     row = start_row + cfg["data_start_offset"]

#     while row < len(df):
#         cell = df.iloc[row, thickness_col]
#         if isinstance(cell, str) or pd.isna(cell):
#             break
#         data.append([cell] + df.iloc[row, cfg["price_start_column"]:].tolist())
#         row += 1

#     table = pd.DataFrame(data, columns=["sq"] + headers).set_index("sq")
#     return table.loc[row_val, col_val]


# # ===============================
# # CAST METAL — LETTERS BY FONT
# # ===============================

# def parse_letters_fonts(df, cfg, params):

#     font = params["font"].strip().lower()
#     size = float(params["size"])
#     country = params["country"].strip().lower()
#     material = params["material"].strip().lower()

#     for i in range(cfg["data_start_row"], len(df)):

#         cell_font = str(df.iloc[i, cfg["font_column"]]).strip().lower()

#         raw_size = str(df.iloc[i, cfg["size_column"]]).strip()
#         # remove inch symbol if present: 6" -> 6
#         raw_size = raw_size.replace('"', '')

#         try:
#             cell_size = float(raw_size)
#         except:
#             continue

#         if cell_font == font and cell_size == size:

#             if country == "us" and material == "aluminum":
#                 return df.iloc[i, cfg["us_aluminum_column"]]

#             if country == "us" and material == "bronze":
#                 return df.iloc[i, cfg["us_bronze_column"]]

#             if country == "canada" and material == "aluminum":
#                 return df.iloc[i, cfg["canada_aluminum_column"]]

#             if country == "canada" and material == "bronze":
#                 return df.iloc[i, cfg["canada_bronze_column"]]

#     raise ValueError("Font/size combination not found")


# # ===============================
# # CAST METAL — SIZE RANGE TABLE
# # ===============================

# def parse_letters_size_range(df, cfg, params):

#     size = params["size"]
#     country = params["country"]

#     for i in range(cfg["data_start_row"], len(df)):
#         if df.iloc[i, cfg["size_column"]] == size:
#             if country == "US":
#                 return df.iloc[i, cfg["us_column"]]
#             else:
#                 return df.iloc[i, cfg["canada_column"]]

#     raise ValueError("Size not found")


# # ===============================
# # CAST METAL — MINIMUM PRICE
# # ===============================

# def parse_minimum_price(df, cfg, params):
#     label = params["label"]

#     for i in range(cfg["data_start_row"], len(df)):
#         if str(df.iloc[i, cfg["label_column"]]).strip() == label:
#             return df.iloc[i, cfg["price_column"]]

#     raise ValueError("Minimum price label not found")


# # ===============================
# # TEST CALLS
# # ===============================

# print("ALUMINUM LOGOS:",
#       get_price(
#           "flat_cut_metal",
#           "US-Logos",
#           {"label": "1/8 Inch", "row": 10, "col": 24},
#           "flat_cut_metal_aluminum",
#       ))

# print("PVC LETTERS:",
#       get_price(
#           "flat_cut_pvc",
#           "Letters PVC",
#           {"country": "US", "thickness": "1-1/2", "column": 2}
#       ))

# # print("GEMLEAF BARS:",
# #       get_price(
# #           "gemleaf",
# #           "Bars",
# #           {"label": 'US 1/8"', "depth": 36, "height": 5}
# #       ))
# print("Laminate on Foam LETTERS:",
#       get_price(
#           "laminate_on_foam",
#           "Letters",
#           {"country": "us", "thickness": "1-1/2", "column": 4},
#       ))
# # print("CAST METAL LETTERS:",
# #       get_price(
# #      "cast_metal",
# #      "Letters-Fonts",
# #     {"font": "Arial", "size": 6, "country": "US", "material": "aluminum"}
# # ))
# # print("CAST METAL LETTERS:",
# #       get_price(
# #      "cast_metal",
# #      "Bars",
# #     {"label": 'Aluminum Cast Bars US', "depth": 12, "height": 1}
# # ))  

# ================================================================================================================================
import json
from pathlib import Path
import pandas as pd

from src.upcharges import get_upcharge

# ===============================
# LOAD CONFIG
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "config.json", "r") as f:
    CONFIG = json.load(f)


# ===============================
# MAIN FUNCTION
# ===============================
def get_price(product_line, sheet_name, params, product=None, upcharge=None):
    """
    product_line can be:
    - productLineKey  (example: "cut-metal")
    - productLineName (example: "Flat Cut Metal")
    """

    # ---------------------------------
    # Find the correct category from config
    # ---------------------------------
    cat_cfg = None
    for category_key, cfg in CONFIG["file_structures"].items():
        if cfg.get("productLineKey") == product_line:
            cat_cfg = cfg
            break
        if cfg.get("productLineName") == product_line:
            cat_cfg = cfg
            break

    if cat_cfg is None:
        raise ValueError(
            "Unknown product line. Use productLineKey or productLineName."
        )
    # -----------------------
    # FIND FILE & SHEETS
    # -----------------------
    if product:
        product_cfg = cat_cfg["productlineFile"][product]
        file_name = product_cfg["file_pattern"].strip()
        sheets = product_cfg["sheets"]
    else:
        file_name = cat_cfg["file_pattern"].strip()
        sheets = cat_cfg["productlineFile"]
    sheet_cfg = sheets[sheet_name]
    sheet_type = sheet_cfg["type"]
    df = pd.read_excel(BASE_DIR / file_name, sheet_name=sheet_name, header=None)
    # -----------------------
    # CALL PARSER
    # -----------------------
    if sheet_type == "letters_price":
        base_price = parse_letters(df, sheet_cfg, params)

    elif sheet_type == "bars":
        base_price = parse_bars(df, sheet_cfg, params)

    elif sheet_type in ("logos", "Canada_logos"):
        base_price = parse_logos(df, sheet_cfg, params)

    else:
        raise ValueError("Only letters, bars, and logos supported in beginner version")

    # ---------------------------------
    # Optional upcharge( For testing only)
    # ---------------------------------
    # upcharge_value = None
    # if upcharge:
    #     upcharge_value = get_upcharge(
    #         product_line=upcharge["product_line"],
    #         material=upcharge["material"],
    #         category=upcharge["category"],
    #         finish_type=upcharge["finish_type"],
    #         country=upcharge["country"],
    #     )

    return base_price

# ===============================
# LETTERS PARSER (SIMPLE)
# ===============================
def parse_letters(df, cfg, params):

    country = params["country"]
    thickness = params["thickness"]
    price_col_index = params["column"]

    country_col = cfg["country_column"]

    # find country row
    start_row = None
    for i in range(len(df)):
        cell = str(df.iloc[i, country_col]).strip()
        if cell.lower() == country.lower():
            start_row = i
            break

    if start_row is None:
        raise ValueError("Country not found")

    # read data rows
    row = start_row + cfg["data_start_offset"]
    stop_vals = [str(x).strip().lower() for x in cfg["stop_conditions"]]

    while row < len(df):

        cell = str(df.iloc[row, country_col]).strip()

        if cell.lower() in stop_vals:
            break

        if cell == thickness:
            price = df.iloc[row, cfg["price_start_column"] + price_col_index]
            return price

        row += 1

    raise ValueError("Thickness not found")


# ===============================
# BARS PARSER (SIMPLE)
# ===============================
def parse_bars(df, cfg, params):

    label = params["label"]
    depth = params["depth"]
    height = params["height"]

    # choose US / Canada block
    if label.startswith("US"):
        start_col, end_col = cfg["us_columns"]
    else:
        start_col, end_col = cfg["canada_columns"]

    block = df.iloc[:, start_col:end_col]

    # find block start
    start_row = None
    for i in range(len(block)):
        cell = str(block.iloc[i, 0]).strip()
        if cell == label:
            start_row = i
            break

    if start_row is None:
        raise ValueError("Bar label not found")

    # read heights
    header_row = start_row + cfg["header_row_offset"]
    heights = block.iloc[header_row, 1:7].tolist()

    # read depth rows
    row = start_row + cfg["data_start_offset"]

    while row < len(block):

        cell = block.iloc[row, 0]

        if isinstance(cell, str) and cell.strip() != "":
            break

        if cell == depth:
            height_index = heights.index(height) + 1
            price = block.iloc[row, height_index]
            return price

        row += 1

    raise ValueError("Depth not found")

def parse_logos(df, cfg, params):

    label = params["label"]       # thickness label like "1/8 Inch"
    sq_value = params["row"]      # square inch value
    col_value = params["col"]     # column header value

    thickness_col = cfg["thickness_column"]

    # find thickness section
    start_row = None
    for i in range(len(df)):
        cell = str(df.iloc[i, thickness_col]).strip()
        if cell == label:
            start_row = i
            break

    if start_row is None:
        raise ValueError("Logo thickness label not found")

    # read header row
    header_row = start_row + cfg["header_row_offset"]
    headers = df.iloc[header_row, cfg["price_start_column"]:].tolist()

    if col_value not in headers:
        raise ValueError("Requested column not found in logo table")

    col_index = headers.index(col_value) + cfg["price_start_column"]

    # read data rows
    row = start_row + cfg["data_start_offset"]

    while row < len(df):

        cell = df.iloc[row, thickness_col]

        if isinstance(cell, str) or pd.isna(cell):
            break

        if cell == sq_value:
            price = df.iloc[row, col_index]
            return price

        row += 1

    raise ValueError("Square inch value not found")


# ===============================
# TEST EXAMPLES
# ===============================

if __name__ == "__main__":
    # Simple test calls (only run when this file is executed directly)
    print(
        "Flat Cut PVC Letters Price:",
        get_price(
            "flat-cut-pvc",
            "Letters PVC",
            {"country": "US", "thickness": "1-1/2", "column": 2},
            upcharge={
                "product_line": "FLAT_CUT_METAL",
                "material": "Stainless Steel",
                "category": "Mounting Option",
                "finish_type": "Double Faced Tape",
                "country": "US",
            },
        ),
    )

    # Uncomment for more tests:
    print("Flat Cut Metal Aluminum Bars Price:",
        get_price(
            "cut-metal",
            "Bars-Aluminum",
            {"label": 'US 1/8"', "depth": 36, "height": 5},
            "flat_cut_metal_aluminum",
            
        )
    )
    
    # print("Flat Cut Metal Aluminum Canada Logos Price:",
    #     get_price(
    #         "FLAT_CUT_METAL",
    #         "Canada-Logos",
    #         {"label": "1/8 Inch", "row": 10, "col": 24},
    #         "flat_cut_metal_aluminum",
    #     )
    # )
    #
    # print("Flat Cut Metal Aluminum Logos Price:",
    #     get_price(
    #         "FLAT_CUT_METAL",
    #         "US-Logos",
    #         {"label": "1/8 Inch", "row": 10, "col": 24},
    #         "flat_cut_metal_aluminum",
    #     )
    # )