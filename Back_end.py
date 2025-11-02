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
    conn=None
    try:
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            host=DB_HOST
        )
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
    except psycopg2.Error as e:
        print("Database error:",e)
    finally:
        if conn:
            conn.close()

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


# def update_product_in_db(product: Product):
#     conn = None
#     try:
#         conn = psycopg2.connect(
#             database=DB_NAME,
#             user=DB_USER,
#             password=DB_PASSWORD,
#             port=DB_PORT,
#             host=DB_HOST
#         )
#         cursor = conn.cursor()
#         cursor.execute("""


#............APIS........................
@app.post("/create_product/")
def create_product(product: Product):
    insert_product_to_db(product)
    return {"message": "Product created successfully"}

@app.get("/get_products/")
def get_all_products():
    products = fetch_products_from_db()
    return products


