import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "http://127.0.0.1:8000"


#.................FUNCTIONS TO RUN APIS............................

def create_product(name,description,price,stock):
    product_name=name.get()
    product_description=description.get()
    product_price=price.get()
    product_stock=stock.get()

    if not product_name or not product_description or not product_price or not product_stock:
        messagebox.showwarning("Input Error", "Please fill all necessary fields.")
        return

    try:
        product={
            "product_name": product_name,
            "product_description": product_description,
            "product_price": product_price,
            "product_stock": product_stock,
        }

        response = requests.post(f"{API_URL}/create_product/", json=product)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Product created successfully")
        else:
            messagebox.showerror("Error", f"API Error: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"API Error: {e}")

def fetch_products():
    try:
        response = requests.get(f"{API_URL}/get_products/")
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error", f"Failed to fetch products: {response.text}")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"API Error: {e}")
        return []




#............... FRONT END VISUALIZATION........................

def open_create_product():
    window = tk.Toplevel(root)
    ttk.Label(window, text="Create a new product", font=("Arial", 14, "bold")).pack(pady=10)

    ttk.Label(window, text="Product Name:").pack()
    product_name_entry = ttk.Entry(window, width=30)
    product_name_entry.pack()

    ttk.Label(window, text="Product description:").pack()
    product_description_entry = ttk.Entry(window, width=30)
    product_description_entry.pack()

    ttk.Label(window, text="Product price:").pack()
    product_price_entry = ttk.Entry(window, width=30)
    product_price_entry.pack()

    ttk.Label(window, text="Stock:").pack()
    product_stock_entry = ttk.Entry(window, width=30)
    product_stock_entry.pack()

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    # FIX: Use lambda to prevent immediate execution
    ttk.Button(button_frame, text="Create Product",
               command=lambda: [create_product(product_name_entry, product_description_entry,
                                           product_price_entry, product_stock_entry),window.destroy()]).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Back",
               command=window.destroy).pack(side="left", padx=10)


def open_view_products():
    window = tk.Toplevel(root)
    window.title("View Products")
    window.geometry("1200x600")

    #First we get our data from database
    products = fetch_products()
    if not products:
        messagebox.showerror("Error","No products found")
        return []

    products_in_stock = [p for p in products if p.get('product_stock', 0)>0]
    products_out_of_stock = [p for p in products if p.get('product_stock',0)<=0]

    #We create the parent frame for both tables
    main_frame = ttk.Frame(window)
    main_frame.pack(fill="both",expand=True,padx=10,pady=10)
    # ttk.Label(main_frame, text="Storage Products Catalog", font=("Arial", 14, "bold")).grid(row=0,column=0,sticky="w",pady=(0,10))
    #All these are for the available table visualization

    available_frame=ttk.Frame(main_frame)
    available_frame.grid(row=1,column=0,sticky="nsew", padx=(0,10))
    ttk.Label(available_frame,text="Available Products",font=("Arial",13,"bold")).pack(pady=10)


    available_tree = ttk.Treeview(available_frame, columns=("ID","Name","Description","Price","Stock"),show="headings", height=10)
    available_tree.heading("ID", text="ID", anchor="center")
    available_tree.heading("Name", text="Product Name", anchor="center")
    available_tree.heading("Description", text="Description", anchor="center")
    available_tree.heading("Price", text="Price", anchor="center")
    available_tree.heading("Stock", text="Stock", anchor="center")
    available_tree.column("ID", width=40, anchor="center")
    available_tree.column("Name", width=140, anchor="center")
    available_tree.column("Description", width=200, anchor="center")
    available_tree.column("Price", width=100, anchor="center")
    available_tree.column("Stock", width=80, anchor="center")

    available_scrollbar=ttk.Scrollbar(available_frame,orient="vertical",command=available_tree.yview)
    available_tree.configure(yscrollcommand=available_scrollbar.set)

    available_tree.pack(side="left", fill="both",expand=True)
    available_scrollbar.pack(side="right", fill="y")

    #All these are for the out of stock table visualization
    out_of_stock_frame=ttk.Frame(main_frame)
    out_of_stock_frame.grid(row=1,column=1,sticky="nsew")
    ttk.Label(out_of_stock_frame,text="Out of Stock Products",font=("Arial",13,"bold")).pack(pady=10)

    out_of_stock_tree=ttk.Treeview(out_of_stock_frame, columns=("ID", "Name", "Description", "Price", "Stock"), show="headings", height=10)

    out_of_stock_tree.heading("ID", text="ID", anchor="center")
    out_of_stock_tree.heading("Name", text="Product Name", anchor="center")
    out_of_stock_tree.heading("Description", text="Description", anchor="center")
    out_of_stock_tree.heading("Price", text="Price", anchor="center")
    out_of_stock_tree.heading("Stock", text="Stock", anchor="center")
    out_of_stock_tree.column("ID", width=40, anchor="center")
    out_of_stock_tree.column("Name", width=140, anchor="center")
    out_of_stock_tree.column("Description", width=200, anchor="center")
    out_of_stock_tree.column("Price", width=100, anchor="center")
    out_of_stock_tree.column("Stock", width=80, anchor="center")

    out_of_stock_scrollbar = ttk.Scrollbar(out_of_stock_frame, orient="vertical", command=out_of_stock_tree.yview)
    out_of_stock_tree.configure(yscrollcommand=out_of_stock_scrollbar.set)

    out_of_stock_tree.pack(side="left", fill="both", expand=True)
    out_of_stock_scrollbar.pack(side="right", fill="y")

    #These are configuration of the main_frame to be more reactive
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(1, weight=1)

    # Define tag for negative stock (red color)
    out_of_stock_tree.tag_configure('negative', foreground='red')

    #And now we populate our trees
    for product in products_in_stock:
        available_tree.insert("","end",values=(
            product.get('product_id', 'N/A'),
            product.get('product_name', 'N/A'),
            product.get('product_description', 'N/A'),
            product.get('product_price', 'N/A'),
            product.get('product_stock', 'N/A')
        ))

    for product in products_out_of_stock:
        stock_value = product.get('product_stock', 0)
        tags = ('negative',) if stock_value < 0 else ()
        out_of_stock_tree.insert("","end",values=(
            product.get('product_id', 'N/A'),
            product.get('product_name', 'N/A'),
            product.get('product_description', 'N/A'),
            product.get('product_price', 'N/A'),
            product.get('product_stock', 'N/A')
        ),tags=tags)

        # Back button
    ttk.Button(window, text="Back", command=window.destroy).pack(pady=10)


#...........MAIN MENU........................

root = tk.Tk()
root.geometry("400x400")
root.title("CRUDE STORAGE APP")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("winnative")
style.configure("TButton", font=("Arial", 12), padding=6)

ttk.Label(root, text="Storage CRUDE App", font=("Arial", 18, "bold")).pack(pady=20)
ttk.Button(root, text="Create Product", width=25, command=open_create_product).pack(pady=5)
ttk.Button(root, text="View Products", width=25, command=open_view_products).pack(pady=5)

ttk.Button(root, text="Exit", width=25, command=root.destroy).pack(pady=20)

root.mainloop()