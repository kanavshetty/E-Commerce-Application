import tkinter as tk
from tkinter import messagebox, simpledialog
import requests

BASE_URL = "http://localhost:5000/api"  # Change if different


class App:
    """Tk‑based desktop frontend for the CS4092 Online Shopping application.

    >>> Key Additions (v2)
    ├─ Product Search & Filtering
    ├─ Complete Shopping‑Cart management (edit / remove)
    ├─ Checkout + Order history
    ├─ Address & Credit‑Card CRUD for customers
    ├─ Product CRUD & Warehouse stock management for staff
    └─ Modular Frame system for easier navigation / extensibility
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("E‑Commerce App")
        self.customer_id: int | None = None
        self.is_staff: bool = False

        # === shared state ===
        self.frames: dict[str, tk.Frame] = {}
        self.current_frame: str | None = None

        # --- Build frames ---
        self.build_main_menu()
        self.build_customer_menu()
        self.build_staff_menu()
        self.build_products_view()
        self.build_cart_view()
        self.build_address_manager()
        self.build_card_manager()
        self.build_orders_view()

        # start
        self.show_frame("main")

    # ------------------------------------------------------------------
    #  Frame helpers
    # ------------------------------------------------------------------
    def show_frame(self, key: str):
        if self.current_frame:
            self.frames[self.current_frame].pack_forget()
        self.frames[key].pack(fill="both", expand=True)
        self.current_frame = key

    def reset_frame(self, key: str):
        frame = self.frames[key]
        for w in frame.winfo_children():
            w.destroy()

    # ------------------------------------------------------------------
    #  Main menu
    # ------------------------------------------------------------------
    def build_main_menu(self):
        f = tk.Frame(self.root)
        self.frames["main"] = f
        tk.Label(f, text="Welcome to the Store", font=("Arial", 16)).pack(pady=10)
        tk.Button(f, text="Login", width=30, command=self.login).pack(pady=5)
        tk.Button(f, text="Register", width=30, command=self.register).pack(pady=5)
        tk.Button(f, text="Browse Products", width=30, command=self.view_products).pack(pady=5)

    # ------------------------------------------------------------------
    #  Customer menu
    # ------------------------------------------------------------------
    def build_customer_menu(self):
        f = tk.Frame(self.root)
        self.frames["customer"] = f
        self.customer_label = tk.Label(f, font=("Arial", 12))
        self.customer_label.pack(pady=10)
        tk.Button(f, text="Browse / Search Products", width=30, command=self.view_products).pack(pady=2)
        tk.Button(f, text="Shopping Cart", width=30, command=self.view_cart).pack(pady=2)
        tk.Button(f, text="Manage Addresses", width=30, command=self.manage_addresses).pack(pady=2)
        tk.Button(f, text="Manage Credit Cards", width=30, command=self.manage_cards).pack(pady=2)
        tk.Button(f, text="View Orders", width=30, command=self.view_orders).pack(pady=2)
        tk.Button(f, text="Logout", width=30, command=self.logout).pack(pady=10)

    # ------------------------------------------------------------------
    #  Staff menu
    # ------------------------------------------------------------------
    def build_staff_menu(self):
        f = tk.Frame(self.root)
        self.frames["staff"] = f
        self.staff_label = tk.Label(f, font=("Arial", 12))
        self.staff_label.pack(pady=10)
        tk.Button(f, text="View Products", width=30, command=self.view_products).pack(pady=2)
        tk.Button(f, text="Add Product", width=30, command=self.add_product).pack(pady=2)
        tk.Button(f, text="Modify Product", width=30, command=self.modify_product).pack(pady=2)
        tk.Button(f, text="Delete Product", width=30, command=self.delete_product).pack(pady=2)
        tk.Button(f, text="Update Price", width=30, command=self.update_price).pack(pady=2)
        tk.Button(f, text="Add Stock to Warehouse", width=30, command=self.add_stock).pack(pady=2)
        tk.Button(f, text="Logout", width=30, command=self.logout).pack(pady=10)

    # ------------------------------------------------------------------
    #  Products view (search + list)
    # ------------------------------------------------------------------
    def build_products_view(self):
        f = tk.Frame(self.root)
        self.frames["products"] = f

        header = tk.Frame(f)
        header.pack(fill="x", pady=5)
        tk.Button(header, text="← Back", command=lambda: self.show_frame("staff" if self.is_staff else ("customer" if self.customer_id else "main"))).pack(side="left", padx=5)
        tk.Label(header, text="Products", font=("Arial", 14)).pack(side="left")

        search_bar = tk.Frame(f)
        search_bar.pack(fill="x", pady=5)
        self.search_entry = tk.Entry(search_bar)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(search_bar, text="Search", command=self.search_products).pack(side="left", padx=5)

        self.products_list = tk.Frame(f)
        self.products_list.pack(fill="both", expand=True)

    def populate_products(self, products: list[dict]):
        self.reset_frame("products")  # clear & rebuild
        self.build_products_view()  # header & search again

        for prod in products:
            row = tk.Frame(self.products_list)
            row.pack(fill="x", padx=10, pady=2)
            info = f"{prod['name']} — ${float(prod['price']):.2f}" if prod.get("price") else f"{prod['name']} — Price N/A"
            tk.Label(row, text=info, anchor="w").pack(side="left", fill="x", expand=True)
            tk.Button(row, text="Add to Cart", command=lambda p=prod["product_id"]: self.add_to_cart(p)).pack(side="right")

    # ------------------------------------------------------------------
    #  Cart view
    # ------------------------------------------------------------------
    def build_cart_view(self):
        f = tk.Frame(self.root)
        self.frames["cart"] = f

        header = tk.Frame(f)
        header.pack(fill="x", pady=5)
        tk.Button(header, text="← Back", command=lambda: self.show_frame("customer")).pack(side="left", padx=5)
        tk.Label(header, text="Shopping Cart", font=("Arial", 14)).pack(side="left")

        self.cart_items_list = tk.Frame(f)
        self.cart_items_list.pack(fill="both", expand=True)

        self.cart_total_var = tk.StringVar(value="Total: $0.00")
        tk.Label(f, textvariable=self.cart_total_var, font=("Arial", 12)).pack(pady=5)
        tk.Button(f, text="Checkout", width=25, command=self.checkout).pack(pady=5)

    def populate_cart(self, items: list[dict]):
        for w in self.cart_items_list.winfo_children():
            w.destroy()

        total = 0.0
        for item in items:
            row = tk.Frame(self.cart_items_list)
            row.pack(fill="x", padx=10, pady=2)
            subtotal = float(item["price"]) * item["quantity"]
            total += subtotal
            info = f"{item['product_name']} x{item['quantity']} — ${subtotal:.2f}"
            tk.Label(row, text=info, anchor="w").pack(side="left", fill="x", expand=True)
            tk.Button(row, text="Edit", command=lambda i=item: self.edit_cart_item(i)).pack(side="right", padx=2)
            tk.Button(row, text="Remove", command=lambda i=item: self.remove_cart_item(i["product_id"])).pack(side="right", padx=2)

        self.cart_total_var.set(f"Total: ${total:.2f}")

    # ------------------------------------------------------------------
    #  Address manager
    # ------------------------------------------------------------------
    def build_address_manager(self):
        f = tk.Frame(self.root)
        self.frames["addresses"] = f

        header = tk.Frame(f)
        header.pack(fill="x", pady=5)
        tk.Button(header, text="← Back", command=lambda: self.show_frame("customer")).pack(side="left", padx=5)
        tk.Label(header, text="My Addresses", font=("Arial", 14)).pack(side="left")

        self.addr_list = tk.Frame(f)
        self.addr_list.pack(fill="both", expand=True)

        tk.Button(f, text="Add Address", width=25, command=self.add_address).pack(pady=5)

    def populate_addresses(self, addresses: list[dict]):
        self.reset_frame("addresses")
        self.build_address_manager()

        for addr in addresses:
            row = tk.Frame(self.addr_list)
            row.pack(fill="x", padx=10, pady=2)
            info = f"#{addr['address_id']} — {addr['street']}, {addr['city']}, {addr['state']} {addr.get('zip','')}"
            tk.Label(row, text=info, anchor="w").pack(side="left", fill="x", expand=True)
            tk.Button(row, text="Edit", command=lambda a=addr: self.edit_address(a)).pack(side="right", padx=2)
            tk.Button(row, text="Delete", command=lambda aid=addr['address_id']: self.delete_address(aid)).pack(side="right", padx=2)

    # ------------------------------------------------------------------
    #  Credit‑card manager
    # ------------------------------------------------------------------
    def build_card_manager(self):
        f = tk.Frame(self.root)
        self.frames["cards"] = f

        header = tk.Frame(f)
        header.pack(fill="x", pady=5)
        tk.Button(header, text="← Back", command=lambda: self.show_frame("customer")).pack(side="left", padx=5)
        tk.Label(header, text="My Credit Cards", font=("Arial", 14)).pack(side="left")

        self.card_list = tk.Frame(f)
        self.card_list.pack(fill="both", expand=True)
        tk.Button(f, text="Add Card", width=25, command=self.add_card).pack(pady=5)

    def populate_cards(self, cards: list[dict]):
        self.reset_frame("cards")
        self.build_card_manager()

        for card in cards:
            row = tk.Frame(self.card_list)
            row.pack(fill="x", padx=10, pady=2)
            info = f"#{card['card_id']} — **** **** **** {card['last4']} (exp {card['expiry']})"
            tk.Label(row, text=info, anchor="w").pack(side="left", fill="x", expand=True)
            tk.Button(row, text="Edit", command=lambda c=card: self.edit_card(c)).pack(side="right", padx=2)
            tk.Button(row, text="Delete", command=lambda cid=card['card_id']: self.delete_card(cid)).pack(side="right", padx=2)

    # ------------------------------------------------------------------
    #  Orders view
    # ------------------------------------------------------------------
    def build_orders_view(self):
        f = tk.Frame(self.root)
        self.frames["orders"] = f

        header = tk.Frame(f)
        header.pack(fill="x", pady=5)
        tk.Button(header, text="← Back", command=lambda: self.show_frame("customer")).pack(side="left", padx=5)
        tk.Label(header, text="My Orders", font=("Arial", 14)).pack(side="left")

        self.order_list = tk.Frame(f)
        self.order_list.pack(fill="both", expand=True)

    def populate_orders(self, orders: list[dict]):
        self.reset_frame("orders")
        self.build_orders_view()

        for order in orders:
            row = tk.Frame(self.order_list)
            row.pack(fill="x", padx=10, pady=2)
            info = (
                f"Order #{order['order_id']} — {order['status'].capitalize()} — "
                f"Placed {order['order_date']} — Total ${order['total']:.2f}"
            )
            tk.Label(row, text=info, anchor="w").pack(side="left", fill="x", expand=True)

    # ================================================================
    #  AUTHENTICATION
    # ================================================================
    def login(self):
        email = simpledialog.askstring("Login", "Email:")
        password = simpledialog.askstring("Login", "Password:", show="*")
        if not (email and password):
            return
        try:
            res = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
        except requests.exceptions.RequestException as e:
            return messagebox.showerror("Network Error", str(e))
        if not res.ok:
            return messagebox.showerror("Login Failed", res.json().get("message", "Unknown error"))

        data = res.json()
        self.customer_id = data["customer_id"]
        staff_val = data.get("is_staff", False)
        self.is_staff = str(staff_val).lower() in {"true", "1", "yes", "y"}
        messagebox.showinfo("Success", "Login successful")
        if self.is_staff:
            self.staff_label.config(text=f"Staff ID: {self.customer_id}")
            self.show_frame("staff")
        else:
            self.customer_label.config(text=f"Customer ID: {self.customer_id}")
            self.show_frame("customer")

    def register(self):
        name = simpledialog.askstring("Register", "Name:")
        email = simpledialog.askstring("Register", "Email:")
        password = simpledialog.askstring("Register", "Password:", show="*")
        balance = simpledialog.askfloat("Register", "Initial Balance:") or 0.0
        is_staff_input = simpledialog.askstring("Register", "Is Staff? (yes/no):") or "no"
        is_staff = is_staff_input.strip().lower() in {"yes", "y", "true", "1"}
        if not (name and email and password):
            return
        res = requests.post(
            f"{BASE_URL}/register-customer",
            json={
                "name": name,
                "email": email,
                "password": password,
                "balance": balance,
                "is_staff": is_staff,
            },
        )
        if res.ok:
            messagebox.showinfo("Success", "Registration successful")
        else:
            messagebox.showerror("Error", res.json().get("message", "Unknown error"))

    # ================================================================
    #  PRODUCT BROWSING
    # ================================================================
    def view_products(self):
        # default list or search result is handled separately
        try:
            res = requests.get(f"{BASE_URL}/view-products")
            if not res.ok:
                raise ValueError(res.json().get("message", "Failed to load products"))
            self.populate_products(res.json().get("products", []))
            self.show_frame("products")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_products(self):
        query = self.search_entry.get().strip()
        if not query:
            return self.view_products()
        try:
            res = requests.get(f"{BASE_URL}/search-products", params={"keyword": query})
            if not res.ok:
                raise ValueError(res.json().get("message", "Search failed"))
            self.populate_products(res.json().get("products", []))
            self.show_frame("products")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================================================================
    #  SHOPPING CART
    # ================================================================
    def add_to_cart(self, product_id: int):
        if not self.customer_id:
            return messagebox.showwarning("Login Required", "Please log in first.")
        quantity = simpledialog.askinteger("Add to Cart", "Quantity:", minvalue=1, initialvalue=1)
        if not quantity:
            return
        try:
            res = requests.post(
                f"{BASE_URL}/add-to-cart",
                json={"customer_id": self.customer_id, "product_id": product_id, "quantity": quantity},
            )
            if res.ok:
                messagebox.showinfo("Success", "Item added to cart")
            else:
                raise ValueError(res.json().get("message", "Add failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_cart(self):
        try:
            res = requests.get(f"{BASE_URL}/view-cart", params={"customer_id": self.customer_id})
            if not res.ok:
                raise ValueError("Failed to load cart")
            self.populate_cart(res.json().get("cart", []))
            self.show_frame("cart")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_cart_item(self, item: dict):
        new_qty = simpledialog.askinteger(
            "Edit Quantity", f"Enter new quantity for {item['product_name']}:", minvalue=1, initialvalue=item["quantity"]
        )
        if not new_qty or new_qty == item["quantity"]:
            return
        try:
            res = requests.put(
                f"{BASE_URL}/update-cart",
                json={
                    "customer_id": self.customer_id,
                    "product_id": item["product_id"],
                    "quantity": new_qty,
                },
            )
            if not res.ok:
                raise ValueError(res.json().get("message", "Update failed"))
            self.view_cart()  # refresh
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_cart_item(self, product_id: int):
        if not messagebox.askyesno("Remove", "Remove this item from cart?"):
            return
        try:
            res = requests.delete(
                f"{BASE_URL}/remove-from-cart",
                json={"customer_id": self.customer_id, "product_id": product_id},
            )

            if not res.ok:
                raise ValueError(res.json().get("message", "Remove failed"))
            self.view_cart()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def checkout(self):
        try:
            # Step 1: Fetch available credit cards
            cards_res = requests.get(f"{BASE_URL}/view-credit-cards", params={"customer_id": self.customer_id})
            if not cards_res.ok:
                raise ValueError("Unable to fetch credit cards")
            
            cards = cards_res.json().get("cards", [])
            if not cards:
                return messagebox.showinfo("No Cards", "Please add a credit card first.")

            card_choices = {str(c["card_id"]): c for c in cards}
            card_id = simpledialog.askstring(
                "Checkout",
                "Enter credit card ID to use:\n" +
                "\n".join([f"{c['card_id']}: ****{c['last4']}" for c in cards])
            )
            if not card_id or card_id not in card_choices:
                return

            # Step 2: Select delivery type
            delivery = messagebox.askyesno("Delivery", "Express delivery?\nYes = Express / No = Standard")
            delivery_type = "express" if delivery else "standard"

            # Step 3: Fetch cart contents
            cart_res = requests.get(f"{BASE_URL}/view-cart", params={"customer_id": self.customer_id})
            if not cart_res.ok:
                raise ValueError("Unable to load cart")

            cart_items = cart_res.json().get("cart", [])
            if not cart_items:
                return messagebox.showinfo("Empty Cart", "Your cart is empty.")

            products = [{"product_id": item["product_id"], "quantity": item["quantity"]} for item in cart_items]

            # Step 4: Submit order
            res = requests.post(
                f"{BASE_URL}/place-order",
                json={
                    "customer_id": self.customer_id,
                    "credit_card_id": int(card_id),
                    "delivery_type": delivery_type,
                    "products": products
                },
            )

            if res.ok:
                messagebox.showinfo("Order Placed", f"Order #{res.json()['order_id']} created!")
                self.view_cart()  # Refresh cart view after checkout
            else:
                raise ValueError(res.json().get("message", "Checkout failed"))

        except Exception as e:
            messagebox.showerror("Error", str(e))


    # ================================================================
    #  ADDRESS CRUD
    # ================================================================
    def manage_addresses(self):
        try:
            res = requests.get(f"{BASE_URL}/view-addresses", params={"customer_id": self.customer_id})
            if not res.ok:
                raise ValueError("Failed to load addresses")
            self.populate_addresses(res.json().get("addresses", []))
            self.show_frame("addresses")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_address(self):
        street = simpledialog.askstring("Add Address", "Street:")
        city = simpledialog.askstring("Add Address", "City:")
        state = simpledialog.askstring("Add Address", "State:")
        zip_code = simpledialog.askstring("Add Address", "ZIP:")
        country = simpledialog.askstring("Add Address", "Country:")
        address_type = simpledialog.askstring("Add Address", "Address Type (e.g. Home/Work):")

        if not all([street, city, state, zip_code, country, address_type]):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            res = requests.post(
                f"{BASE_URL}/add-address",
                json={
                    "customer_id": self.customer_id,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip_code": zip_code,
                    "country": country,
                    "address_type": address_type,
                },
            )
            if res.ok:
                self.manage_addresses()
            else:
                raise ValueError(res.json().get("message", "Add failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def edit_address(self, addr: dict):
        street = simpledialog.askstring("Edit Address", "Street:", initialvalue=addr["street"])
        city = simpledialog.askstring("Edit Address", "City:", initialvalue=addr["city"])
        state = simpledialog.askstring("Edit Address", "State:", initialvalue=addr["state"])
        zip_code = simpledialog.askstring("Edit Address", "ZIP:", initialvalue=addr.get("zip_code", ""))
        country = simpledialog.askstring("Edit Address", "Country:", initialvalue=addr["country"])
        if not street:
            return
        try:
            res = requests.post(
                f"{BASE_URL}/update-address",
                json={
                    "address_id": addr["address_id"],
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "country": country,
                },
            )
            if res.ok:
                self.manage_addresses()
            else:
                raise ValueError(res.json().get("message", "Update failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_address(self, address_id: int):
        if not messagebox.askyesno("Delete", "Delete this address?"):
            return
        try:
            res = requests.delete(f"{BASE_URL}/delete-address", json={"address_id": address_id})
            if res.ok:
                self.manage_addresses()
            else:
                raise ValueError(res.json().get("message", "Delete failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================================================================
    #  CARD CRUD
    # ================================================================
    def manage_cards(self):
        try:
            res = requests.get(f"{BASE_URL}/view-credit-cards", params={"customer_id": self.customer_id})
            if not res.ok:
                raise ValueError("Failed to load cards")
            self.populate_cards(res.json().get("cards", []))
            self.show_frame("cards")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_card(self):
        number = simpledialog.askstring("Add Card", "Card Number (16 digits):")
        expiry = simpledialog.askstring("Add Card", "Expiry Date (YYYY-MM-DD):")
        cvv = simpledialog.askstring("Add Card", "CVV:")
        billing_id = simpledialog.askinteger("Add Card", "Billing Address ID:")
        
        if not all([number, expiry, cvv, billing_id]):
            return

        try:
            res = requests.post(
                f"{BASE_URL}/add-credit-card",
                json={
                    "customer_id": self.customer_id,
                    "card_number": number,
                    "expiry_date": expiry,
                    "cvv": cvv,
                    "billing_address_id": billing_id
                },
            )
            if res.ok:
                self.manage_cards()
            else:
                print(f"Status: {res.status_code}")
                print(f"Text: {res.text}")
                raise ValueError(res.json().get("message", "Add failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def edit_card(self, card: dict):
        expiry = simpledialog.askstring("Edit Card", "Expiry (MM/YY):", initialvalue=card["expiry"])
        if not expiry or expiry == card["expiry"]:
            return
        try:
            res = requests.put(  # PUT instead of POST
                f"{BASE_URL}/edit-credit-card",
                json={"card_id": card["card_id"], "expiry_date": expiry},
            )

            if res.ok:
                self.manage_cards()
            else:
                raise ValueError(res.json().get("message", "Update failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_card(self, card_id: int):
        if not messagebox.askyesno("Delete", "Delete this card?"):
            return
        try:
            res = requests.delete(f"{BASE_URL}/delete-credit-card", json={"card_id": card_id})
            if res.ok:
                self.manage_cards()
            else:
                raise ValueError(res.json().get("message", "Delete failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================================================================
    #  ORDERS
    # ================================================================
    def view_orders(self):
        try:
            res = requests.get(f"{BASE_URL}/view-past-orders", params={"customer_id": self.customer_id})
            if not res.ok:
                raise ValueError("Failed to fetch orders")
            self.populate_orders(res.json().get("orders", []))
            self.show_frame("orders")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================================================================
    #  STAFF OPERATIONS
    # ================================================================
    def add_product(self):
        name = simpledialog.askstring("Add Product", "Product Name:")
        description = simpledialog.askstring("Add Product", "Description:")
        category = simpledialog.askstring("Add Product", "Category:")
        type_ = simpledialog.askstring("Add Product", "Type:")
        brand = simpledialog.askstring("Add Product", "Brand:")
        size = simpledialog.askstring("Add Product", "Size:")
        price = simpledialog.askfloat("Add Product", "Price:")
        if not name:
            return
        res = requests.post(
            f"{BASE_URL}/add-product",
            json={
                "name": name,
                "description": description,
                "category": category,
                "type": type_,
                "brand": brand,
                "size": size,
                "price": price,
            },
        )
        if res.ok:
            messagebox.showinfo("Success", "Product added")
        else:
            messagebox.showerror("Error", res.json().get("message", "Add failed"))

    def modify_product(self):
        pid = simpledialog.askinteger("Modify Product", "Enter Product ID:")
        if not pid:
            return
        field = simpledialog.askstring("Field", "Which field to modify? (name/description/category/type/brand/size)")
        if not field or field not in {"name", "description", "category", "type", "brand", "size"}:
            return
        value = simpledialog.askstring("Modify", f"Enter new value for {field}:")
        if not value:
            return
        res = requests.put(f"{BASE_URL}/modify-product", json={"product_id": pid, field: value})
        if res.ok:
            messagebox.showinfo("Success", "Product updated")
        else:
            messagebox.showerror("Error", res.json().get("message", "Update failed"))

    def delete_product(self):
        pid = simpledialog.askinteger("Delete Product", "Enter Product ID:")
        if not pid or not messagebox.askyesno("Delete", f"Delete product #{pid}?"):
            return
        res = requests.delete(f"{BASE_URL}/delete-product", json={"product_id": pid})
        if res.ok:
            messagebox.showinfo("Success", "Product deleted")
        else:
            messagebox.showerror("Error", res.json().get("message", "Delete failed"))

    def update_price(self):
        pid = simpledialog.askinteger("Update Price", "Enter Product ID:")
        price = simpledialog.askfloat("Update Price", "Enter new price:")
        if not (pid and price):
            return

        try:
            res = requests.put(f"{BASE_URL}/update-price", json={"product_id": pid, "price": price})
            if res.ok:
                messagebox.showinfo("Success", "Price updated")
            else:
                try:
                    error_msg = res.json().get("message", "Update failed")
                except ValueError:
                    error_msg = f"Non-JSON response:\n{res.status_code}\n{res.text}"
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Request Error", f"An error occurred:\n{str(e)}")


    def add_stock(self):
        pid = simpledialog.askinteger("Add Stock", "Product ID:")
        wid = simpledialog.askinteger("Add Stock", "Warehouse ID:")
        qty = simpledialog.askinteger("Add Stock", "Quantity:", minvalue=1)
        if not (pid and wid and qty):
            return
        res = requests.post(
            f"{BASE_URL}/add-stock",
            json={"product_id": pid, "warehouse_id": wid, "quantity": qty},
        )
        if res.ok:
            messagebox.showinfo("Success", "Stock updated")
        else:
            messagebox.showerror("Error", res.json().get("message", "Add stock failed"))

    # ================================================================
    #  MISC
    # ================================================================
    def logout(self):
        self.customer_id = None
        self.is_staff = False
        self.search_entry.delete(0, tk.END)
        messagebox.showinfo("Logged Out", "You have been logged out.")
        self.show_frame("main")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
