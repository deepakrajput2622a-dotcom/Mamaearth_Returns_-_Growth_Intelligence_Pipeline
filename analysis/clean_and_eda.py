import pandas as pd

# Load datasets
orders = pd.read_csv('orders.csv')
products = pd.read_csv('products.csv')
customers = pd.read_csv('customers.csv')

# Clean payment method
orders['payment_method'] = orders['payment_method'].str.strip().str.upper()

# Deduplicate
natural_key = ['customer_id', 'product_id', 'order_date', 'quantity', 
               'discount_pct', 'payment_method', 'rating', 'returned']
orders_clean = orders.drop_duplicates(subset=natural_key, keep='first').copy()

# Impute missing values
orders_clean['discount_pct'] = orders_clean['discount_pct'].fillna(0)
median_rating = orders_clean['rating'].median()
orders_clean['rating'] = orders_clean['rating'].fillna(median_rating)

# Merge datasets
merged_clean = orders_clean.merge(products, on='product_id', how='left').merge(customers, on='customer_id', how='left')
merged_clean['order_value'] = merged_clean['quantity'] * merged_clean['price'] * (1 - merged_clean['discount_pct'] / 100)

# IQR Outlier Detection
q1 = float(merged_clean['quantity'].quantile(0.25))
q3 = float(merged_clean['quantity'].quantile(0.75))
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
merged_clean['is_outlier'] = (merged_clean['quantity'] < lower) | (merged_clean['quantity'] > upper)

print("Data cleaning & EDA processing completed.")
