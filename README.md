# Ecommerce Data Lakehouse - Complete Project Documentation

## 1. PROJECT OVERVIEW

### Project Name
Ecommerce Data Lakehouse - Customer Analytics & ML Segmentation

### Project Goal
Build an enterprise-grade data lakehouse using Microsoft Fabric to:
- Ingest customer and order data from multiple sources
- Transform raw data through medallion architecture layers
- Create aggregated customer metrics for analytics
- Enable real-time Power BI dashboards
- Implement ML-based customer segmentation using K-Means clustering

### Technology Stack
- Microsoft Fabric (OneLake)
- Apache Spark (PySpark)
- Delta Lake (optimized table format)
- Semantic Model (Direct Lake connection)
- Power BI (dashboards and reports)
- Python (data transformation and ML)

---

## 2. PROJECT ARCHITECTURE

### Medallion Architecture Pattern

```
Data Flow:
Raw Data → Bronze Layer → Silver Layer → Gold Layer → Semantic Model → Power BI
(ingestion)  (storage)     (cleaning)   (aggregation)  (business layer)  (visualization)
```

### Data Sources
1. **Primary Source**: Ecommerce dataset from Kaggle (2020-2026)
   - Customers table (7,959 records)
   - Orders table (detailed transaction data)
   - Product information
   - Monthly revenue data

2. **Secondary Source**: Day 2 Synthetic Data (Incremental Load)
   - 8 new/updated customers
   - 30 new orders
   - Tests UPSERT merge logic

3. **Data Locations**:
   - Source: ADLS Gen 2 + GitHub (raw CSV files)
   - Lakehouse: OneLake (Ecommerce_Data.Lakehouse)
   - Workspace: my_workspace

---

## 3. LAYER-BY-LAYER BREAKDOWN

### LAYER 1: BRONZE (Raw Data)

**Purpose**: Store raw data as-is, no transformations

**Contents**:
```
bronze/
├── customers (Parquet format)
├── orders (Parquet format)
├── product_summary (Parquet format)
├── monthly_revenue (Parquet format)
└── siddharthpal18/Dataset/main/
    ├── customers2.csv
    └── synthetic_orders_day2.csv
```

**Record Counts**:
- customers: 7,959 records
- orders: 30,000+ records
- products: 100+ products
- Day 2 customers: 8 records
- Day 2 orders: 30 records


<img width="1521" height="482" alt="image" src="https://github.com/user-attachments/assets/ffd27185-e1a3-46a8-95fd-731a2ae0a205" />
<img width="1535" height="615" alt="image" src="https://github.com/user-attachments/assets/6e97b126-a7c7-4b9f-8baf-de4726458f01" />


---

### LAYER 2: SILVER (Cleaned Data)

**Purpose**: Clean, standardize, and prepare data

**Contents**:
```
silver/
├── customers (cleaned, all 20 columns)
├── customers2 (Day 2 synthetic, cleaned)
├── orders (cleaned, all 28 columns)
├── orders2 (Day 2 synthetic, cleaned)
├── monthly_revenue
└── Products
```

**Transformations Applied**:
1. Data type casting
2. Column selection and renaming
3. Boolean conversion (CASE WHEN for '1'/'0' → true/false)
4. Null handling
5. Data validation

**Record Counts**:
- customers: 7,959 records
- customers2: 8 records
- orders: 30,000+ records
- orders2: 30 records

<img width="1480" height="652" alt="image" src="https://github.com/user-attachments/assets/ce01b264-17a6-41b3-969c-acadc43320cd" />


---

### LAYER 3: GOLD (Analytics-Ready)

**Purpose**: Aggregate and optimize for analytics and BI

**Dimension Table: dim_customers**

Columns:
```
customer_id, age, gender, country, membership_tier,
registration_date, newsletter_subscribed, churned,
effective_date, end_date, is_current
```

Record Count: 7,964 (after Day 2 UPSERT merge)

Description:
- One row per customer
- SCD2 tracking (effective_date, end_date, is_current)
- Slow-Changing Dimensions for historical tracking
- Updated with Day 2 incremental data

**Fact Table: fact_customer_metrics**

Columns:
```
customer_id, total_orders, total_spent, avg_order_value,
last_order_date, avg_rating, return_count,
age, gender, country, membership_tier,
registration_date, newsletter_subscribed, churned,
effective_date, end_date, is_current
```

Record Count: 7,964 (after Day 2 UPSERT merge)

Description:
- Aggregated metrics per customer
- Denormalized (includes customer dimension columns)
- Order statistics (count, total, average)
- Customer satisfaction metrics (rating, returns)
- Directly optimized for Power BI

<img width="1457" height="644" alt="image" src="https://github.com/user-attachments/assets/0c0516b3-ea89-4df0-ab1e-7151389afa81" />

---

