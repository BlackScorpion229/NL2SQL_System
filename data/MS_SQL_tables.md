## ✅ FINAL – MySQL-safe CREATE TABLE script

### 1️⃣ customers

```sql
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    country VARCHAR(50),
    state VARCHAR(50),
    city VARCHAR(50),
    postal_code VARCHAR(10),
    customer_segment ENUM('Premium','Standard','Budget'),
    registration_date DATE,
    last_purchase_date DATE,
    is_active TINYINT(1) DEFAULT 1,
    KEY idx_customer_segment (customer_segment),
    KEY idx_location (country, state, city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2️⃣ suppliers

```sql
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100),
    contact_person VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(15),
    country VARCHAR(50),
    city VARCHAR(50),
    address VARCHAR(255),
    payment_terms VARCHAR(50),
    lead_time_days INT,
    is_active TINYINT(1) DEFAULT 1,
    registration_date DATE,
    KEY idx_supplier_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 3️⃣ products

```sql
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    sub_category VARCHAR(50),
    brand VARCHAR(50),
    description TEXT,
    price DECIMAL(10,2),
    cost DECIMAL(10,2),
    stock_quantity INT,
    reorder_level INT,
    supplier_id INT,
    is_discontinued TINYINT(1) DEFAULT 0,
    created_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_category (category, sub_category),
    KEY idx_supplier_id (supplier_id),
    CONSTRAINT fk_products_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4️⃣ orders

```sql
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    delivery_date DATE,
    total_amount DECIMAL(12,2),
    discount_applied DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    order_status ENUM('Pending','Shipped','Delivered','Cancelled','Returned'),
    payment_method ENUM('Credit Card','Debit Card','PayPal','Cash'),
    notes TEXT,
    KEY idx_order_date (order_date),
    KEY idx_order_status (order_status),
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5️⃣ order_items

