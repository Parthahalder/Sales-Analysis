import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
import matplotlib.pyplot as plt



# Upload or load data
df = pd.read_csv('sales_data_cleaned.csv')
# Connect to DB
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Partha@123",
    database="new_sales"
)

cursor = conn.cursor()

st.title("Sales & Margin Dashboard")

# Run Query
query = """
SELECT Product, SUM(turnover) AS Total_Sales, SUM(margin) AS Total_Margin
FROM sales_data_cleaned
GROUP BY product
"""
cursor.execute(query)
result = cursor.fetchall()

# Convert to DataFrame
df = pd.DataFrame(result, columns=["Product", "Total Sales", "Total Margin"])

# Display Table
st.subheader("Sales & Margin by Product")
st.dataframe(df)

# Plotting
fig, ax = plt.subplots()
df.plot(x="Product", y=["Total Sales", "Total Margin"], kind="bar", ax=ax)
st.pyplot(fig)
# 1. PEAK ORDER TIME AND QUANTITY
st.subheader("⏰ Peak Order Time & Quantity")

query1 = """
SELECT 
    HOUR(`Order Time`) AS hour_of_day,
    sum(`Quantity Ordered`) As Total_Quantity,
    COUNT(*) AS orders_count
FROM sales_data_cleaned
GROUP BY hour_of_day
ORDER BY hour_of_day;
"""
df1 = pd.read_sql_query(query1, conn)
fig1 = px.line(df1, x="hour_of_day", y="orders_count", title="Orders by Hour of Day")
fig2 = px.line(df1, x="hour_of_day", y="Total_Quantity", title="Quantity by Hour of Day")
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)
# 2. PREMIUM PRODUCTS VS BULK PRODUCTS
st.subheader("💎 Premium Products")

query2 = """
WITH product_summary AS (
    SELECT 
        Product,
        SUM(Turnover) AS total_turnover,
        SUM(Margin) AS total_margin,
        SUM(Margin) / SUM(Turnover) * 100 AS margin_pct
    FROM 
        sales_data_cleaned
    GROUP BY 
        Product
), avg_margin AS (
    SELECT 
        AVG(total_turnover) AS Avg_turnover,
        AVG(margin_pct) AS avg_margin_pct
    FROM 
        product_summary
)
SELECT 
    ps.Product,
    am.Avg_turnover,
    ps.total_turnover,
    ps.total_margin,
    ROUND(ps.margin_pct, 2) AS margin_percentage,
    ROUND(am.avg_margin_pct, 2) AS avg_margin_percentage
FROM 
    product_summary ps
CROSS JOIN 
    avg_margin am
WHERE 
    ps.margin_pct > am.avg_margin_pct
    and ps.total_turnover < am.Avg_turnover
ORDER BY 
    ps.total_turnover DESC;
"""
df2 = pd.read_sql_query(query2, conn)
st.dataframe(df2)
st.subheader("!! Bulk Products")
QUERY100 = """
WITH product_summary AS (
    SELECT 
        Product,
        SUM(Turnover) AS total_turnover,
        SUM(Margin) AS total_margin,
        SUM(Margin) / SUM(Turnover) * 100 AS margin_pct
    FROM 
        sales_data_cleaned
    GROUP BY 
        Product
), avg_margin AS (
    SELECT 
        AVG(total_turnover) AS Avg_turnover,
        AVG(margin_pct) AS avg_margin_pct
    FROM 
        product_summary
)
SELECT 
    ps.Product,
    am.Avg_turnover,
    ps.total_turnover,
    ps.total_margin,
    CONCAT(ROUND(ps.margin_pct, 2), '%') AS margin_percentage,
    ROUND(am.avg_margin_pct, 2) AS avg_margin_percentage
FROM 
    product_summary ps
CROSS JOIN 
    avg_margin am
WHERE 
    ps.margin_pct < am.avg_margin_pct
    and ps.total_turnover > am.Avg_turnover
ORDER BY 
    ps.total_turnover DESC;
"""
dATA2 = pd.read_sql_query(QUERY100, conn)
st.dataframe(dATA2)
# 3. TOP 5 PRODUCTS
st.subheader("🏆 Top 5 Products by Revenue")

query3 = """
SELECT `Product`, SUM(`Turnover`) AS total_revenue
FROM sales_data_cleaned
GROUP BY `Product`
ORDER BY total_revenue DESC
LIMIT 5;
"""
df3 = pd.read_sql_query(query3, conn)
fig3 = px.bar(df3, x="Product", y="total_revenue", title="Top 5 Revenue Generating Products")
st.plotly_chart(fig3, use_container_width=True)