## 4. TRANSFORMATION NOTEBOOKS

### minorTransformation Notebook

**Purpose**: Clean raw data from Bronze and load to Silver

**Input**: Bronze layer (raw CSV files)
**Output**: Silver layer (cleaned parquet tables)

**Steps**:
1. Read customers.csv from bronze
2. Select 20 columns
3. Apply CASE WHEN for boolean conversions
4. Save to silver/customers
5. Read orders.csv from bronze
6. Select 28 columns
7. Apply transformations
8. Save to silver/orders
9. Repeat for Day 2 data (customers2, orders2)
10. Read additional tables (products, monthly_revenue)
11. Clean and save

**Code Highlights**:
- Uses PySpark selectExpr for column transformations
- Handles boolean conversion: CASE WHEN newsletter_subscribed = '1' THEN true
- Saves as Delta tables for optimization
- All data types properly cast (STRING → DATE, STRING → BOOLEAN, etc.)

<img width="1484" height="923" alt="image" src="https://github.com/user-attachments/assets/6f6273a3-5b0a-4440-9fbe-da98a2261c38" />
<img width="1505" height="930" alt="image" src="https://github.com/user-attachments/assets/74c2d2f9-7206-4c1d-96df-4879aad54b4e" />
<img width="1499" height="935" alt="image" src="https://github.com/user-attachments/assets/98613f0e-0d86-4452-9c07-fdc64be5aed4" />


---

### majorTransformation Notebook

**Purpose**: Aggregate Silver data and load to Gold

**Input**: Silver layer (cleaned tables)
**Output**: Gold layer (aggregated analytics tables)

**Steps**:

**Day 1 Data Creation**:
1. Read silver/customers
2. Select columns + add SCD2 columns (effective_date, end_date, is_current)
3. Save as gold.dim_customers (7,959 records)
4. Read silver/orders
5. Group by customer_id
6. Calculate metrics: count, sum, avg, max, count(returns)
7. Join with dim_customers
8. Handle NULL ratings (replace with 0)
9. Save as gold.fact_customer_metrics (7,621 records)

**Day 2 Data Merge (UPSERT)**:
10. Read silver/customers2 (Day 2)
11. Prepare with SCD2 columns
12. UPSERT merge into gold.dim_customers
    - whenMatchedUpdate: age, membership_tier, effective_date
    - whenNotMatchedInsert: all columns
13. Read silver/orders2 (Day 2)
14. Aggregate same metrics
15. Join with Day 2 customers
16. UPSERT merge into gold.fact_customer_metrics
    - whenMatchedUpdate: order metrics + customer attributes
    - whenNotMatchedInsert: all columns

**Result**: 
- dim_customers: 7,964 records (7,959 + 5 new)
- fact_customer_metrics: 7,964 records (updated + new)

<img width="1515" height="850" alt="image" src="https://github.com/user-attachments/assets/b279e390-c358-43ce-9ac6-265f15477316" />
<img width="1492" height="895" alt="image" src="https://github.com/user-attachments/assets/e3735c77-0b17-42bd-84b7-62ade5280904" />
<img width="1510" height="899" alt="image" src="https://github.com/user-attachments/assets/de309803-1115-4da3-bbbb-045bc6fcabbe" />

---

## 5. DATA PIPELINE FLOW

### Pipeline Name: Ecommerce_Pipeline

**Pipeline Stages** (Sequential):

1. **Get Metadata**
   - Type: GetMetadata activity
   - Source: ADLS ecommerce_data folder
   - Purpose: List all files to process

2. **ForEach + Copy Activities** (Parallel)
   - Copy each CSV from ADLS to bronze (parquet)
   - Copy synthetic_customers_day2.csv from GitHub to bronze
   - Copy synthetic_orders_day2.csv from GitHub to bronze
   - All 3 copy activities run in parallel
   - Status: All ✅ Succeeded

3. **minorTransformation** (Notebook)
   - Depends on: ForEach and both Copy activities
   - Cleans Bronze data
   - Outputs: Silver tables
   - Status: ✅ Succeeded

4. **majorTransformation** (Notebook)
   - Depends on: minorTransformation
   - Aggregates Silver data + UPSERT merge
   - Outputs: Gold tables + Semantic Model ready
   - Status: ✅ Succeeded

5. **ML-kmeans** (Notebook)
   - Depends on: majorTransformation
   - Reads gold tables
   - Performs K-Means clustering
   - Customer segmentation
   - Status: ✅ Succeeded

<img width="1469" height="438" alt="image" src="https://github.com/user-attachments/assets/78300f12-2541-4841-bd07-54b81856e302" />


---

## 6. SEMANTIC MODEL

### Model Name: ecommerce_model

**Purpose**: Business layer connecting Power BI to Lakehouse

**Tables Included**:
1. dim_customers (7,964 rows)
2. fact_customer_metrics (7,964 rows)

