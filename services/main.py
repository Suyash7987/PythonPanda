from pathlib import Path
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel

# -------------------------------------------------
# Add project root to Python path so we can import
# from src/ without installing a package.
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import the existing pricing logic
from src.FlexibleExcelParser import get_price  # noqa: E402
from src.upcharges import get_upcharge  # noqa: E402

app = FastAPI()


# =================================================
# Request models using Pydantic method
# =================================================

class UpchargeInput(BaseModel):
    product_line: str
    material: Optional[str]=None
    category: str
    finish_type: str
    country: str


class LettersRequest(BaseModel):
    product_line: str
    sheet_name: str
    country: str
    thickness: str
    height: int
    product: Optional[str] = None
    upcharge: Optional[UpchargeInput] = None


class BarsRequest(BaseModel):
    product_line: str
    sheet_name: str
    label: str
    depth: float
    height: float
    product: Optional[str] = None


class LogosRequest(BaseModel):
    product_line: str
    sheet_name: str
    label: str
    row: float
    col: float
    product: Optional[str] = None


class UpchargeRequest(BaseModel):
    product_line: str
    material: str
    category: str
    finish_type: str
    country: str


# =================================================
# API endpoints
# =================================================

# @app.post("/price/letters")
# def price_letters(payload: LettersRequest):
#     """
#     Get letter price from Excel based on country, thickness, and column.
#     """
#     try:
#         price = get_price(
#             product_line=payload.product_line,
#             sheet_name=payload.sheet_name,
#             params={
#                 "country": payload.country,
#                 "thickness": payload.thickness,
#                 "column": payload.column,
#             },
#             product=payload.product,
#         )
#         # upcharge_value = None
#         # if payload.upcharge is not None:
#         #     upcharge_value = get_upcharge(
#         #         product_line=payload.upcharge.product_line,
#         #         material=payload.upcharge.material,
#         #         category=payload.upcharge.category,
#         #         finish_type=payload.upcharge.finish_type,
#         #         country=payload.upcharge.country,
#         #     )
#         return {
#             "Price":{
#                 "Base Price": price,
#                 # "Upcharge": upcharge_value,
#             }
#         }   
#     except Exception as exc:
#         raise HTTPException(status_code=400, detail=str(exc))


# @app.post("/price/bars")
# def price_bars(payload: BarsRequest):
#     """
#     Get bar price from Excel based on label, depth, and height.
#     """
#     try:
#         price = get_price(
#             product_line=payload.product_line,
#             sheet_name=payload.sheet_name,
#             params={
#                 "label": payload.label,
#                 "depth": payload.depth,
#                 "height": payload.height,
#             },
#             product=payload.product,
#         )
#         return {"price": price}
#     except Exception as exc:
#         raise HTTPException(status_code=400, detail=str(exc))


# @app.post("/price/logos")
# def price_logos(payload: LogosRequest):
#     """
#     Get logo price from a square-inch table.
#     """
#     try:
#         price = get_price(
#             product_line=payload.product_line,
#             sheet_name=payload.sheet_name,
#             params={
#                 "label": payload.label,
#                 "row": payload.row,
#                 "col": payload.col,
#             },
#             product=payload.product,
#         )
#         return {"price": price}
#     except Exception as exc:
#         raise HTTPException(status_code=400, detail=str(exc))


@app.post("/price")
def price_by_type(
    category: str = Query(..., description="letters, bars, or logos"),
    body: dict = Body(...),
):
    """
    Single endpoint using query param:
    /price?pricing_type=letters|bars|logos
    Body contains the matching payload fields.
    """
    try:
        if category == "letters":
            data = LettersRequest(**body)
            price = get_price(
                product_line=data.product_line,
                sheet_name=data.sheet_name,
                params={
                    "country": data.country,
                    "thickness": data.thickness,
                    "column": data.height,
                },
                product=data.product,
            )
            # If get_price returns a dict, pull the base_price out
            base_price = price["base_price"] if isinstance(price, dict) else price

            # mapping:
            # frontend field -> upcharge category in Excel
            field_to_category = {
                "basecolorFinish": "Color/Finish:",
                "mountingOption": "Mounting Option",
            }

            # Collect all upcharges in one place
            upcharges = {}
            for field_name, upcharge_category in field_to_category.items():
                if field_name in body and body[field_name]:
                    upcharges[upcharge_category] = get_upcharge(
                        product_line=data.product_line,
                        material=body.get("material", "Aluminum"),
                        category=upcharge_category,
                        finish_type=body[field_name],
                        country=data.country,
                    )

            return {"Base price": base_price, "Upcharges": upcharges}
        if category == "bars":
            data = BarsRequest(**body)
            price = get_price(
                product_line=data.product_line,
                sheet_name=data.sheet_name,
                params={
                    "label": data.label,
                    "depth": data.depth,   
                    "height": data.height,
                },
                product=data.product,
            )
            return {"price": price}

        if category == "logos":
            data = LogosRequest(**body)
            price = get_price(
                product_line=data.product_line,
                sheet_name=data.sheet_name,
                params={
                    "label": data.label,
                    "row": data.row,
                    "col": data.col,
                },
                product=data.product,
            )
            return {"price": price}

        raise HTTPException(
            status_code=400,
            detail="pricing_type must be: letters, bars, or logos",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/upcharge")
def price_upcharge(payload: UpchargeRequest):
    """
    Get upcharge price for a material and finish type.
    """
    try:
        upcharge = get_upcharge(
            product_line=payload.product_line,
            material=payload.material,
            category=payload.category,
            finish_type=payload.finish_type,
            country=payload.country,
        )
        return {"upcharge": upcharge}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