# 4. UNIQUE PRODUCTS MONTHLY
st.subheader("📦 Unique Products Sold Each Month")

query4 = """
SELECT
    DATE_FORMAT(Order_Date, '%Y-%m') AS `Year-Month`,
    COUNT(DISTINCT `Product`) AS `Unique Products`
FROM
    sales_data_cleaned
GROUP BY
    `Year-Month`
ORDER BY
    `Year-Month`;
"""
df4 = pd.read_sql_query(query4, conn)
fig4 = px.line(df4, x="Year-Month", y="Unique Products", title="Unique Products Sold Over Time")
st.plotly_chart(fig4, use_container_width=True)

# 5. PRODUCT PERFORMANCE
st.subheader("📈 Product Performance (High Revenue & Count)")

query5 = """
SELECT `Product`,
    COUNT(`Product`) AS product_count,
    SUM(`Quantity Ordered`) AS total_quantity,
    SUM(`turnover`) AS total_turnover,
    SUM(`margin`) AS total_margin
FROM 
    sales_data_cleaned
GROUP BY 
    `Product`
HAVING 
    total_turnover > 1000
    AND product_count >= 10;
"""
df5 = pd.read_sql_query(query5, conn)
st.dataframe(df5)

# 6. PROFITABILITY PERCENTAGE
st.subheader("💰 Profitability by Product")

query6 = """
SELECT 
    `Product`,
    CONCAT(ROUND(SUM(`margin`) / SUM(`turnover`) * 100.00, 2), '%') AS profitability_percentage
FROM 
    sales_data_cleaned
GROUP BY 
    `Product`
ORDER BY 
    profitability_percentage DESC;
"""
df6 = pd.read_sql_query(query6, conn)
st.dataframe(df6)

# 7. CATEGORY SEGREGATION
st.subheader("🧾 Category-wise Sales Overview")

query7 = """
SELECT 
    category,
    Product,
    SUM(turnover) AS Total_Turnover,
    SUM(margin) AS Total_margin,
    SUM(`Quantity Ordered`) AS Total_Qty_Ordered
FROM 
    sales_data_cleaned
GROUP BY 
    category, Product
ORDER BY 
    category;
"""
df7 = pd.read_sql_query(query7, conn)
st.dataframe(df7)

# 8. TOP 3 PRODUCTS IN EACH STATE
st.subheader("🌎 Top 3 Products by State")

query8 = """
SELECT
    t1.state,
    t1.Product,
    ROUND(t1.total_turnover, 2) AS turnover
FROM (
    SELECT
        state,
        Product,
        SUM(turnover) AS total_turnover,
        RANK() OVER (PARTITION BY state ORDER BY SUM(turnover) DESC) AS rnk
    FROM sales_data_cleaned
    GROUP BY state, Product
) AS t1
WHERE t1.rnk <= 3
ORDER BY t1.state, t1.rnk;
"""
df8 = pd.read_sql_query(query8, conn)
st.dataframe(df8)
query9 = """
SELECT 
    `state`,
    `city`,
    ROUND(SUM(`turnover`), 2) AS total_turnover
FROM 
    sales_data_cleaned
GROUP BY 
    `state`, `city`
ORDER BY 
     total_turnover DESC;
"""
df9 = pd.read_sql_query(query9,conn)
st.dataframe(df9)
# Plot 1: Total turnover by state (aggregated)
state_turnover = df9.groupby("state")["total_turnover"].sum().sort_values(ascending=False)

fig1, ax1 = plt.subplots(figsize=(10, 6))
state_turnover.plot(kind="bar", ax=ax1, color="skyblue")
ax1.set_title("Total Turnover by State")
ax1.set_xlabel("State")
ax1.set_ylabel("Total Turnover")
st.pyplot(fig1)

# Plot 2: Top 10 cities by turnover
top_cities = df9.groupby("city")["total_turnover"].sum().sort_values(ascending=False).head(10)

fig2, ax2 = plt.subplots(figsize=(10, 6))
top_cities.plot(kind="bar", ax=ax2, color="lightgreen")
ax2.set_title("Top 10 Cities by Turnover")
ax2.set_xlabel("City")
ax2.set_ylabel("Total Turnover")
st.pyplot(fig2)

##- For running streamlit to deploy it in the web app the following code is executed standards ----###
##-- python -m streamlit run "c:/Users/DELL/OneDrive/Documents/PROJECTS/Python + SQL/conn.py" --##




#############-------------------THANK YOU---------------------##########################
















