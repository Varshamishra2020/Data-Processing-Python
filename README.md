### 📄 Overview

This project is a **Python-based data processing and analytics dashboard** built using **Streamlit**.
It generates **synthetic eCommerce order transaction data** and provides **interactive dashboards** to explore and analyze insights such as **profit/loss**, **popular products**, and **potential fraud detection**.

1. Generate synthetic order data (100,000+ records)
2. Load and visualize data dynamically via Streamlit
3. Analyze and visualize:

   * Daily Profit/Loss trends
   * Most popular products or categories
   * Fraud detection insights
4. Enable user-driven filtering and CSV uploads

---

### ⚙️ Features

#### 🧩 Data Generation

* Script generates a large dataset using **Faker** and **NumPy**
* CSV includes fields:

  ```
  order_id, customer_name, customer_id, order_date, product_name, category,
  quantity, cost_price, selling_price, total_price, total_discount, coupon_code,
  payment_method, city, country, is_fraud
  ```

#### 📊 Streamlit Dashboards

* **📁 CSV Loader:** Upload and preview any CSV file
* **💰 Daily Profit/Loss Dashboard:** Calculates profits using cost and sale price per item
* **🔥 Popular Products Dashboard:** Displays top-selling products and categories
* **🎯 Filtering System:** Filter by date, category, payment method, or region
* **🚨 Fraud Detection (Bonus):** Highlights suspicious orders based on:

  * unusually high discounts
  * large order totals
  * repetitive coupon usage
  * same user with multiple large transactions in short time


#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Varshamishra2020/Data-Processing-Python.git
cd Data-Processing-Python
```


#### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4️⃣ Generate Synthetic Data

```bash
python generate_data.py
```

This will create a large CSV file under `data/synthetic_orders.csv`.

#### 5️⃣ Run the Streamlit App

```bash
streamlit run app.py
```

Then open the displayed local URL in your browser (usually [http://localhost:8501](http://localhost:8501)).

---
