ORDERS_SCHEMA = {
    "order_id": "TEXT PRIMARY KEY",
    "customer_id": "TEXT NOT NULL",
    "order_status": "TEXT NOT NULL",
    "order_purchase_timestamp": "TIMESTAMP NOT NULL",
    "order_approved_at": "TIMESTAMP",
    "order_delivered_carrier_date": "TIMESTAMP",
    "order_delivered_customer_date": "TIMESTAMP",
    "order_estimated_delivery_date": "TIMESTAMP NOT NULL"
}


ORDER_ITEMS_SCHEMA = {
    "order_id": "TEXT NOT NULL",
    "order_item_id": "INTEGER NOT NULL",
    "product_id": "TEXT NOT NULL",
    "seller_id": "TEXT NOT NULL",
    "shipping_limit_date": "TIMESTAMP NOT NULL",
    "price": "NUMERIC(12, 2) NOT NULL",
    "freight_value": "NUMERIC(12, 2) NOT NULL",
    "PRIMARY KEY": "(order_id, order_item_id)"
}


PRODUCTS_SCHEMA = {
    "product_id": "TEXT PRIMARY KEY",
    "product_category_name": "TEXT",
    "product_name_lenght": "INTEGER",
    "product_description_lenght": "INTEGER",
    "product_photos_qty": "INTEGER",
    "product_weight_g": "INTEGER",
    "product_length_cm": "INTEGER",
    "product_height_cm": "INTEGER",
    "product_width_cm": "INTEGER"
}


SELLERS_SCHEMA = {
    "seller_id": "TEXT PRIMARY KEY",
    "seller_zip_code_prefix": "INTEGER NOT NULL",
    "seller_city": "TEXT NOT NULL",
    "seller_state": "TEXT NOT NULL"
}


CUSTOMERS_SCHEMA = {
    "customer_id": "TEXT PRIMARY KEY",
    "customer_unique_id": "TEXT NOT NULL",
    "customer_zip_code_prefix": "INTEGER NOT NULL",
    "customer_city": "TEXT NOT NULL",
    "customer_state": "TEXT NOT NULL"
}


ORDER_PAYMENTS_SCHEMA = {
    "order_id": "TEXT NOT NULL",
    "payment_sequential": "INTEGER NOT NULL",
    "payment_type": "TEXT NOT NULL",
    "payment_installments": "INTEGER NOT NULL",
    "payment_value": "NUMERIC(12, 2) NOT NULL",
    "PRIMARY KEY": "(order_id, payment_sequential)"
}


ORDER_REVIEWS_SCHEMA = {
    "review_id": "TEXT PRIMARY KEY",
    "order_id": "TEXT NOT NULL",
    "review_score": "INTEGER NOT NULL",
    "review_comment_title": "TEXT",
    "review_comment_message": "TEXT",
    "review_creation_date": "TIMESTAMP",
    "review_answer_timestamp": "TIMESTAMP"
}