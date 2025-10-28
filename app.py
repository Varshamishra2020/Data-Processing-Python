import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Ecommerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 2.8rem;
        color: #1a365d;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2d3748;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }
    .subsection-header {
        font-size: 1.4rem;
        color: #4a5568;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    .metric-card {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3182ce;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .fraud-alert {
        background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #e53e3e;
        margin: 1rem 0;
    }
    .insight-card {
        background: #f8fafc;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #48bb78;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f5f9;
        border-radius: 8px 8px 0px 0px;
        gap: 8px;
        padding: 12px 24px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3182ce;
        color: white;
    }
    .dataframe-table {
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

class EcommerceDashboard:
    def __init__(self):
        self.df = None
        self.original_df = None
        self.load_data()
    
    def load_data(self):
        """Load data from CSV file"""
        try:
            # File uploader in sidebar
            uploaded_file = st.sidebar.file_uploader(
                "Upload CSV File", 
                type="csv",
                help="Upload your ecommerce data CSV file"
            )
            
            if uploaded_file is not None:
                self.df = pd.read_csv(uploaded_file)
                self.original_df = self.df.copy()
                # Convert order_date to datetime
                self.df['order_date'] = pd.to_datetime(self.df['order_date'])
                st.sidebar.success(f"Data loaded successfully: {len(self.df):,} records")
            else:
                # Try to load default generated data
                try:
                    self.df = pd.read_csv('generated_data/ecommerce_data.csv')
                    self.original_df = self.df.copy()
                    self.df['order_date'] = pd.to_datetime(self.df['order_date'])
                    st.sidebar.info("Using default generated dataset")
                except Exception as e:
                    st.sidebar.warning(f"Please generate data first using data_generator.py. Error: {str(e)}")
                    st.info("""
                    **Demo Instructions:**
                    - Run `data_generator.py` first to create sample data
                    - Or upload your own CSV file using the sidebar uploader
                    - Required columns: order_date, total_price, profit, category, customer_segment, order_status
                    """)
                    return
                    
            # Display dataset info
            self.show_dataset_info()
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    def show_dataset_info(self):
        """Display basic dataset information"""
        if self.df is not None:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_revenue = self.df['total_price'].sum()
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            
            with col2:
                total_orders = len(self.df)
                st.metric("Total Orders", f"{total_orders:,}")
            
            with col3:
                total_profit = self.df['profit'].sum()
                st.metric("Total Profit", f"${total_profit:,.2f}")
            
            with col4:
                avg_order_value = self.df['total_price'].mean()
                st.metric("Average Order Value", f"${avg_order_value:.2f}")
    
    def create_filters(self):
        """Create interactive filters in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.header("Data Filters")
        
        if self.df is None or len(self.df) == 0:
            st.sidebar.warning("No data available for filtering")
            return
        
        # Store original data for reset functionality
        if self.original_df is not None:
            filtered_df = self.original_df.copy()
            filtered_df['order_date'] = pd.to_datetime(filtered_df['order_date'])
        else:
            filtered_df = self.df.copy()
        
        # Date range filter
        min_date = filtered_df['order_date'].min().date()
        max_date = filtered_df['order_date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['order_date'].dt.date >= start_date) & 
                (filtered_df['order_date'].dt.date <= end_date)
            ]
        
        # Category filter
        categories = ['All Categories'] + sorted(filtered_df['category'].unique().tolist())
        selected_category = st.sidebar.selectbox("Product Category", categories)
        if selected_category != 'All Categories':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        # Customer segment filter
        segments = ['All Segments'] + sorted(filtered_df['customer_segment'].unique().tolist())
        selected_segment = st.sidebar.selectbox("Customer Segment", segments)
        if selected_segment != 'All Segments':
            filtered_df = filtered_df[filtered_df['customer_segment'] == selected_segment]
        
        # Order status filter
        statuses = ['All Statuses'] + sorted(filtered_df['order_status'].unique().tolist())
        selected_status = st.sidebar.selectbox("Order Status", statuses)
        if selected_status != 'All Statuses':
            filtered_df = filtered_df[filtered_df['order_status'] == selected_status]
        
        # Price range filter
        min_price = float(filtered_df['total_price'].min())
        max_price = float(filtered_df['total_price'].max())
        
        price_range = st.sidebar.slider(
            "Price Range ($)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price)
        )
        filtered_df = filtered_df[
            (filtered_df['total_price'] >= price_range[0]) & 
            (filtered_df['total_price'] <= price_range[1])
        ]
        
        # Fraud risk filter (if column exists)
        if 'is_high_risk' in filtered_df.columns:
            fraud_filter = st.sidebar.radio("Fraud Risk Filter", ['All Orders', 'High Risk Only', 'Low Risk Only'])
            if fraud_filter == 'High Risk Only':
                filtered_df = filtered_df[filtered_df['is_high_risk'] == True]
            elif fraud_filter == 'Low Risk Only':
                filtered_df = filtered_df[filtered_df['is_high_risk'] == False]
        
        # Reset filters button
        if st.sidebar.button("Reset All Filters"):
            filtered_df = self.original_df.copy() if self.original_df is not None else self.df.copy()
            if 'order_date' in filtered_df.columns:
                filtered_df['order_date'] = pd.to_datetime(filtered_df['order_date'])
        
        # Update main dataframe with filtered data
        self.df = filtered_df
        
        # Show filter summary
        st.sidebar.markdown(f"**Filtered Results:** {len(self.df):,} records")
    
    def create_overview_dashboard(self):
        """Create overview dashboard with key metrics"""
        st.markdown('<div class="section-header">Business Performance Overview</div>', unsafe_allow_html=True)
        
        if self.df is None or len(self.df) == 0:
            st.warning("No data available with current filters")
            return
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_customers = self.df['customer_id'].nunique()
            st.metric("Unique Customers", f"{total_customers:,}")
        
        with col2:
            total_products = self.df['order_id'].nunique()
            st.metric("Unique Products", f"{total_products:,}")
        
        with col3:
            success_rate = (len(self.df[self.df['order_status'].isin(['Delivered', 'Shipped'])]) / len(self.df)) * 100
            st.metric("Order Success Rate", f"{success_rate:.1f}%")
        
        with col4:
            if 'total_discount' in self.df.columns and 'total_price' in self.df.columns:
                avg_discount = (self.df['total_discount'].sum() / self.df['total_price'].sum()) * 100
                st.metric("Average Discount Rate", f"{avg_discount:.1f}%")
            else:
                st.metric("Total Quantity", f"{self.df['quantity'].sum():,}")
        
        # Performance Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by category
            category_revenue = self.df.groupby('category')['total_price'].sum().sort_values(ascending=False)
            fig_category = px.bar(
                x=category_revenue.index,
                y=category_revenue.values,
                title='Revenue Distribution by Product Category',
                labels={'x': 'Category', 'y': 'Revenue ($)'},
                color=category_revenue.values,
                color_continuous_scale='Blues'
            )
            fig_category.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            # Sales trend analysis
            weekly_sales = self.df.resample('W', on='order_date').agg({
                'total_price': 'sum',
                'order_id': 'count'
            }).reset_index()
            
            if len(weekly_sales) > 0:
                fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig_trend.add_trace(go.Scatter(
                    x=weekly_sales['order_date'],
                    y=weekly_sales['total_price'],
                    name='Weekly Revenue',
                    line=dict(color='#2980b9', width=3)
                ), secondary_y=False)
                
                fig_trend.add_trace(go.Bar(
                    x=weekly_sales['order_date'],
                    y=weekly_sales['order_id'],
                    name='Weekly Orders',
                    opacity=0.3,
                    marker_color='#7f8c8d'
                ), secondary_y=True)
                
                fig_trend.update_layout(
                    title='Weekly Sales Trend Analysis',
                    xaxis_title='Week',
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                fig_trend.update_yaxes(title_text="Revenue ($)", secondary_y=False)
                fig_trend.update_yaxes(title_text="Number of Orders", secondary_y=True)
                
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Insufficient data for trend analysis with current filters")
        
        # Business Insights Section
        st.markdown('<div class="subsection-header">Strategic Business Insights</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Customer Value Analysis**")
            if 'customer_name' in self.df.columns:
                customer_value = self.df.groupby('customer_name').agg({
                    'total_price': 'sum',
                    'order_id': 'count',
                    'profit': 'sum'
                }).nlargest(5, 'total_price')
                
                for i, (customer, data) in enumerate(customer_value.iterrows(), 1):
                    customer_margin = (data['profit'] / data['total_price']) * 100 if data['total_price'] > 0 else 0
                    st.markdown(f"""
                    <div class="insight-card">
                        {i}. <strong>{customer}</strong><br>
                        Total Spend: ${data['total_price']:,.2f}<br>
                        Orders: {data['order_id']} | Margin: {customer_margin:.1f}%
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Customer name data not available")
        
        with col2:
            st.write("**Operational Efficiency**")
            
            # Payment methods pie chart
            if 'payment_method' in self.df.columns:
                payment_methods = self.df['payment_method'].value_counts()
                if len(payment_methods) > 0:
                    fig_payment = px.pie(
                        values=payment_methods.values,
                        names=payment_methods.index,
                        title='Payment Method Distribution',
                        hole=0.3
                    )
                    fig_payment.update_layout(height=500)
                    st.plotly_chart(fig_payment, use_container_width=True)
                else:
                    st.info("No payment method data available")
            else:
                st.info("Payment method data not available")
    
    def create_daily_profit_dashboard(self):
        """Create daily profit/loss dashboard"""
        st.markdown('<div class="section-header">Daily Profit & Loss Analysis</div>', unsafe_allow_html=True)
        
        if self.df is None or len(self.df) == 0:
            st.warning("No data available with current filters")
            return
        
        # Daily aggregation
        daily_data = self.df.groupby(self.df['order_date'].dt.date).agg({
            'total_price': 'sum',
            'profit': 'sum',
            'order_id': 'count',
            'quantity': 'sum'
        }).reset_index()
        
        # Add discount column if available
        if 'total_discount' in self.df.columns:
            daily_discount = self.df.groupby(self.df['order_date'].dt.date)['total_discount'].sum().reset_index()
            daily_data = daily_data.merge(daily_discount, on='order_date')
        else:
            daily_data['total_discount'] = 0
            
        daily_data.columns = ['date', 'revenue', 'profit', 'order_count', 'quantity_sold', 'discounts']
        
        if len(daily_data) == 0:
            st.warning("No daily data available with current filters")
            return
        
        # Calculate key metrics
        total_profit = daily_data['profit'].sum()
        profitable_days = len(daily_data[daily_data['profit'] > 0])
        profit_margin = (daily_data['profit'].sum() / daily_data['revenue'].sum()) * 100 if daily_data['revenue'].sum() > 0 else 0
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_daily_profit = daily_data['profit'].mean()
            st.metric("Average Daily Profit", f"${avg_daily_profit:,.2f}")
        with col2:
            profit_margin_display = f"{profit_margin:.1f}%"
            st.metric("Overall Profit Margin", profit_margin_display)
        with col3:
            st.metric("Profitable Days Ratio", f"{profitable_days}/{len(daily_data)}")
        with col4:
            max_daily_profit = daily_data['profit'].max()
            st.metric("Peak Daily Profit", f"${max_daily_profit:,.2f}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Profit trend with confidence interval
            fig_profit = px.line(
                daily_data, 
                x='date', 
                y='profit',
                title='Daily Profit Trend Analysis',
                labels={'profit': 'Profit ($)', 'date': 'Date'}
            )
            
            # Add confidence interval
            profit_std = daily_data['profit'].std()
            if profit_std > 0:
                fig_profit.add_trace(go.Scatter(
                    x=list(daily_data['date']) + list(daily_data['date'])[::-1],
                    y=list(daily_data['profit'] + profit_std) + list(daily_data['profit'] - profit_std)[::-1],
                    fill='toself',
                    fillcolor='rgba(46, 204, 113, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Profit Range (±1 std)'
                ))
            
            fig_profit.update_traces(line=dict(color='#2ecc71', width=4))
            fig_profit.update_layout(
                hovermode='x unified',
                showlegend=True,
                height=450,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_profit, use_container_width=True)
        
        with col2:
            # Revenue vs Profit correlation
            fig_comparison = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_comparison.add_trace(go.Bar(
                x=daily_data['date'],
                y=daily_data['revenue'],
                name='Revenue',
                marker_color='#3498db',
                opacity=0.7
            ), secondary_y=False)
            
            fig_comparison.add_trace(go.Scatter(
                x=daily_data['date'],
                y=daily_data['profit'],
                name='Profit',
                mode='lines+markers',
                line=dict(color='#2ecc71', width=4),
                marker=dict(size=6)
            ), secondary_y=True)
            
            fig_comparison.update_layout(
                title='Revenue vs Profit Correlation',
                xaxis_title='Date',
                hovermode='x unified',
                height=450,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            fig_comparison.update_yaxes(title_text="Revenue ($)", secondary_y=False)
            fig_comparison.update_yaxes(title_text="Profit ($)", secondary_y=True)
            
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Profitability Insights
        st.markdown('<div class="subsection-header">Profitability Insights</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            best_profit_day = daily_data.loc[daily_data['profit'].idxmax()]
            st.markdown(f"""
            <div class="insight-card">
                <strong>Most Profitable Day</strong><br>
                Date: {best_profit_day['date']}<br>
                Profit: ${best_profit_day['profit']:,.2f}<br>
                Revenue: ${best_profit_day['revenue']:,.2f}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            worst_profit_day = daily_data.loc[daily_data['profit'].idxmin()]
            st.markdown(f"""
            <div class="insight-card">
                <strong>Least Profitable Day</strong><br>
                Date: {worst_profit_day['date']}<br>
                Profit: ${worst_profit_day['profit']:,.2f}<br>
                Revenue: ${worst_profit_day['revenue']:,.2f}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_daily_orders = daily_data['order_count'].mean()
            st.markdown(f"""
            <div class="insight-card">
                <strong>Operational Metrics</strong><br>
                Avg Daily Orders: {avg_daily_orders:.1f}<br>
                Success Rate: {(profitable_days/len(daily_data)*100):.1f}%<br>
                Volatility: ${profit_std:,.2f}
            </div>
            """, unsafe_allow_html=True)
    
    def create_popular_products_dashboard(self):
        """Create popular products and categories dashboard"""
        st.markdown('<div class="section-header">Product Performance & Category Analysis</div>', unsafe_allow_html=True)
        
        if self.df is None or len(self.df) == 0:
            st.warning("No data available with current filters")
            return
        
        # Key product metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            best_selling_product = self.df.groupby('product_name')['quantity'].sum().idxmax()
            st.metric("Best Selling Product", best_selling_product[:20] + "..." if len(best_selling_product) > 20 else best_selling_product)
        
        with col2:
            most_profitable_product = self.df.groupby('product_name')['profit'].sum().idxmax()
            st.metric("Most Profitable Product", most_profitable_product[:20] + "..." if len(most_profitable_product) > 20 else most_profitable_product)
        
        with col3:
            avg_profit_margin = (self.df['profit'].sum() / self.df['total_price'].sum()) * 100 if self.df['total_price'].sum() > 0 else 0
            st.metric("Average Profit Margin", f"{avg_profit_margin:.1f}%")
        
        with col4:
            total_products = self.df['order_id'].nunique()
            st.metric("Unique Products", f"{total_products}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top products by revenue and profit
            top_products = self.df.groupby('product_name').agg({
                'quantity': 'sum',
                'total_price': 'sum',
                'profit': 'sum',
                'order_id': 'count'
            }).round(2)
            
            top_products['profit_margin'] = (top_products['profit'] / top_products['total_price']) * 100
            top_products_revenue = top_products.nlargest(10, 'total_price').reset_index()
            
            if len(top_products_revenue) > 0:
                fig_products = px.bar(
                    top_products_revenue,
                    x='total_price',
                    y='product_name',
                    orientation='h',
                    title='Top 10 Products by Revenue Generation',
                    labels={'total_price': 'Revenue ($)', 'product_name': 'Product'},
                    color='profit',
                    color_continuous_scale='Viridis'
                )
                fig_products.update_layout(
                    height=500,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_products, use_container_width=True)
        
        with col2:
            # Category performance analysis
            category_data = self.df.groupby('category').agg({
                'total_price': 'sum',
                'profit': 'sum',
                'order_id': 'count',
                'quantity': 'sum'
            }).reset_index()
            
            category_data['profit_margin'] = (category_data['profit'] / category_data['total_price']) * 100
            category_data['avg_order_value'] = category_data['total_price'] / category_data['order_id']
            
            if len(category_data) > 0:
                # Revenue distribution pie chart
                fig_pie = px.pie(
                    category_data,
                    values='total_price',
                    names='category',
                    title='Revenue Distribution by Category',
                    hole=0.4
                )
                fig_pie.update_layout(height=250)
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Profit margin bar chart
                fig_margin = px.bar(
                    category_data,
                    x='category',
                    y='profit_margin',
                    title='Profit Margin by Category',
                    labels={'profit_margin': 'Profit Margin (%)', 'category': 'Category'},
                    color='profit_margin',
                    color_continuous_scale='Reds'
                )
                fig_margin.update_layout(height=250)
                st.plotly_chart(fig_margin, use_container_width=True)
        
        # Product Performance Insights
        st.markdown('<div class="subsection-header">Product Performance Insights</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top 5 Products by Profit Margin**")
            if len(top_products) > 0:
                high_margin_products = top_products[top_products['total_price'] > top_products['total_price'].median()]
                if len(high_margin_products) > 0:
                    high_margin_products = high_margin_products.nlargest(5, 'profit_margin')
                    
                    for i, (product, data) in enumerate(high_margin_products.iterrows(), 1):
                        st.markdown(f"""
                        <div class="insight-card">
                            {i}. <strong>{product[:25]}{'...' if len(product) > 25 else ''}</strong><br>
                            Profit Margin: {data['profit_margin']:.1f}%<br>
                            Revenue: ${data['total_price']:,.2f}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No high margin products found")
            else:
                st.info("No product data available")
        
        with col2:
            st.write("**Category Performance Summary**")
            if len(category_data) > 0:
                for _, category in category_data.iterrows():
                    st.markdown(f"""
                    <div class="insight-card">
                        <strong>{category['category']}</strong><br>
                        Revenue: ${category['total_price']:,.2f}<br>
                        Margin: {category['profit_margin']:.1f}%<br>
                        Orders: {category['order_id']:,}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No category data available")
    
    def create_fraud_detection_dashboard(self):
        """Create fraud detection and risk analysis dashboard"""
        st.markdown('<div class="section-header">Fraud Detection & Risk Analysis</div>', unsafe_allow_html=True)
        
        if self.df is None or len(self.df) == 0:
            st.warning("No data available with current filters")
            return
        
        # Check if fraud detection columns exist
        if 'is_high_risk' not in self.df.columns:
            st.info("Fraud detection features require 'is_high_risk' column in the dataset")
            return
        
        # Fraud statistics
        high_risk_orders = self.df[self.df['is_high_risk'] == True]
        total_high_risk = len(high_risk_orders)
        high_risk_revenue = high_risk_orders['total_price'].sum()
        total_revenue = self.df['total_price'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("High Risk Orders", f"{total_high_risk:,}")
        
        with col2:
            st.metric("High Risk Revenue", f"${high_risk_revenue:,.2f}")
        
        with col3:
            risk_percentage = (total_high_risk / len(self.df)) * 100
            st.metric("Risk Percentage", f"{risk_percentage:.2f}%")
        
        with col4:
            revenue_at_risk = (high_risk_revenue / total_revenue) * 100 if total_revenue > 0 else 0
            st.metric("Revenue at Risk", f"{revenue_at_risk:.2f}%")
        
        if total_high_risk > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Fraud indicators analysis
                if 'fraud_indicators' in self.df.columns:
                    fraud_indicators = self.df[self.df['fraud_indicators'] != 'No indicators']
                    if len(fraud_indicators) > 0:
                        indicator_counts = {}
                        for indicators in fraud_indicators['fraud_indicators']:
                            if isinstance(indicators, str):
                                for indicator in indicators.split(', '):
                                    if indicator != 'No indicators':
                                        indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1
                        
                        if indicator_counts:
                            fig_indicators = px.bar(
                                x=list(indicator_counts.keys()),
                                y=list(indicator_counts.values()),
                                title='Fraud Indicators Frequency Analysis',
                                labels={'x': 'Fraud Indicator', 'y': 'Occurrence Count'},
                                color=list(indicator_counts.values()),
                                color_continuous_scale='Reds'
                            )
                            fig_indicators.update_layout(
                                height=450,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                            )
                            st.plotly_chart(fig_indicators, use_container_width=True)
            
            with col2:
                # Risk analysis by various dimensions
                risk_by_segment = self.df.groupby('customer_segment').agg({
                    'is_high_risk': 'mean',
                    'order_id': 'count'
                }).reset_index()
                risk_by_segment['risk_percentage'] = risk_by_segment['is_high_risk'] * 100
                
                fig_segment_risk = px.bar(
                    risk_by_segment,
                    x='customer_segment',
                    y='risk_percentage',
                    title='Risk Distribution Across Customer Segments',
                    labels={'risk_percentage': 'Risk Percentage (%)', 'customer_segment': 'Customer Segment'},
                    color='risk_percentage',
                    color_continuous_scale='Oranges'
                )
                fig_segment_risk.update_layout(
                    height=450,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_segment_risk, use_container_width=True)
            
            # High risk orders detailed analysis
            st.markdown('<div class="subsection-header">High Risk Orders Analysis</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**High Risk Order Characteristics**")
                avg_risk_order_value = high_risk_orders['total_price'].mean()
                common_risk_payment = high_risk_orders['payment_method'].mode()[0] if len(high_risk_orders) > 0 else 'N/A'
                common_risk_category = high_risk_orders['category'].mode()[0] if len(high_risk_orders) > 0 else 'N/A'
                
                st.markdown(f"""
                <div class="fraud-alert">
                    <strong>Key Risk Patterns Identified:</strong><br>
                    • Average High Risk Order Value: ${avg_risk_order_value:.2f}<br>
                    • Most Common Payment Method: {common_risk_payment}<br>
                    • Most Frequent Category: {common_risk_category}<br>
                    • Risk Concentration: {revenue_at_risk:.1f}% of total revenue
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.write("**Risk Mitigation Insights**")
                st.markdown(f"""
                <div class="insight-card">
                    <strong>Recommended Actions:</strong><br>
                    • Enhanced verification for {common_risk_payment} payments<br>
                    • Additional scrutiny for {common_risk_category} category<br>
                    • Order value threshold: ${avg_risk_order_value:.2f}+<br>
                    • Target reduction: {risk_percentage:.1f}% to 1.0%
                </div>
                """, unsafe_allow_html=True)
            
            # High risk orders table
            st.subheader("High Risk Orders Detailed View")
            display_columns = ['order_id', 'order_date', 'category', 'total_price', 'payment_method']
            if 'customer_name' in high_risk_orders.columns:
                display_columns.insert(2, 'customer_name')
            if 'fraud_indicators' in high_risk_orders.columns:
                display_columns.append('fraud_indicators')
                
            high_risk_display = high_risk_orders[display_columns].sort_values('total_price', ascending=False)
            
            st.dataframe(
                high_risk_display.head(15),
                use_container_width=True,
                height=400
            )
        else:
            st.success("No high-risk orders detected in the current dataset with applied filters.")
    
    def create_data_explorer(self):
        """Create interactive data explorer"""
        st.markdown('<div class="section-header">Data Explorer & Advanced Analytics</div>', unsafe_allow_html=True)
        
        if self.df is None or len(self.df) == 0:
            st.warning("No data available with current filters")
            return
        
        # Advanced analytics section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Customer Lifetime Value Analysis")
            customer_ltv = self.df.groupby('customer_id').agg({
                'total_price': 'sum',
                'order_id': 'count',
                'profit': 'sum'
            }).round(2)
            
            customer_ltv.columns = ['total_spent', 'order_count', 'total_profit']
            customer_ltv['avg_order_value'] = customer_ltv['total_spent'] / customer_ltv['order_count']
            customer_ltv = customer_ltv.sort_values('total_spent', ascending=False)
            
            st.dataframe(
                customer_ltv.head(10),
                use_container_width=True,
                height=300
            )
        
        with col2:
            st.subheader("Seasonality Analysis")
            monthly_data = self.df.resample('M', on='order_date').agg({
                'total_price': 'sum',
                'profit': 'sum',
                'order_id': 'count'
            }).reset_index()
            
            if len(monthly_data) > 0:
                fig_seasonality = px.line(
                    monthly_data,
                    x='order_date',
                    y='total_price',
                    title='Monthly Revenue Trend',
                    labels={'order_date': 'Month', 'total_price': 'Revenue ($)'}
                )
                fig_seasonality.update_layout(height=300)
                st.plotly_chart(fig_seasonality, use_container_width=True)
            else:
                st.info("Insufficient data for seasonality analysis")
        
        # Interactive data table
        st.subheader("Interactive Data Table")
        
        # Column selector
        available_columns = self.df.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to display:",
            available_columns,
            default=['order_id', 'order_date', 'customer_name', 'product_name', 'category', 'total_price', 'order_status']
        )
        
        if selected_columns:
            display_df = self.df[selected_columns]
            
            # Search functionality
            search_term = st.text_input("Search across all columns:")
            if search_term:
                mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                display_df = display_df[mask]
            
            if len(display_df) > 0:
                # Pagination
                page_size = st.selectbox("Rows per page", [10, 25, 50, 100])
                total_pages = max(1, len(display_df) // page_size)
                page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
                
                start_idx = (page_number - 1) * page_size
                end_idx = start_idx + page_size
                
                st.dataframe(
                    display_df.iloc[start_idx:end_idx],
                    use_container_width=True,
                    height=600
                )
                
                st.write(f"Showing records {start_idx + 1} to {min(end_idx, len(display_df))} of {len(display_df)} total records")
            else:
                st.info("No data matches your search criteria")
        else:
            st.info("Please select columns to display")
    
    def run(self):
        """Run the complete dashboard"""
        st.markdown('<div class="main-header">Ecommerce Analytics Dashboard</div>', unsafe_allow_html=True)
        
        # Load data and create filters
        self.create_filters()
        
        if self.df is None or len(self.df) == 0:
            st.error("No data available. Please check your filters or upload a file.")
            return
        
        # Create tabs for different dashboards
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Business Overview", 
            "Profit Analysis", 
            "Product Performance", 
            "Fraud Detection",
            "Data Explorer"
        ])
        
        with tab1:
            self.create_overview_dashboard()
        
        with tab2:
            self.create_daily_profit_dashboard()
        
        with tab3:
            self.create_popular_products_dashboard()
        
        with tab4:
            self.create_fraud_detection_dashboard()
        
        with tab5:
            self.create_data_explorer()

def main():
    """Main function to run the dashboard"""
    try:
        dashboard = EcommerceDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"An error occurred while running the dashboard: {str(e)}")
        st.info("Please check your data file and try again. If the problem persists, contact support.")

if __name__ == "__main__":
    main()