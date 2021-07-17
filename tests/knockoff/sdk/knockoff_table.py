# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import numpy as np
import pandas as pd

from knockoff.sdk.table import KnockoffTable
from knockoff.sdk.factory.collections import KnockoffDataFrameFactory
from knockoff.sdk.constraints import KnockoffUniqueConstraint
from knockoff.sdk.factory.column import ColumnFactory, FakerFactory, ChoiceFactory
from knockoff.sdk.factory.collections import KnockoffTableFactory

PRODUCT_TABLE_NAME = "product"
LOCATION_TABLE_NAME = "location"
TRANSACTION_TABLE_NAME = "transaction"


def size_factory(division):
    return {
        "Apparel": ChoiceFactory(["XS", "S", "M", "L", "XL", "XXL"]),
        "Shoes": FakerFactory("pyint", min_value=4, max_value=16),
    }[division]()


shoes_categories = [
    "Lifestyle",
    "Running",
    "Basketball",
    "Jordan",
    "Training & Gym",
    "Soccer",
    "Golf",
    "Cross Country",
    "Skateboarding",
    "Tennis",
    "Baseball",
    "Sandals & Slides"
]

apparel_categories = [
    "Tops & T-Shirts",
    "Shorts",
    "Hoodies & Sweatshirts",
    "Pants & Tights",
    "Matching Sets",
    "Jackets & Vests",
    "Swimwear",
    "Polos",
    "Yoga",
    "Socks",
    "Underwear",
    "Big & Tall",
    "Sustainable Materials"
]


def cartesian_product(values, names):
    return pd.DataFrame(
        index=pd.MultiIndex.from_product(
            values,
            names=names
        )
    ).reset_index()


shoes = cartesian_product(
    [["Shoes"], shoes_categories],
    names=["division", "category"]
)


apparel = cartesian_product(
    [["Apparel"], apparel_categories],
    names=["division", "category"]
)


hierarchy = pd.concat([shoes, apparel])


PRODUCT_TABLE = KnockoffTable(
    PRODUCT_TABLE_NAME,
    columns=[
        "division",
        "category",
        "gender",
        "color",
        "size",
        "sku",
        "price"
    ],
    factories=[
        KnockoffDataFrameFactory(hierarchy),
        ColumnFactory("gender", ChoiceFactory(["Mens", "Womens"])),
        ColumnFactory("color", FakerFactory("color_name")),
        ColumnFactory("size", size_factory, depends_on=["division"]),
        ColumnFactory("sku", FakerFactory("numerify", text="%#########")),
        ColumnFactory("price", FakerFactory("pyfloat", right_digits=2, min_value=5, max_value=300)),
    ],
    constraints=[KnockoffUniqueConstraint(["sku"])],
    size=20
)


LOCATION_TABLE = KnockoffTable(
    LOCATION_TABLE_NAME,
    columns=[
        "location_id",
        "address",
    ],
    factories=[
        ColumnFactory("location_id", FakerFactory("numerify", text="%###")),
        ColumnFactory("address", FakerFactory("address")),
    ],
    constraints=[KnockoffUniqueConstraint(["location_id"])],
    size=3
)


# create a demand function
def sales_func():
    return max(np.random.poisson(1), 1)


# create a revenue function based on price and units
def revenue_func(price, units):
    return price*float(units)


TRANSACTION_TABLE = KnockoffTable(
    TRANSACTION_TABLE_NAME,
    columns=[
        "location_id",
        "sku",
        "units",
        "revenue",
        "date"
    ],
    factories=[
        KnockoffTableFactory(PRODUCT_TABLE, columns=["sku", "price"]),
        KnockoffTableFactory(LOCATION_TABLE, columns=["location_id"]),
        ColumnFactory("units", sales_func),
        ColumnFactory("revenue", revenue_func, depends_on=["price", "units"]),
        ColumnFactory("date", FakerFactory("date_between", start_date="-2y", end_date="today")),
    ],
    size=50
)
