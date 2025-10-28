import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid
import os

class EcommerceDataGenerator:
    def __init__(self):
        self.products = self._generate_product_catalog()
        self.customers = self._generate_customer_list()
        self.coupons = self._generate_coupon_list()
        
    def _generate_product_catalog(self):
        """Generate a realistic product catalog with categories and costs"""
        products = []
        categories = {
            'Electronics': ['Smartphone', 'Laptop', 'Tablet', 'Headphones', 'Smartwatch', 'Camera'],
            'Clothing': ['T-Shirt', 'Jeans', 'Dress', 'Jacket', 'Shoes', 'Accessories'],
            'Home': ['Furniture', 'Kitchenware', 'Decor', 'Bedding', 'Lighting'],
            'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Children', 'Cookbook'],
            'Sports': ['Equipment', 'Apparel', 'Footwear', 'Accessories']
        }
        
        product_id = 1
        for category, items in categories.items():
            for item in items:
                base_cost = random.uniform(10, 500)
                selling_price = base_cost * random.uniform(1.2, 2.5)  # 20-150% markup
                products.append({
                    'product_id': product_id,
                    'product_name': f"{item} {random.choice(['Pro', 'Elite', 'Basic', 'Premium', 'Standard'])}",
                    'category': category,
                    'subcategory': item,
                    'base_cost': round(base_cost, 2),
                    'selling_price': round(selling_price, 2)
                })
                product_id += 1
                
        return products
    
    def _generate_customer_list(self):
        """Generate a list of customer names"""
        first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
                      'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
                      'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
                      'Matthew', 'Margaret', 'Anthony', 'Betty', 'Mark', 'Sandra']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                     'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
                     'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson']
        
        customers = []
        for i in range(500):  # 500 unique customers
            first = random.choice(first_names)
            last = random.choice(last_names)
            customers.append({
                'customer_id': i + 1,
                'customer_name': f"{first} {last}",
                'email': f"{first.lower()}.{last.lower()}@email.com",
                'customer_segment': random.choice(['Regular', 'Premium', 'VIP', 'New'])
            })
            
        return customers
    
    def _generate_coupon_list(self):
        """Generate various coupon codes"""
        coupons = [
            {'code': 'WELCOME10', 'discount_percent': 10, 'min_order': 0},
            {'code': 'SAVE15', 'discount_percent': 15, 'min_order': 50},
            {'code': 'SUMMER20', 'discount_percent': 20, 'min_order': 100},
            {'code': 'VIP25', 'discount_percent': 25, 'min_order': 200},
            {'code': 'FREESHIP', 'discount_percent': 0, 'min_order': 75, 'free_shipping': True},
            {'code': 'FLASH30', 'discount_percent': 30, 'min_order': 150}
        ]
        return coupons
    
    def _generate_order_date(self, base_date=None):
        """Generate random order dates within the last year"""
        if base_date is None:
            base_date = datetime.now()
        
        # Generate dates within the last 365 days
        days_ago = random.randint(0, 365)
        order_date = base_date - timedelta(days=days_ago)
        
        # Add random time within the day
        order_date = order_date.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return order_date
    
    def _calculate_discount(self, total_price, coupon):
        """Calculate discount based on coupon rules"""
        if coupon and total_price >= coupon['min_order']:
            if 'free_shipping' in coupon and coupon['free_shipping']:
                return min(15, total_price * 0.1)  # Assume shipping cost is $15 max
            else:
                return total_price * (coupon['discount_percent'] / 100)
        return 0
    
    def _detect_fraud_patterns(self, order_data):
        """Identify potential fraudulent orders based on patterns"""
        fraud_indicators = []
        
        # High value orders from new customers
        if (order_data['customer_segment'] == 'New' and 
            order_data['total_price'] > 500):
            fraud_indicators.append('High value new customer')
            
        # Multiple orders in short time
        if order_data['orders_in_last_hour'] > 3:
            fraud_indicators.append('Multiple orders in short time')
            
        # Unusual discount usage
        if (order_data['coupon_code'] and 
            order_data['total_discount'] / order_data['total_price'] > 0.5):
            fraud_indicators.append('High discount usage')
            
        # International shipping with expedited delivery
        if (order_data['shipping_country'] != 'USA' and 
            order_data['shipping_method'] == 'Express'):
            fraud_indicators.append('International express shipping')
            
        return ', '.join(fraud_indicators) if fraud_indicators else 'No indicators'
    
    def generate_orders(self, num_orders=100000):
        """Generate synthetic ecommerce order data"""
        orders = []
        customer_order_counts = {}
        customer_last_order_time = {}
        
        print(f"Generating {num_orders} synthetic ecommerce orders...")
        
        for i in range(num_orders):
            if (i + 1) % 10000 == 0:
                print(f"Generated {i + 1} orders...")
            
            # Select random customer and product
            customer = random.choice(self.customers)
            product = random.choice(self.products)
            
            customer_id = customer['customer_id']
            
            # Track customer order patterns for fraud detection
            current_time = self._generate_order_date()
            if customer_id in customer_last_order_time:
                time_since_last_order = (current_time - customer_last_order_time[customer_id]).total_seconds() / 3600
                orders_in_last_hour = sum(1 for t in customer_order_counts.get(customer_id, []) 
                                        if (current_time - t).total_seconds() / 3600 <= 1)
            else:
                time_since_last_order = float('inf')
                orders_in_last_hour = 0
            
            # Update customer order tracking
            if customer_id not in customer_order_counts:
                customer_order_counts[customer_id] = []
            customer_order_counts[customer_id].append(current_time)
            customer_last_order_time[customer_id] = current_time
            
            # Generate order details
            quantity = random.randint(1, 5)
            unit_price = product['selling_price']
            total_price = unit_price * quantity
            
            # Apply coupon randomly (20% of orders)
            coupon = random.choice(self.coupons + [None] * 4)
            coupon_code = coupon['code'] if coupon else None
            
            # Calculate discount
            total_discount = self._calculate_discount(total_price, coupon)
            final_price = total_price - total_discount
            
            # Calculate profit
            total_cost = product['base_cost'] * quantity
            profit = final_price - total_cost
            
            # Generate shipping information
            shipping_method = random.choice(['Standard', 'Express', 'Next Day'])
            shipping_country = random.choice(['USA', 'USA', 'USA', 'Canada', 'UK', 'Australia'])  # Weighted toward USA
            
            # Fraud detection
            fraud_data = {
                'customer_segment': customer['customer_segment'],
                'total_price': total_price,
                'coupon_code': coupon_code,
                'total_discount': total_discount,
                'orders_in_last_hour': orders_in_last_hour,
                'shipping_country': shipping_country,
                'shipping_method': shipping_method
            }
            fraud_indicators = self._detect_fraud_patterns(fraud_data)
            
            order = {
                'order_id': str(uuid.uuid4())[:8].upper(),
                'order_date': current_time,
                'customer_id': customer_id,
                'customer_name': customer['customer_name'],
                'customer_email': customer['email'],
                'customer_segment': customer['customer_segment'],
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'category': product['category'],
                'subcategory': product['subcategory'],
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': round(total_price, 2),
                'base_cost': round(total_cost, 2),
                'coupon_code': coupon_code,
                'total_discount': round(total_discount, 2),
                'final_price': round(final_price, 2),
                'profit': round(profit, 2),
                'shipping_method': shipping_method,
                'shipping_country': shipping_country,
                'payment_method': random.choice(['Credit Card', 'PayPal', 'Debit Card', 'Apple Pay']),
                'order_status': random.choice(['Delivered', 'Shipped', 'Processing', 'Cancelled']),
                'fraud_indicators': fraud_indicators,
                'is_high_risk': len(fraud_indicators) > 0 and fraud_indicators != 'No indicators'
            }
            
            orders.append(order)
        
        return pd.DataFrame(orders)
    
    def save_to_csv(self, df, filename='ecommerce_data.csv'):
        """Save generated data to CSV file"""
        # Create directory if it doesn't exist
        os.makedirs('generated_data', exist_ok=True)
        
        filepath = os.path.join('generated_data', filename)
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
        return filepath

def main():
    """Main function to generate and save synthetic data"""
    generator = EcommerceDataGenerator()
    
    # Generate 100,000 orders
    df = generator.generate_orders(100000)
    
    # Display basic information about the generated data
    print(f"\nGenerated dataset information:")
    print(f"Total orders: {len(df)}")
    print(f"Date range: {df['order_date'].min()} to {df['order_date'].max()}")
    print(f"Total revenue: ${df['final_price'].sum():,.2f}")
    print(f"Total profit: ${df['profit'].sum():,.2f}")
    print(f"Unique customers: {df['customer_id'].nunique()}")
    print(f"Unique products: {df['product_id'].nunique()}")
    print(f"Potential high-risk orders: {df['is_high_risk'].sum()}")
    
    # Save to CSV
    filepath = generator.save_to_csv(df)
    
    print(f"\nDataset columns: {list(df.columns)}")
    print(f"\nSample data:")
    print(df.head(3).to_string())
    
    return filepath

if __name__ == "__main__":
    main()