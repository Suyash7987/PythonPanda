# import pandas as pd
# import json

# with open("config.json", "r") as f:
#     CONFIG = json.load(f)
# file_name = "tq_upcharges_flat_cut_metal_demo.xlsx"
# df = pd.read_excel(file_name)

# # Just to see raw data once
# print(df)
# material_columns = CONFIG["upcharges_file_structure"]["flat_cut_metal"]["flat_cut_metal_aluminum"]["material_columns"]
# # MATERIAL_COLUMNS = {
# #     "Aluminum": {
# #         "label": 0,   # Column A
# #         "type": 1,    # Column B
# #         "us": 2,      # Column C
# #         "canada": 3   # Column D
# #     },
# #     "Stainless Steel": {
# #         "label": 4,   # Column E
# #         "type": 5,    # Column F
# #         "us": 6,      # Column G
# #         "canada": 7   # Column H
# #     },
# #     "Brass / Bronze": {
# #         "label": 8,   # Column I
# #         "type": 9,    # Column J
# #         "us": 10,     # Column K
# #         "canada": 11  # Column L
# #     }
# # }
# def get_upcharge(material, category, finish_type, country):

#     cols = material_columns[material]
#     for row in range(len(df)):

#         label = str(df.iloc[row, cols["label"]]).strip()
#         option = str(df.iloc[row, cols["type"]]).strip()

#         label_match = label.lower() == category.lower()
#         finish_row = label == "-"

#         # Debug: Print every row's values
#         if row < 20 or label_match or option.lower() in finish_type.lower() or finish_type.lower() in option.lower():

#          if option.lower() == finish_type.lower() and (finish_row or label_match):
           

#             if country.upper() == "US":
#                 price = df.iloc[row, cols["us"]]
#             else:
#                 price = df.iloc[row, cols["canada"]]


#             price_str = str(price).strip().upper()


#             if price_str == "BASE PRICE":
#                 return "BASE PRICE"

#             if price_str in ["", ".", "NAN"]:
#                 return None

#             return float(price)

#     return None


# result = get_upcharge(
#     material="Brass/Bronze",
#     category="Color/Finish:",
#     finish_type="Oxidized Finishes",
#     country="US"
# )

# print("Upcharge:", result)

# ======================================================================================================================
import pandas as pd
import json


# ----------------------------
# LOAD CONFIG
# ----------------------------
with open("config.json", "r") as f:
    CONFIG = json.load(f)


# ----------------------------
# MAIN UNIVERSAL FUNCTION
# ----------------------------
def get_upcharge(product_line, material, category, finish_type, country):
    """
    product_line : 'FLAT_CUT_METAL', 'GEMLEAF_LAMINATE', etc
    material     : block name from config (Aluminum, Stainless Steel, etc)
    category     : 'Mounting Option', 'Color/Finish:' etc
    finish_type  : 'Double Faced Tape', 'Oxidized Finishes', etc
    country      : 'US' or 'Canada'
    """

    # ✅ NEW PATH
    product_cfg = CONFIG["file_structures"][product_line]
    print("product_cfg :- ",product_cfg)
    file_name = product_cfg["upchargeFile"]
    blocks = product_cfg["upchargeFileStructure"]["blocks"]

    if material not in blocks:
        raise ValueError(f"Material/Block not found in config: {material}")

    cols = blocks[material]

    # read excel (no headers in file)
    df = pd.read_excel(file_name, header=None)

    for row in range(len(df)):

        label = str(df.iloc[row, cols["label"]]).strip()
        option = str(df.iloc[row, cols["type"]]).strip()

        label_lower = label.lower()
        option_lower = option.lower()
        category_lower = category.lower()

        valid_label = (
            label == "-" or
            label_lower == category_lower or
            label_lower == "nan" or
            label == ""
        )

        if option_lower == finish_type.lower() and valid_label:

            if country.upper() == "US":
                price = df.iloc[row, cols["us"]]
            else:
                price = df.iloc[row, cols["canada"]]

            price_str = str(price).strip().upper()

            if price_str == "BASE PRICE":
                return "BASE PRICE"

            if price_str in ["", ".", "NAN", "-"]:
                return None

            return float(price)

    return None
metal_result = get_upcharge(
    product_line="FLAT_CUT_METAL",
    material="Stainless Steel",
    category="Mounting Option",
    finish_type="Double Faced Tape",
    country="US"
)

print("Metal Upcharge:", metal_result)
# Completed The upcharge  