CREATE INDEX idx_order_items_product_id
ON order_items(product_id);

CREATE INDEX idx_order_items_seller_id
ON order_items(seller_id);

CREATE INDEX idx_order_payments_order_id
ON order_payments(order_id);

CREATE INDEX idx_order_reviews_order_id
ON order_reviews(order_id);