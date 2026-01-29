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

---

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

---

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

---

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

---

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

--- End of final code. Happy querying! 🎉

| Table       | Ideal Record Count      | Why this works                              |
| ----------- | ----------------------- | ------------------------------------------- |
| customers   | **5,000 – 20,000**      | Enough diversity for segments, geo, cohorts |
| suppliers   | **50 – 300**            | Realistic retail supplier spread            |
| products    | **1,000 – 5,000**       | Rich category & pricing analytics           |
| orders      | **50,000 – 300,000**    | Time-series + behavioral depth              |
| order_items | **150,000 – 1,000,000** | Where analytics actually live               |

---

# Recommended “Perfect Demo Dataset”
customers     → 10,000
suppliers     → 100
products      → 2,500
orders        → 120,000
order_items   → 450,000


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

---

## 2. Order-related questions

- How many orders are Delivered?
- Show all Cancelled orders.
- Total sales amount by month.
- Orders placed in 2023.
- Average order value.
- Orders with Returned status.
- Which payment method is used most?
- Orders with shipping cost more than 15.

---

## 3. Order item (line-level) questions

- Total quantity sold per product.
- Total revenue by product.
- Which items are Cancelled?
- Average discount percent per product.
- Order items with Pending status.
- Total tax collected per order.
- Top 5 products by line total.

---

## 4. Product-related questions

- List all Electronics products.
- Products that are discontinued.
- Products with stock below reorder level.
- Total products by category.
- Average price by category.
- Top 3 most expensive products.
- Products created in 2024.

---

## 5. Supplier-related questions

- List all active suppliers.
- Suppliers from United Kingdom.
- Average lead time by supplier.
- Suppliers with Net 60 payment terms.
- How many products per supplier?
- Recently registered suppliers.

---

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

---

## 7. Business / analytics questions

- Monthly revenue trend.
- Best-selling product category.
- Top 5 customers by revenue.
- Total discount given this year.
- Total tax collected.
- Which products generate highest profit?  
  *(price – cost)*

---

## 8. Data quality / ops-style questions

- Orders without delivery date.
- Products with zero stock.
- Customers without phone number.
- Orders with unusually high discount.
- Inactive suppliers.

---

## 9. Natural language (how users REALLY type)

- “Show me last year sales”
- “Who are my best customers?”
- “Which products are low in stock?”
- “How much tax did we collect?”
- “Give me cancelled orders”
- “Top selling electronics”

---

## 10. Advanced (good for demos)

- Customer lifetime value.
- Repeat customers count.
- Average delivery time.
- Revenue by country.
- Profit by supplier.
