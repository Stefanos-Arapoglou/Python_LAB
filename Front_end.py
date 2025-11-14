import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "http://127.0.0.1:8000"


#.................CLASSES AND HELPER SCRIPTS......................

#the EditableTreeview is used in the restocking tab. It allows double clicking on field to edit
class EditableTreeview(ttk.Treeview):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Double-1>", self._on_double_click)
        self._edit_box = None

    def _on_double_click(self, event):
        region = self.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.identify_row(event.y)
        column = self.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1

        # Only allow editing the Addition column
        if self["columns"][col_index].lower() != "additions":
            return

        x, y, width, height = self.bbox(row_id, column)
        value = self.item(row_id, "values")[col_index]

        self._edit_box = tk.Entry(self)
        self._edit_box.place(x=x, y=y, width=width, height=height)
        self._edit_box.insert(0, value)
        self._edit_box.focus()
        self._edit_box.bind("<Return>", lambda e: self._save_edit(row_id, col_index))
        self._edit_box.bind("<FocusOut>", lambda e: self._cancel_edit())

    def _save_edit(self, row_id, col_index):
        new_value = self._edit_box.get()
        values = list(self.item(row_id, "values"))
        values[col_index] = new_value
        self.item(row_id, values=values)
        self._edit_box.destroy()
        self._edit_box = None

    def _cancel_edit(self):
        if self._edit_box:
            self._edit_box.destroy()
            self._edit_box = None


#.................FUNCTIONS TO RUN APIS............................

def create_product(name,description,price,stock):
    product_name=name.get()
    product_description=description.get()
    product_price=price.get()
    product_stock=stock.get()

    if not product_name or not product_price or not product_stock:
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

    if not product_name or not product_price or not product_stock:
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
    result=messagebox.askyesno("Confirm deletion","Are you sure you want to delete this product?")
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

def restock_products(restocked_products, window=None, refresh_callback=None):
    for product in restocked_products:
        # Extract product data from dict
        product_id = product.get("product_id")
        product_name = product.get("product_name")
        product_description = product.get("product_description")
        product_price = product.get("product_price")
        product_stock = product.get("product_stock")

        # Validation
        if not all([product_name, product_description, product_price, product_stock]):
            messagebox.showerror("Input Error", "Please fill all necessary fields.")
            return

        try:
            product_data = {
                "product_name": product_name,
                "product_description": product_description,
                "product_price": float(product_price),
                "product_stock": int(product_stock),
            }

            response = requests.put(f"{API_URL}/update_product/{product_id}/", json=product_data)

            if response.status_code == 200:
                print(f"Product {product_name} updated successfully.")
            else:
                messagebox.showerror("Error", f"API Error ({response.status_code}): {response.text}")

        except Exception as e:
            messagebox.showerror("Error", f"API Error: {e}")

    # Optional cleanup after all updates
    messagebox.showinfo("Success", "All products updated successfully.")
    if window:
        window.destroy()
    if refresh_callback:
        refresh_callback()

def get_stats():
    try:
        response = requests.get(f"{API_URL}/get_stats/")
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

    ttk.Label(window, text="*Product Name:").pack()
    product_name_entry = ttk.Entry(window, width=30)
    product_name_entry.pack()

    ttk.Label(window, text="Product description:").pack()
    product_description_entry = ttk.Entry(window, width=30)
    product_description_entry.pack()

    ttk.Label(window, text="*Product price:").pack()
    product_price_entry = ttk.Entry(window, width=30)
    product_price_entry.pack()

    ttk.Label(window, text="*Stock:").pack()
    product_stock_entry = ttk.Entry(window, width=30)
    product_stock_entry.pack()

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    ttk.Label(
        window,
        text="Fields with * are necessary",
        font=("Arial", 10, "italic"),
        foreground="red"
    ).pack(pady=10)

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

def open_search_window():
    window = tk.Toplevel(root)
    window.title("Search Products")
    window.geometry("800x680")

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

    # Back button
    ttk.Button(action_frame, text="Back", command=window.destroy).pack(side="right")

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

