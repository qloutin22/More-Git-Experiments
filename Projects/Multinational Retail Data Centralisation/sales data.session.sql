
UPDATE dim_store_details
SET latitude = COALESCE(lat, latitude); 

ALTER TABLE dim_store_details DROP COLUMN lat;


UPDATE orders_table
SET product_price = REPLACE(product_price, '£', '');


UPDATE products_table
SET weight_class =
    CASE
        WHEN weight < 2 THEN 'Light'
        WHEN weight >= 2 AND weight < 40 THEN 'Mid_Sized'
        WHEN weight >= 40 AND weight < 140 THEN 'Heavy'
        ELSE 'Truck_Required'
    END;
