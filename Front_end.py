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

def update_product(product_id,name,description,price,stock,window,refresh_callback=None):
    product_name=name.get()
    product_description=description.get()
    product_price=price.get()
    product_stock=stock.get()

    if not product_name or not product_description or not product_price or not product_stock:
        messagebox.showerror("Input Error","Please fill all necessary fields.")
        return

    try:
        product_data={
            "product_name": product_name,
            "product_description": product_description,
            "product_price": float(product_price),
            "product_stock": int(product_stock),
        }
        response = requests.put(f"{API_URL}/update_product/{product_id}/", json=product_data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Product updated successfully")
            window.destroy()
            if refresh_callback:
                refresh_callback()
        else:
            messagebox.showerror("Error", f"API Error: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"API Error: {e}")

def delete_product(product_id,window,refresh_callback=None):
    result=messagebox.askyesno("Confim deletion","Are you sure you want to delete this product?")
    if not result:
        return

    try:
        response = requests.delete(f"{API_URL}/delete_product/{product_id}/")
        if response.status_code == 200:
            messagebox.showinfo("Success", "Product deleted successfully")
            window.destroy()
            if refresh_callback:
                refresh_callback()
        else:
            messagebox.showerror("Error", f"API Error: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"API Error: {e}")

def find_products(search_term):
    try:
        response=requests.get(f'{API_URL}/find_products/{search_term}/')
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error", f"API Error: {response.text}")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"API Error: {e}")
        return []

def find_products_by_field(field,search_term):
    try:
        response=requests.get(f'{API_URL}/find_product_by_field/{field}/{search_term}/')
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error", f"API Error: {response.text}")
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

    def refresh_tables():
        """Refresh both tables with updated data"""
        # Clear existing data
        for tree in [available_tree, out_of_stock_tree]:
            for item in tree.get_children():
                tree.delete(item)

        # Fetch updated products
        products = fetch_products()
        if not products:
            return

        # Separate products
        available_products = [p for p in products if p.get('product_stock', 0) > 0]
        out_of_stock_products = [p for p in products if p.get('product_stock', 0) <= 0]

        # Populate tables with updated data
        for product in available_products:
            stock_value = product.get('product_stock', 0)  # FIXED: Define stock_value here
            tags = ('negative',) if stock_value < 0 else ()

            available_tree.insert("", "end", values=(
                product.get('product_id', 'N/A'),
                product.get('product_name', 'N/A'),
                product.get('product_description', 'N/A'),
                product.get('product_price', 'N/A'),
                stock_value
            ), tags=tags)

        for product in out_of_stock_products:
            stock_value = product.get('product_stock', 0)  # FIXED: Define stock_value here
            tags = ('negative',) if stock_value < 0 else ()

            out_of_stock_tree.insert("", "end", values=(
                product.get('product_id', 'N/A'),
                product.get('product_name', 'N/A'),
                product.get('product_description', 'N/A'),
                product.get('product_price', 'N/A'),
                stock_value
            ), tags=tags)

    # Add double-click bindings
    available_tree.bind("<Double-1>", lambda e: on_double_click(e, available_tree, refresh_tables))
    out_of_stock_tree.bind("<Double-1>", lambda e: on_double_click(e, out_of_stock_tree, refresh_tables))

        # Back button
    ttk.Button(window, text="Back", command=window.destroy).pack(pady=10)

def open_edit_product(product_data,refresh_callback=None):
    window = tk.Toplevel(root)
    window.title("Edit Product")
    window.geometry("400x400")

    ttk.Label(window, text="Edit Product", font=("Arial", 14, "bold")).pack(pady=10)

    ttk.Label(window, text="Product ID:").pack()
    product_id_label = ttk.Label(window, text=product_data['product_id'])
    product_id_label.pack()

    ttk.Label(window, text="Product Name:").pack()
    product_name_entry = ttk.Entry(window, width=30)
    product_name_entry.insert(0, product_data['product_name'])
    product_name_entry.pack()

    ttk.Label(window, text="Product Description:").pack()
    product_description_entry = ttk.Entry(window, width=30)
    product_description_entry.insert(0, product_data['product_description'])
    product_description_entry.pack()

    ttk.Label(window, text="Product Price:").pack()
    product_price_entry = ttk.Entry(window, width=30)
    product_price_entry.insert(0, str(product_data['product_price']))
    product_price_entry.pack()

    ttk.Label(window, text="Stock:").pack()
    product_stock_entry = ttk.Entry(window, width=30)
    product_stock_entry.insert(0, str(product_data['product_stock']))
    product_stock_entry.pack()

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Update Product",
               command=lambda: update_product(
                   product_data['product_id'],
                   product_name_entry,
                   product_description_entry,
                   product_price_entry,
                   product_stock_entry,
                   window,
                   refresh_callback
               )).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Cancel",
               command=window.destroy).pack(side="left", padx=10)

    # Delete button (separate with different color/style)
    delete_button_frame = ttk.Frame(window)
    delete_button_frame.pack(pady=10)

    # Create a style for the delete button to make it red
    style = ttk.Style()
    style.configure("Delete.TButton", foreground="red")

    ttk.Button(delete_button_frame, text="Delete Product",
               style="Delete.TButton",
               command=lambda: delete_product(
                   product_data['product_id'],
                   window,
                   refresh_callback
               )).pack()

def on_double_click(event, tree, refresh_callback=None):
    """Handle double-click on treeview item"""
    item = tree.selection()[0] if tree.selection() else None
    if item:
        values = tree.item(item, 'values')
        product_data = {
            'product_id': values[0],
            'product_name': values[1],
            'product_description': values[2],
            'product_price': float(values[3]),
            'product_stock': int(values[4])
        }
        open_edit_product(product_data, refresh_callback)

#NEED TO STUDY IT AND LEARN IT
def open_search_window():
    window = tk.Toplevel(root)
    window.title("Search Products")
    window.geometry("800x500")

    style = ttk.Style()
    style.configure("Search.TFrame", background="#f0f0f0")

    # --- Main Container Frame ---
    main_frame = ttk.Frame(window, padding="20")
    main_frame.pack(fill="both", expand=True)

    # --- Title ---
    ttk.Label(main_frame, text="Search Products",
              font=("Arial", 16, "bold")).pack(pady=(0, 20))

    # --- Search Controls Frame ---
    control_frame = ttk.LabelFrame(main_frame, text="Search Options", padding="15")
    control_frame.pack(fill="x", pady=(0, 15))

    # --- Search in All Fields (Row 1) ---
    all_search_frame = ttk.Frame(control_frame)
    all_search_frame.pack(fill="x", pady=8)

    ttk.Label(all_search_frame, text="Search All Fields:",
              font=("Arial", 10, "bold")).grid(row=0, column=0, padx=(0, 15), sticky="w")

    all_search_entry = ttk.Entry(all_search_frame, width=40, font=("Arial", 10))
    all_search_entry.grid(row=0, column=1, padx=(0, 15))

    ttk.Button(all_search_frame, text="Search All",
               command=lambda: perform_search_all(),
               width=12).grid(row=0, column=2)

    # --- Search by Specific Field (Row 2) ---
    field_search_frame = ttk.Frame(control_frame)
    field_search_frame.pack(fill="x", pady=8)

    ttk.Label(field_search_frame, text="Search by Field:",
              font=("Arial", 10, "bold")).grid(row=0, column=0, padx=(0, 15), sticky="w")

    field_combobox = ttk.Combobox(field_search_frame,
                                  values=["product_id", "product_name", "product_description", "product_price",
                                          "product_stock"],
                                  state="readonly",
                                  width=15,
                                  font=("Arial", 10))
    field_combobox.grid(row=0, column=1, padx=(0, 15))
    field_combobox.set("product_name")  # Default field

    field_search_entry = ttk.Entry(field_search_frame, width=40, font=("Arial", 10))
    field_search_entry.grid(row=0, column=2, padx=(0, 15))

    ttk.Button(field_search_frame, text="Search Field",
               command=lambda: perform_search_field(),
               width=12).grid(row=0, column=3)

    # --- Quick Action Buttons (Row 3) ---
    action_frame = ttk.Frame(control_frame)
    action_frame.pack(fill="x", pady=(10, 0))

    ttk.Button(action_frame, text="Show All Products",
               command=lambda: [all_search_entry.delete(0, tk.END),
                                field_search_entry.delete(0, tk.END),
                                load_all_products()],
               width=18).pack(side="left", padx=(0, 10))

    ttk.Button(action_frame, text="Clear All",
               command=lambda: [all_search_entry.delete(0, tk.END),
                                field_search_entry.delete(0, tk.END)],
               width=12).pack(side="left")

    # --- Results Frame ---
    results_label_frame = ttk.LabelFrame(main_frame, text="Search Results", padding="10")
    results_label_frame.pack(fill="both", expand=True)

    columns = ("ID", "Name", "Description", "Price", "Stock")
    tree = ttk.Treeview(results_label_frame, columns=columns, show="headings", height=12)

    tree.column("ID", width=60, anchor="center")
    tree.column("Name", width=150, anchor="center")
    tree.column("Description", width=200, anchor="center")
    tree.column("Price", width=100, anchor="center")
    tree.column("Stock", width=80, anchor="center")

    # Configure headings
    for col in columns:
        tree.heading(col, text=col, anchor="center")

    # Add scrollbar
    scrollbar = ttk.Scrollbar(results_label_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # Pack tree and scrollbar
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Configure tag for negative stock
    tree.tag_configure('negative', foreground='red')

    # --- Status Bar ---
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill="x", pady=(10, 0))

    status_label = ttk.Label(status_frame, text="Ready to search...",
                             font=("Arial", 9), foreground="gray")
    status_label.pack(side="left")

    # --- Helper: Populate Tree with Data ---
    def populate_tree(products, search_type=""):
        # Clear old data
        for item in tree.get_children():
            tree.delete(item)

        if not products:
            status_label.config(text="No products found for your search.")
            messagebox.showinfo("No Results", "No products found for your search.")
            return

        # Populate with products
        for product in products:
            stock_value = product.get('product_stock', 0)
            tags = ('negative',) if stock_value < 0 else ()

            tree.insert("", "end", values=(
                product.get('product_id', 'N/A'),
                product.get('product_name', 'N/A'),
                product.get('product_description', 'N/A'),
                product.get('product_price', 'N/A'),
                stock_value
            ), tags=tags)

        # Update status
        status_label.config(text=f"Found {len(products)} products" +
                                 (f" ({search_type})" if search_type else ""))

    # --- Search Functions ---
    def perform_search_all():
        search_term = all_search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Input Error", "Please enter a search term.")
            return
        status_label.config(text="Searching...")
        window.update()
        products = find_products(search_term)
        populate_tree(products, "all fields search")

    def perform_search_field():
        field = field_combobox.get()
        search_term = field_search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Input Error", "Please enter a search term for the selected field.")
            return
        status_label.config(text="Searching...")
        window.update()
        products = find_products_by_field(field, search_term)
        populate_tree(products, f"{field} search")

    def load_all_products():
        status_label.config(text="Loading all products...")
        window.update()
        products = fetch_products()
        populate_tree(products, "all products")
        status_label.config(text=f"Loaded {len(products)} products")

    # --- Double Click to Edit Product ---
    def on_tree_double_click(event):
        item = tree.selection()
        if not item:
            return
        values = tree.item(item, 'values')
        product_data = {
            'product_id': values[0],
            'product_name': values[1],
            'product_description': values[2],
            'product_price': float(values[3]),
            'product_stock': int(values[4])
        }
        open_edit_product(product_data, lambda: load_all_products())

    tree.bind("<Double-1>", on_tree_double_click)

    # --- Bind Enter key to search ---
    def on_enter_key(event, search_function):
        search_function()

    all_search_entry.bind("<Return>", lambda e: on_enter_key(e, perform_search_all))
    field_search_entry.bind("<Return>", lambda e: on_enter_key(e, perform_search_field))

    # Load all products initially
    load_all_products()

    # Set focus to first search field
    all_search_entry.focus()

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
ttk.Button(root, text="Search Products", width=25, command=open_search_window).pack(pady=5)

ttk.Button(root, text="Exit", width=25, command=root.destroy).pack(pady=20)

root.mainloop()