def open_restock_window():
    window = tk.Toplevel(root)
    window.title("Restock Products")
    window.geometry("680x600")

    products = fetch_products()
    if not products:
        messagebox.showerror("Error", "No products found")
        return []

    main_frame = ttk.Frame(window)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    products_frame = ttk.Frame(main_frame)
    products_frame.pack()
    ttk.Label(products_frame, text="Available products", font=("Arial", 13, "bold")).pack(pady=10)

    products_tree = EditableTreeview(products_frame, columns=("ID", "Name", "Description", "Price", "Stock","Additions"),
                                     show="headings", height=20)
    products_tree.heading("ID", text="ID", anchor="center")
    products_tree.heading("Name", text="Product Name", anchor="center")
    products_tree.heading("Description", text="Description", anchor="center")
    products_tree.heading("Price", text="Price", anchor="center")
    products_tree.heading("Stock", text="Stock", anchor="center")
    products_tree.heading("Additions", text="Additions", anchor="center")
    products_tree.column("ID", width=40, anchor="center")
    products_tree.column("Name", width=140, anchor="center")
    products_tree.column("Description", width=200, anchor="center")
    products_tree.column("Price", width=100, anchor="center")
    products_tree.column("Stock", width=80, anchor="center")
    products_tree.column("Additions", width=80, anchor="center")

    products_tree_scrollbar = ttk.Scrollbar(products_frame, orient="vertical", command=products_tree.yview)
    products_tree.configure(yscrollcommand=products_tree_scrollbar.set)

    products_tree.pack(fill="both", expand=True)
    products_tree.pack(side="right", fill="y")

    # Define tag for negative stock (red color)
    products_tree.tag_configure('negative', foreground='red')

    for product in products:
        stock_value = product.get('product_stock', 0)  # FIXED: Define stock_value here
        tags = ('negative',) if stock_value < 0 else ()

        products_tree.insert("", "end", values=(
            product.get('product_id', 'N/A'),
            product.get('product_name', 'N/A'),
            product.get('product_description', 'N/A'),
            product.get('product_price', 'N/A'),
            stock_value,
            0
        ), tags=tags)

    def on_restock():
        updated_products = []
        for item_id in products_tree.get_children():
            values = products_tree.item(item_id, "values")
            stock = int(values[4])
            additions = int(values[5])

            new_stock = stock + additions
            updated_products.append({
                "product_id": values[0],
                "product_name": values[1],
                "product_description": values[2],
                "product_price": values[3],
                "product_stock": new_stock,
            })
        restock_products(updated_products, window)

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    # FIX: Use lambda to prevent immediate execution
    ttk.Button(button_frame, text="Restock Products",
               command=lambda: [on_restock(),window.destroy()]).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Back",
               command=window.destroy).pack(side="left", padx=10)

def open_stats_window():
    window = tk.Toplevel(root)
    window.title("Statistics Overview")
    window.geometry("400x500")
    window.resizable(False, False)

    ttk.Label(window, text="📊 Product Statistics", font=("Arial", 16, "bold")).pack(pady=15)

    stats = get_stats()
    if not stats:
        ttk.Label(window, text="No statistics available", font=("Arial", 12)).pack(pady=20)
        return

    # Fetch all products to resolve product_id → product_name
    products = fetch_products()
    product_map = {str(p["product_id"]): p for p in products}

    # Build readable labels
    stat_labels = {
        "product_count": "Total Products",
        "average_price": "Average Price",
        "average_stock": "Average Stock",
        "highest_price_id": "Product with Highest Price",
        "highest_price": "Highest Price",
        "highest_stock_id": "Product with Highest Stock",
        "highest_stock": "Highest Stock",
        "value_sum": "Total Inventory Value",
        "available_products": "Available Products",
        "out_of_stock_products": "Out of Stock Products",
    }

    # Frame for all stat rows
    stats_frame = ttk.Frame(window)
    stats_frame.pack(padx=20, pady=10, fill="x")

    product_links = {}  # Keep references for clickable product labels

    for i, (key, label_text) in enumerate(stat_labels.items()):
        ttk.Label(stats_frame, text=label_text + ":", font=("Arial", 11, "bold")).grid(row=i, column=0, sticky="w", pady=5)

        value = stats.get(key, "N/A")

        # Handle product ID fields
        if key in ("highest_price_id", "highest_stock_id"):
            product = product_map.get(str(value))
            if product:
                product_name = product["product_name"]
                label = tk.Label(stats_frame, text=f"{product_name} (ID: {value})",
                                 font=("Arial", 11), foreground="blue", cursor="hand2")
                label.grid(row=i, column=1, sticky="w", pady=5)
                # Store and bind double-click
                product_links[label] = product
                label.bind("<Double-1>", lambda e, p=product: open_edit_product(p))
            else:
                ttk.Label(stats_frame, text=f"Unknown (ID: {value})", font=("Arial", 11)).grid(row=i, column=1, sticky="w", pady=5)

        else:
            # Format numeric values nicely
            if isinstance(value, (int, float)):
                # Round all numeric values
                value = round(float(value), 2)
                if key in ("product_count","average_stock","highest_stock","available_products","out_of_stock_products"):
                    value = round(int(value), 2)

                # Add euro sign to price-related stats
                if key in ("average_price", "highest_price", "value_sum"):
                    display_value = f"{value:.2f} €"
                else:
                    display_value = str(value)
            else:
                display_value = str(value)

            ttk.Label(stats_frame, text=display_value, font=("Arial", 11)).grid(row=i, column=1, sticky="w", pady=5)

    ttk.Button(window, text="Close", command=window.destroy).pack(pady=20)



#...........MAIN MENU........................

root = tk.Tk()
root.geometry("400x480")
root.title("CRUD STORAGE APP")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("winnative")
style.configure("TButton", font=("Arial", 12), padding=6)

ttk.Label(root, text="Storage CRUD App", font=("Arial", 18, "bold")).pack(pady=20)
ttk.Button(root, text="Create Product", width=25, command=open_create_product).pack(pady=5)
ttk.Button(root, text="View Products", width=25, command=open_view_products).pack(pady=5)
ttk.Button(root, text="Search Products", width=25, command=open_search_window).pack(pady=5)
ttk.Button(root, text="Restock Products", width=25, command=open_restock_window).pack(pady=5)
ttk.Button(root, text="View Statistics", width=25, command=open_stats_window).pack(pady=5)

ttk.Button(root, text="Exit", width=25, command=root.destroy).pack(pady=50)

root.mainloop()