**Relationship**:
- From: fact_customer_metrics.customer_id
- To: dim_customers.customer_id
- Type: Many-to-One
- Cardinality: Many (:1)
- Direction: Single direction
- Status: ✅ Active

**Connection Type**: Direct Lake
- Live connection to gold layer tables
- Real-time data updates
- No data copying
- Optimized for analytics

<img width="1020" height="667" alt="image" src="https://github.com/user-attachments/assets/8a511651-5b98-4fd4-9a13-2e04b5ba59ab" />


---

## 7. POWER BI DASHBOARD

### Dashboard Name: Ecommerce_Dashboard

### Visuals to Create:

**PAGE 1: KPI OVERVIEW**

Visual 1: Total Customers (Card)
- Measure: COUNT(customer_id)
- Result: 7,964
- Format: Blue, large font

Visual 2: Total Revenue (Card)
- Measure: SUM(total_spent)
- Result: $XXX,XXX
- Format: Green, currency

Visual 3: Average Order Value (Card)
- Measure: AVERAGE(avg_order_value)
- Result: $XX.XX
- Format: Purple, currency

Visual 4: Average Rating (Card)
- Measure: AVERAGE(avg_rating)
- Result: 4.2
- Format: Orange, 1 decimal

Visual 5: Donut Chart - Membership Tier
- Category: membership_tier (Free, Silver, Gold, Platinum)
- Value: COUNT(customer_id)
- Shows: Distribution of customers by tier

Visual 6: Bar Chart - Top 10 Countries
- Category: country
- Value: COUNT(customer_id)
- Filter: Top 10
- Shows: Geographic distribution

**PAGE 2: SPENDING ANALYSIS**

Visual 7: Scatter Chart - Orders vs Spending
- X-axis: total_orders
- Y-axis: total_spent
- Bubble size: avg_rating
- Legend: membership_tier
- Shows: Relationship between purchase volume and spending

Visual 8: Column Chart - Avg Spending by Tier
- X-axis: membership_tier
- Y-axis: AVERAGE(total_spent)
- Shows: Which tier spends most per customer

Visual 9: Column Chart - Total Orders by Tier
- X-axis: membership_tier
- Y-axis: SUM(total_orders)
- Shows: Which tier orders most

Visual 10: Table - Top 10 Customers
- Columns: customer_id, membership_tier, total_spent, total_orders, avg_order_value
- Sort: total_spent (descending)
- Filter: Top 10 by total_spent


<img width="1143" height="663" alt="image" src="https://github.com/user-attachments/assets/3f742f24-a514-4c02-aa47-9d0c490131d0" />
<img width="1160" height="650" alt="image" src="https://github.com/user-attachments/assets/8b814502-f3b9-458e-af5a-140e314878c0" />


---

## 8. KEY TECHNICAL DECISIONS

### 1. Medallion Architecture
**Why**: Industry standard for data lakes
**Benefit**: Separation of concerns, data quality control, reusability

### 2. Delta Lake Format
**Why**: ACID transactions, schema evolution, time travel
**Benefit**: Data integrity, optimized queries, incremental processing

### 3. Direct Lake Connection
**Why**: Real-time, no data copying
**Benefit**: Performance, cost-effective, always fresh data

### 4. UPSERT Merge Logic
**Why**: Incremental load capability
**Benefit**: Handles Day 2+ data updates efficiently, preserves historical data

### 5. SCD2 Tracking
**Why**: Track customer changes over time
**Benefit**: Can analyze historical customer attributes and behavior

---

## 9. DATA QUALITY MEASURES

### Input Validation
- Schema validation at each layer
- Type checking and casting
- Null value handling
- Duplicate detection and handling

### Output Verification
- Record count tracking at each stage
- Column count verification
- Data type confirmation
- Aggregation validation

### Error Handling
- Try-catch blocks in notebooks
- Logging of transformation steps
- Failed record capture
- Alerting on pipeline failures

---

## 10. MAINTENANCE & CLEANUP

### Regular Tasks

**Daily**:
- Monitor pipeline execution
- Check for failed activities
- Verify data freshness

**Weekly**:
- Review data quality metrics
- Check storage usage
- Validate dashboard accuracy

**Monthly**:
- Archive old snapshots
- Optimize table performance
- Review security access

### Cleanup Code (Run at Notebook End)

```python
# Clear cache
spark.catalog.clearCache()

# Verify final counts
dim_count = spark.sql("SELECT COUNT(*) FROM gold.dim_customers").collect()[0][0]
fact_count = spark.sql("SELECT COUNT(*) FROM gold.fact_customer_metrics").collect()[0][0]

print(f"Final verification:")
print(f"  dim_customers: {dim_count}")
print(f"  fact_customer_metrics: {fact_count}")

# Stop Spark session
spark.stop()
print("✅ Cleanup complete")
```

