import sqlite3
import pandas as pd

def get_connection():
    return sqlite3.connect("sales.db")

def yoy_growth():
    sql = """
    WITH yearly AS (
        SELECT year,
               SUM(sales)  AS total_sales,
               SUM(profit) AS total_profit
        FROM orders
        GROUP BY year
    ),
    yoy AS (
        SELECT year,
               total_sales,
               total_profit,
               LAG(total_sales)  OVER (ORDER BY year) AS prev_sales,
               LAG(total_profit) OVER (ORDER BY year) AS prev_profit
        FROM yearly
    )
    SELECT year,
           total_sales,
           total_profit,
           ROUND(100.0 * (total_sales - prev_sales) / prev_sales, 2) AS sales_growth_pct,
           ROUND(100.0 * (total_profit - prev_profit) / prev_profit, 2) AS profit_growth_pct
    FROM yoy
    """
    return pd.read_sql(sql, get_connection())

def regional_performance():
    sql = """
    SELECT region,
           category,
           SUM(sales)   AS total_sales,
           SUM(profit)  AS total_profit,
           COUNT(DISTINCT order_id) AS num_orders,
           ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS profit_margin_pct,
           RANK() OVER (PARTITION BY region ORDER BY SUM(sales) DESC) AS category_rank
    FROM orders
    GROUP BY region, category
    ORDER BY region, total_sales DESC
    """
    return pd.read_sql(sql, get_connection())

def top_products():
    sql = """
    SELECT sub_category,
           SUM(sales)  AS total_sales,
           SUM(profit) AS total_profit,
           ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS margin_pct,
           DENSE_RANK() OVER (ORDER BY SUM(profit) DESC) AS profit_rank
    FROM orders
    GROUP BY sub_category
    ORDER BY total_profit DESC
    LIMIT 15
    """
    return pd.read_sql(sql, get_connection())

def customer_segments():
    sql = """
    SELECT segment,
           COUNT(DISTINCT customer_id) AS num_customers,
           SUM(sales)   AS total_sales,
           SUM(profit)  AS total_profit,
           ROUND(SUM(sales) / COUNT(DISTINCT customer_id), 2) AS avg_revenue_per_customer
    FROM orders
    GROUP BY segment
    """
    return pd.read_sql(sql, get_connection())

def sales_over_time(region=None, category=None):
    filters = []
    if region and region != "All":
        filters.append(f"region = '{region}'")
    if category and category != "All":
        filters.append(f"category = '{category}'")
    where = "WHERE " + " AND ".join(filters) if filters else ""
    sql = f"""
    SELECT strftime('%Y-%m', order_date) AS month,
           SUM(sales)  AS monthly_sales,
           SUM(profit) AS monthly_profit
    FROM orders
    {where}
    GROUP BY month
    ORDER BY month
    """
    return pd.read_sql(sql, get_connection())
    