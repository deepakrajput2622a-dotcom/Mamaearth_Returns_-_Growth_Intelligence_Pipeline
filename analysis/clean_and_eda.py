import pandas as pd
import numpy as np

def run_pipeline():
    print("--- Task 1 & 2: Load and Clean Payment Methods ---")
    orders = pd.read_csv('orders.csv')
    products = pd.read_csv('products.csv')
    customers = pd.read_csv('customers.csv')
    
    # Standardize payment method
    orders['payment_method'] = orders['payment_method'].str.strip().str.upper()
    
    print("--- Task 3: Remove duplicate orders ---")
    natural_key = [
        'customer_id', 'product_id', 'order_date', 'quantity',
        'discount_pct', 'payment_method', 'rating', 'returned'
    ]
    dropped_orders = orders[orders.duplicated(subset=natural_key, keep='first')]
    dropped_order_ids = dropped_orders['order_id'].tolist()
    orders_clean = orders.drop_duplicates(subset=natural_key, keep='first').copy()
    print(f"Removed {len(dropped_order_ids)} duplicates: {dropped_order_ids}")
    
    print("--- Task 4: Impute missing values ---")
    orders_clean['discount_pct'] = orders_clean['discount_pct'].fillna(0)
    median_rating = orders_clean['rating'].median()
    orders_clean['rating'] = orders_clean['rating'].fillna(median_rating)
    
    print("--- Task 5: Merge datasets ---")
    merged_clean = (
        orders_clean.merge(products, on='product_id', how='left')
                    .merge(customers, on='customer_id', how='left')
    )
    merged_clean['order_value'] = (
        merged_clean['quantity'] * merged_clean['price'] * (1 - merged_clean['discount_pct'] / 100)
    )
    
    print("--- Task 6: IQR outlier detection ---")
    q1 = float(merged_clean['quantity'].quantile(0.25))
    q3 = float(merged_clean['quantity'].quantile(0.75))
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    merged_clean['is_outlier'] = (merged_clean['quantity'] < lower) | (merged_clean['quantity'] > upper)
    
    print("--- Task 7 & 8: Hypothesis and Segmentation ---")
    seg_returns = merged_clean.groupby(['payment_method', 'city_tier'])['returned'].agg(['count', 'mean'])
    print(seg_returns)
    
    print("--- Task 9: Correlation analysis ---")
    corr_cols = ['rating', 'returned', 'discount_pct', 'quantity']
    print(merged_clean[corr_cols].corr())
    
    print("--- Task 10: Time Series monthly revenue ---")
    merged_clean['year_month'] = pd.to_datetime(merged_clean['order_date']).dt.to_period('M').astype(str)
    monthly_no_outliers = merged_clean[~merged_clean['is_outlier']].groupby('year_month')['order_value'].sum()
    print(monthly_no_outliers)
    
    # Save the cleaned DataFrame for the visualization script to load
    merged_clean.to_csv('cleaned_data.csv', index=False)
    print("Cleaned dataset saved as cleaned_data.csv")

if __name__ == '__main__':
    run_pipeline()