---

## 11. PERFORMANCE METRICS

### Pipeline Execution
- Get Metadata: < 1 minute
- Copy Activities: 2-3 minutes (parallel)
- minorTransformation: 3-5 minutes
- majorTransformation: 4-6 minutes
- ML-kmeans: 2-3 minutes
- **Total Pipeline Time**: ~15-20 minutes

### Data Processing
- Bronze ingestion: 7,959 customers + 30,000+ orders
- Silver cleaning: ~99.5% data retention
- Gold aggregation: Customer deduplication + metrics calculation
- UPSERT merge: Handles incremental loads efficiently

### Storage Usage
- Bronze layer: ~500 MB (Parquet compressed)
- Silver layer: ~450 MB (Parquet compressed)
- Gold layer: ~100 MB (optimized Delta tables)
- **Total**: ~1 GB (highly compressed)

---

## 12. SECURITY & GOVERNANCE

### Access Control
- Workspace: my_workspace (team members only)
- Lakehouse: Role-based access
- Semantic Model: Consumer access restrictions
- Power BI: Published reports (shared workspace)

### Data Classification
- Customer PII: Personal attributes (age, location)
- Transaction Data: Order and spending information
- Aggregated Metrics: Non-sensitive summaries

### Compliance
- Data retention policy: 24 months
- Audit logging: Enabled for all changes
- Encryption: At-rest and in-transit

---

## 13. COST OPTIMIZATION

### Storage Strategy
- Delta format compression: Parquet with Snappy
- Partitioning: By country in future iterations
- Lifecycle management: Archive old snapshots after 90 days

### Compute Optimization
- Spark cluster: Autoscale 2-8 nodes
- Notebook execution: On-demand
- Query optimization: Direct Lake (no data copying)

### Cost Estimates
- Storage: ~$20/month
- Compute: ~$100/month (variable)
- Semantic Model: Included in Fabric license
- Power BI: Pro license per user

---

## 14. TROUBLESHOOTING GUIDE

### Common Issues & Solutions

**Issue 1**: UPSERT fails with schema mismatch
**Solution**: Verify .cast("date") on date columns, ensure column names match exactly

**Issue 2**: Semantic Model won't create
**Solution**: Ensure tables are in Tables/ folder (not Files/), verify table registration

**Issue 3**: Power BI shows stale data
**Solution**: Refresh semantic model manually, check Direct Lake connection

**Issue 4**: Pipeline fails at minorTransformation
**Solution**: Check ADLS connectivity, verify file formats, review error logs

**Issue 5**: K-Means clustering fails
**Solution**: Verify numeric columns, check for NULL values, reduce feature count if needed

---

## 15. NEXT STEPS & ENHANCEMENTS

### Short-term (Next Sprint)
1. Schedule daily pipeline runs (Fabric scheduler)
2. Add data quality checks (Great Expectations)
3. Create additional Power BI pages
4. Set up automated alerts

### Medium-term (Next Quarter)
1. Implement table partitioning by country
2. Add more ML models (regression, classification)
3. Create premium Power BI reports
4. Set up data governance catalog

### Long-term (Next Year)
1. Migrate to Data Warehouse for heavy analytics
2. Implement real-time streaming (Event Hubs)
3. Add predictive models (customer churn, LTV)
4. Create data marketplace

---

## 16. CONCLUSION

This Ecommerce Data Lakehouse project demonstrates a production-ready data platform using Microsoft Fabric. It successfully:

✅ Ingests data from multiple sources
✅ Transforms data through medallion architecture
✅ Creates analytics-ready aggregations
✅ Enables real-time Power BI dashboards
✅ Implements ML-based segmentation
✅ Handles incremental data loads with UPSERT
✅ Provides enterprise-grade governance

The architecture is scalable, maintainable, and ready for expansion with additional data sources, ML models, and analytics capabilities.

---

## APPENDIX: FILE LOCATIONS

**Lakehouse Path**:
```
abfss://my_workspace@onelake.dfs.fabric.microsoft.com/
Ecommerce_Data.Lakehouse/Files/
├── bronze/
├── silver/
├── gold/
└── tmp/
```

**Notebooks**:
- minorTransformation (ID: e90a4147-42b3-4fdf-bf52-bbbe19fdb25a)
- majorTransformation (ID: 3791be6d-2f4c-435c-ae43-063d931cd736)
- ML-kmeans (ID: f6d43337-0a04-40df-bbe7-4f7072d4dec6)

**Pipeline**:
- Ecommerce_Pipeline (JSON config included)

**Semantic Model**:
- ecommerce_model (Direct Lake)

**Power BI**:
- Ecommerce_Dashboard (Shared workspace)

---

**Document Version**: 1.0
**Last Updated**: May 2026
**Status**: Production Ready 
