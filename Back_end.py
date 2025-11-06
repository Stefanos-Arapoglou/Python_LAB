from fastapi import FastAPI
import psycopg2
from pydantic import BaseModel

# FastAPI app
app = FastAPI()

# Database connection info
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "12345"
DB_HOST = "localhost"
DB_PORT = "5442"


#........CLASSES (BaseModels)............

class Product(BaseModel):
    product_name: str
    product_description: str
    product_price: float
    product_stock: int



#.......FUNCTIONS TO HANDLE DATABASE...............

def get_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT):
    try:
        conn=psycopg2.connect(
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting: ",e)
        return None

def insert_product_to_db(product: Product):
    conn=get_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id SERIAL PRIMARY KEY,
        product_name VARCHAR(100),
        product_description VARCHAR(500),
        product_price DOUBLE PRECISION,
        product_stock INT
    );
    """)

    cursor.execute("""
    INSERT INTO products (product_name, product_description, product_price, product_stock)
    VALUES (%s, %s, %s, %s);
    """, (product.product_name, product.product_description, product.product_price, product.product_stock))
    conn.commit()
    cursor.close()

def fetch_products_from_db():
    conn = get_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT product_id, product_name, product_description, product_price, product_stock FROM products;""")
    rows = cursor.fetchall()
    cursor.close()
    return [
        {
            "product_id": r[0],
            "product_name": r[1],
            "product_description": r[2],
            "product_price": r[3],
            "product_stock": r[4]
        }
        for r in rows
    ]

def update_product_in_db(product_id,product: Product):
    conn = get_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE products
                   SET product_name        = %s,
                       product_description = %s,
                       product_price       = %s,
                       product_stock       = %s
                   WHERE product_id = %s;
                   """,
                   (product.product_name, product.product_description, product.product_price, product.product_stock,
                    product_id))
    conn.commit()
    cursor.close()

def delete_product_in_db(productd_id):
    conn = get_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    conn.cursor().execute("""
            DELETE FROM products where product_id=%s
    """, (productd_id))
    conn.commit()
    conn.close()

def search_all_fields(search_term):
    conn = get_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    cursor = conn.cursor()
    search_pattern = f'%{search_term}%'
    cursor.execute("""
        SELECT * FROM products WHERE
            product_id::TEXT ILIKE %s OR
            product_name ILIKE %s OR
            product_description ILIKE %s OR
            product_price::TEXT ILIKE %s OR
            product_stock::TEXT ILIKE %s;
    """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "product_id": r[0],
            "product_name": r[1],
            "product_description": r[2],
            "product_price": r[3],
            "product_stock": r[4]
        }
        for r in rows
    ]

def search_product_by_field(search_field, search_term):
    conn = get_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    cursor = conn.cursor()

    # Validate the search_field to prevent SQL injection
    valid_fields = ['product_id', 'product_name', 'product_description', 'product_price', 'product_stock']
    if search_field not in valid_fields:
        raise ValueError(f"Invalid search field: {search_field}")

    # Use string formatting for the column name, parameter for the value
    query = f"""
        SELECT * FROM products WHERE {search_field}::TEXT ILIKE %s;
    """
    search_term_pattern = f'%{search_term}%'

    cursor.execute(query, (search_term_pattern,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "product_id": r[0],
            "product_name": r[1],
            "product_description": r[2],
            "product_price": r[3],
            "product_stock": r[4]
        }
        for r in rows
    ]

def stats_calculation_in_db():
    conn = get_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_id, product_name, product_description, product_price, product_stock FROM products;""")
    rows = cursor.fetchall()
    cursor.close()

    #... variables that we will need for our stats:....
    product_count=0
    price_sum=0
    stock_sum=0
    value_sum=0
    current_highest_price=0
    highest_price_id=""
    current_highest_stock=0
    highest_stock_id=""
    available_products=0
    out_of_stock_products=0

    #.... getting info from our database...
    for row in rows:
        product_id = row[0]
        product_name = row[1]
        product_description = row[2]
        product_price = row[3]
        product_stock = row[4]
        product_count=product_count+1
        price_sum+=float(product_price)
        stock_sum+=float(product_stock)
        value_sum+=float(product_price*product_stock)
        if product_price>current_highest_price:
            current_highest_price=product_price
            highest_price_id=product_id
        if product_stock>current_highest_stock:
            current_highest_stock=product_stock
            highest_stock_id=product_id
        if product_stock>0:
            available_products=available_products+1
        else:
            out_of_stock_products=out_of_stock_products+1


    #... Calculating stats....
    average_price=price_sum/product_count
    average_stock=stock_sum/product_count
    stats={
        "product_count": product_count,
        "average_price": average_price,
        "average_stock": average_stock,
        "highest_price_id": highest_price_id,
        "highest_price": current_highest_price,
        "highest_stock_id": highest_stock_id,
        "highest_stock": current_highest_stock,
        "value_sum": value_sum,
        "available_products": available_products,
        "out_of_stock_products": out_of_stock_products
    }
    return stats


#............APIS........................
@app.post("/create_product/")
def create_product(product: Product):
    insert_product_to_db(product)
    return {"message": "Product created successfully"}

@app.get("/get_products/")
def get_all_products():
    products = fetch_products_from_db()
    return products

@app.put("/update_product/{product_id}")
def update_product(product_id,product: Product):
    update_product_in_db(product_id,product)
    return {"message": "Product updated successfully"}

@app.delete("/delete_product/{product_id}")
def delete_product(product_id):
    delete_product_in_db(product_id)
    return {"message":"Product deleted successfully"}

@app.get("/find_products/{search_term}")
def search_products(search_term: str):
    products = search_all_fields(search_term)
    return products

@app.get("/find_product_by_field/{search_field}/{search_term}")
def serach_products_by_field(search_field,search_term):
    products = search_product_by_field(search_field,search_term)
    return products

@app.get("/get_stats/")
def get_stats():
    stats = stats_calculation_in_db()
    return stats