```sql
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    line_total DECIMAL(12,2),
    discount_percent DECIMAL(5,2),
    tax_percent DECIMAL(5,2),
    item_status ENUM('Pending','Shipped','Delivered','Cancelled'),
    notes VARCHAR(255),
    KEY idx_order_id (order_id),
    KEY idx_product_id (product_id),
    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

End of final code. Happy querying! 🎉

| Table       | Ideal Record Count      | Why this works                              |
| ----------- | ----------------------- | ------------------------------------------- |
| customers   | **5,000 – 20,000**      | Enough diversity for segments, geo, cohorts |
| suppliers   | **50 – 300**            | Realistic retail supplier spread            |
| products    | **1,000 – 5,000**       | Rich category & pricing analytics           |
| orders      | **50,000 – 300,000**    | Time-series + behavioral depth              |
| order_items | **150,000 – 1,000,000** | Where analytics actually live               |

# Recommended “Perfect Demo Dataset”
customers     → 10,000
suppliers     → 100
products      → 2,500
orders        → 120,000
order_items   → 450,000

---
# Business Questions for Analytics / NL-to-SQL
---

## 1. Customer-related questions

- How many active customers do we have?
- List all customers from Tennessee.
- Who are the Premium customers?
- Customers who have not purchased in the last 1 year.
- Total customers by country.
- Show customers registered in 2024.
- Which customers are inactive?
- Top 5 customers by total purchase amount.

## 2. Order-related questions

- How many orders are Delivered?
- Show all Cancelled orders.
- Total sales amount by month.
- Orders placed in 2023.
- Average order value.
- Orders with Returned status.
- Which payment method is used most?
- Orders with shipping cost more than 15.

## 3. Order item (line-level) questions

- Total quantity sold per product.
- Total revenue by product.
- Which items are Cancelled?
- Average discount percent per product.
- Order items with Pending status.
- Total tax collected per order.
- Top 5 products by line total.

## 4. Product-related questions

- List all Electronics products.
- Products that are discontinued.
- Products with stock below reorder level.
- Total products by category.
- Average price by category.
- Top 3 most expensive products.
- Products created in 2024.

## 5. Supplier-related questions

- List all active suppliers.
- Suppliers from United Kingdom.
- Average lead time by supplier.
- Suppliers with Net 60 payment terms.
- How many products per supplier?
- Recently registered suppliers.

## 6. Cross-table (joins) questions ⭐  
*(Very important for NL-to-SQL)*

- Total sales by customer.
- Customer name with their total orders.
- Products sold in Delivered orders.
- Revenue by product category.
- Supplier name for each product.
- Customers who bought Electronics products.
- Orders and their item details.
- Products sold by each supplier.

## 7. Business / analytics questions

- Monthly revenue trend.
- Best-selling product category.
- Top 5 customers by revenue.
- Total discount given this year.
- Total tax collected.
- Which products generate highest profit?  
  *(price – cost)*

## 8. Data quality / ops-style questions

- Orders without delivery date.
- Products with zero stock.
- Customers without phone number.
- Orders with unusually high discount.
- Inactive suppliers.

## 9. Natural language (how users REALLY type)

- “Show me last year sales”
- “Who are my best customers?”
- “Which products are low in stock?”
- “How much tax did we collect?”
- “Give me cancelled orders”
- “Top selling electronics”

## 10. Advanced (good for demos)

- Customer lifetime value.
- Repeat customers count.
- Average delivery time.
- Revenue by country.
- Profit by supplier.

---
# Text-to-SQL System – User Stories Track & Admin Stories Track
This document defines **end-to-end stories** for both **Business Users** and **Admins**, based strictly on your existing tables, columns, and access rules.
---

## 1. Business User Stories Track

### Role Summary
- Read-only access
- Can query **safe columns only**
- Can use **2–3 table joins** (approved paths)
- No PII, no cost, no supplier data

## Story U1: Sales Overview

**Goal:** Understand overall sales performance

**User Questions:**
- What is total sales today?
- Sales this month
- Total orders this month
- Average order value

**Tables Used:**
- orders

**Output:**
- KPI cards: Total Revenue, Order Count, Avg Order Value
- Table: order_date, total_amount, order_status

## Story U2: Order Tracking

**Goal:** Track order status and flow

**User Questions:**
- How many orders are pending?
- Show delivered orders
- Cancelled orders count

**Tables Used:**
- orders

**Output:**
- KPI: Pending / Delivered / Cancelled orders
- Table: order_id, order_date, delivery_date, order_status, payment_method

## Story U3: Product Performance

**Goal:** See what products are selling well

**User Questions:**
- Top selling products
- Revenue by product
- Revenue by category

**Tables Used (Join):**
- orders → order_items → products

**Output:**
- Table: product_name, category, quantity_sold, total_revenue
- Chart: Revenue by category

## Story U4: Inventory Visibility

**Goal:** Monitor stock levels

**User Questions:**
- Low stock products
- Out of stock products
- Discontinued products

**Tables Used:**
- products

**Output:**
- Table: product_name, category, stock_quantity, is_discontinued
- Alerts for low stock

## Story U5: Customer Overview

**Goal:** Understand customer base

**User Questions:**
- How many customers do we have?
- Active customers count
- Customers by segment

**Tables Used:**
- customers

**Output:**
- KPI: Total Customers, Active Customers
- Table: customer_id, first_name, last_name, customer_segment, is_active

## Story U6: Customer Behavior

**Goal:** Analyze customer purchasing behavior

**User Questions:**
- Revenue by customer segment
- Orders by customer segment

**Tables Used (Join):**
- customers → orders → order_items

**Output:**
- Table: customer_segment, total_orders, total_revenue

## Story U7: Time-based Analysis

**Goal:** Analyze trends over time

**User Questions:**
- Sales last month
- Orders this year
- Monthly revenue trend

**Tables Used:**
- orders

**Output:**
- Table: month, total_revenue, order_count
- Line chart: monthly revenue

## Story U8: Payment Analysis

**Goal:** Understand payment preferences

**User Questions:**
- Most used payment method
- Revenue by payment method

**Tables Used:**
- orders

**Output:**
- Table: payment_method, order_count, total_revenue

# 2. Admin Stories Track

### Role Summary
- Full read access to all tables
- Can see PII, cost, supplier data
- Can run complex joins & calculations
- Can build dashboards and reports

## Story A1: Executive Business Overview

**Goal:** Monitor overall business health

**Admin Questions:**
- Total revenue by month
- Total orders and customers
- Revenue by category

**Tables Used:**
- orders, order_items, products, customers

**Output:**
- Executive KPIs
- Monthly revenue dashboard

## Story A2: Customer Analytics

**Goal:** Deep customer insights

**Admin Questions:**
- Top customers by revenue
- Customer lifetime value
- Inactive customers

**Tables Used:**
- customers, orders, order_items

**Output:**
- Customer ranking tables
- CLV metrics

## Story A3: Product Profitability

**Goal:** Understand product margins

**Admin Questions:**
- Profit per product
- Margin by category

**Tables Used:**
- products, order_items

**Output:**
- Table: product_name, revenue, cost, profit, margin

## Story A4: Inventory & Supply Chain

**Goal:** Manage inventory and suppliers

**Admin Questions:**
- Low stock vs reorder level
- Supplier lead time performance

**Tables Used:**
- products, suppliers

**Output:**
- Inventory alerts
- Supplier performance table

## Story A5: Order Operations

**Goal:** Improve fulfillment

**Admin Questions:**
- Delivery delays
- Cancellation reasons
- Return rate

**Tables Used:**
- orders, order_items

**Output:**
- Ops KPIs
- Order lifecycle dashboard

## Story A6: Financial Controls

**Goal:** Track discounts, tax, revenue leakage

**Admin Questions:**
- Total discount given
- Tax collected by month
- Net revenue

**Tables Used:**
- orders, order_items

**Output:**
- Finance summary tables

# 3. Why This Structure Works

- Clear separation of **user vs admin intent**
- Safe Text-to-SQL generation
- Easy to map stories → SQL → dashboards
- Production-ready RBAC design

## 4. Next Recommended Steps

1. Convert each story into SQL views
2. Create NL → SQL training pairs per story
3. Add role-aware prompt injection
4. Add SQL validation & guardrails

**This document can be directly used for:**
- Product design
- Model training
- Interview explanation
- Stakeholder walkthrough
---