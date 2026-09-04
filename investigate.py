import pandas as pd


# Load datasets
df = pd.read_csv("Project-Data/raw/olist_orders_dataset.csv")
items = pd.read_csv("Project-Data/raw/olist_order_items_dataset.csv")
products = pd.read_csv("Project-Data/raw/olist_products_dataset.csv")
sellers = pd.read_csv("Project-Data/raw/olist_sellers_dataset.csv")
customers = pd.read_csv("Project-Data/raw/olist_customers_dataset.csv")

# --------------------------------------------------
# ORDERS
# --------------------------------------------------

# print(df.shape)
# print(df.columns)
# print(df.columns.tolist())
# print(df["order_id"].nunique())
# print(len(df))
# print(df.isna().sum())
# print(df["order_status"].value_counts())
# print(
#     df[df["order_delivered_customer_date"].isna()]
#     ["order_status"]
#     .value_counts()
# )
# print(
#     df[
#         (df["order_status"] == "delivered")
#         & (df["order_delivered_customer_date"].isna())
#     ].to_string(index=False)
# )


# --------------------------------------------------
# ORDER ITEMS
# --------------------------------------------------

# print(
#     items[
#         items["order_id"] == "2d1e2d5bf4dc7227b3bfebb81328c15f"
#     ]
# )

# print(items["order_id"].value_counts().head(10))

# print(items["order_item_id"].nunique())

# print(len(items))

# print(
#     items[
#         ["order_id", "order_item_id"]
#     ].drop_duplicates().shape
# )

# print(items.shape)

# print(
#     items["order_id"]
#     .isin(df["order_id"])
#     .value_counts()
# )

# print(
#     items["order_id"]
#     .value_counts()
#     .value_counts()
#     .sort_index()
# )

# print(items["product_id"].nunique())

# print(items["product_id"].isna().sum())

# print(items["product_id"].value_counts().head(10))


# --------------------------------------------------
# PRODUCTS
# --------------------------------------------------

# print(
#     items["product_id"]
#     .isin(products["product_id"])
#     .value_counts()
# )

# print(products.shape)

# print(products["product_id"].nunique())


# --------------------------------------------------
# SELLERS
# --------------------------------------------------

# print(items.columns.tolist())

# print(items["seller_id"].nunique())

# print(items["seller_id"].isna().sum())

# print(sellers.shape)

# print(sellers["seller_id"].nunique())

# print(
#     items["seller_id"]
#     .isin(sellers["seller_id"])
#     .value_counts()
# )


# --------------------------------------------------
# SHIPPING LIMIT INVESTIGATION
# --------------------------------------------------

# print(items["shipping_limit_date"].isna().sum())

# print(items["shipping_limit_date"].dtype)

# print(items[["price", "freight_value"]].describe())

# print(items[["price", "freight_value"]].dtypes)

# dup_product = items.duplicated(
#     subset=["order_id", "product_id"],
#     keep=False
# )

# print(dup_product.sum())

# repeated_products = items[dup_product]

# print(
#     repeated_products
#     .head(10)
#     .to_string(index=False)
# )


# --------------------------------------------------
# TIMESTAMP INVESTIGATION
# --------------------------------------------------

# print(df["order_purchase_timestamp"].dtype)

# print(items["shipping_limit_date"].dtype)

# print(df["order_purchase_timestamp"].head())

# print(items["shipping_limit_date"].head())


order_purchase = pd.to_datetime(
    df["order_purchase_timestamp"]
)

shipping_limit = pd.to_datetime(
    items["shipping_limit_date"]
)


items_check = items.merge(
    df[["order_id", "order_purchase_timestamp"]],
    on="order_id",
    how="left"
)


items_check["order_purchase_timestamp"] = pd.to_datetime(
    items_check["order_purchase_timestamp"]
)

items_check["shipping_limit_date"] = pd.to_datetime(
    items_check["shipping_limit_date"]
)


# print(
#     (
#         items_check["shipping_limit_date"]
#         < items_check["order_purchase_timestamp"]
#     ).sum()
# )


items_check["shipping_limit_time"] = (
    items_check["shipping_limit_date"]
    - items_check["order_purchase_timestamp"]
)


# print(
#     items_check["shipping_limit_time"].describe()
# )


# print(
#     items_check.loc[
#         items_check["shipping_limit_time"].idxmax()
#     ].to_string()
# )


# print(
#     df[
#         df["order_id"]
#         == "13bdf405f961a6deec817d817f5c6624"
#     ].to_string(index=False)
# )


# print(
#     items[
#         items["order_id"]
#         == "13bdf405f961a6deec817d817f5c6624"
#     ].to_string(index=False)
# )


# print(
#     (
#         items_check["shipping_limit_time"]
#         > pd.Timedelta(days=30)
#     ).sum()
# )


# print(
#     items_check[
#         items_check["shipping_limit_time"]
#         > pd.Timedelta(days=30)
#     ][
#         [
#             "order_id",
#             "shipping_limit_date",
#             "order_purchase_timestamp",
#             "shipping_limit_time"
#         ]
#     ]
#     .sort_values(
#         "shipping_limit_time",
#         ascending=False
#     )
#     .head(20)
#     .to_string(index=False)
# )


# print(
#     items_check[
#         items_check["shipping_limit_time"]
#         > pd.Timedelta(days=1000)
#     ][
#         [
#             "order_id",
#             "product_id",
#             "seller_id",
#             "shipping_limit_date",
#             "order_purchase_timestamp"
#         ]
#     ].to_string(index=False)
# )


# print(
#     items_check[
#         items_check["shipping_limit_time"]
#         > pd.Timedelta(days=1000)
#     ]["seller_id"].value_counts()
# )


# --------------------------------------------------
# SELLER ANOMALY INVESTIGATION
# --------------------------------------------------

seller_id = "7a241947449cc45dbfda4f9d0798d9d0"

seller_items = items_check[
    items_check["seller_id"] == seller_id
]


# print(seller_items.shape)

# print(seller_items["shipping_limit_time"].describe())

# print(
#     seller_items[
#         seller_items["shipping_limit_time"]
#         > pd.Timedelta(days=30)
#     ]["shipping_limit_time"].sort_values()
# )


# anomalous_orders = items_check[
#     items_check["shipping_limit_time"]
#     > pd.Timedelta(days=1000)
# ]


# print(
#     anomalous_orders[
#         ["order_id", "product_id", "seller_id"]
#     ]
#     .drop_duplicates()
#     .to_string(index=False)
# )


# product_ids = [
#     "96ea060e41bdecc64e2de00b97068975",
#     "282b126b2354516c5f400154398f616d",
#     "87b92e06b320e803d334ac23966c80b1"
# ]


# print(
#     products[
#         products["product_id"].isin(product_ids)
#     ].to_string(index=False)
# )


# print(
#     seller_items[
#         [
#             "order_id",
#             "order_purchase_timestamp",
#             "shipping_limit_date"
#         ]
#     ]
#     .sort_values("shipping_limit_date")
#     .tail(10)
#     .to_string(index=False)
# )


# --------------------------------------------------
# CUSTOMER INVESTIGATION
# --------------------------------------------------

print(customers["customer_id"].nunique())

print(len(customers))

print(customers["customer_unique_id"].nunique())