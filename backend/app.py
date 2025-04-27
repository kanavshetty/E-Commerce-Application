from flask import Flask
from flask_jwt_extended import JWTManager
from api.DatabaseConnection.connection import DBConnection
from flask_cors import CORS



# ✅ Import all your API Blueprints
from api.CustomerAPI.AddressPaymentAPI.addAddress import address_api
from api.CustomerAPI.AddressPaymentAPI.editAddress import edit_address_api
from api.CustomerAPI.AddressPaymentAPI.deleteAddress import delete_address_api
from api.CustomerAPI.AddressPaymentAPI.viewAddress import view_address_api

from api.CustomerAPI.AddressPaymentAPI.CreditCardManagement.addCreditCard import credit_card_api
from api.CustomerAPI.AddressPaymentAPI.CreditCardManagement.editCreditCard import edit_credit_card_api
from api.CustomerAPI.AddressPaymentAPI.CreditCardManagement.deleteCreditCard import delete_credit_card_api
from api.CustomerAPI.AddressPaymentAPI.CreditCardManagement.viewCreditCards import view_credit_card_api

from api.CustomerAPI.CustomerAccount.customerLogin import auth_api
from api.CustomerAPI.CustomerAccount.customerRegister import customer_account_api
from api.CustomerAPI.CustomerAccount.customerChanges import customer_change_api

from api.CustomerAPI.Cart.addToCart import cart_api as add_to_cart_api
from api.CustomerAPI.Cart.removeFromCart import cart_api as remove_from_cart_api
from api.CustomerAPI.Cart.viewCart import cart_api as view_cart_api
from api.CustomerAPI.Cart.updateCartQuant import cart_api as update_cart_item_api

from api.CustomerAPI.Order.placeOrder import order_api as place_order_api
from api.CustomerAPI.Order.viewCurrentOrder import order_api as view_current_order_api
from api.CustomerAPI.Order.viewPastOrders import order_api as view_past_orders_api

from api.CustomerAPI.Cart.searchProduct import product_search_api

from api.StaffAPI.ProductManagement.addProduct import product_api as add_product_api
from api.StaffAPI.ProductManagement.modifyProduct import product_api as modify_product_api
from api.StaffAPI.ProductManagement.deleteProduct import product_api as delete_product_api
from api.StaffAPI.ProductManagement.viewProduct import product_api as view_product_api

from api.StaffAPI.Stock.addStock import stock_api as add_stock_api
from api.StaffAPI.Stock.checkInventory import stock_api as check_inventory_api
from api.StaffAPI.Stock.checkWarehouseCapacity import warehouse_api

from api.StaffAPI.OrderFulfillment.updateOrderStatus import order_api as update_order_status_api

from api.SuppliersAPI.addSupplier import supplier_api as add_supplier_api
from api.SuppliersAPI.connectSuppliertoProduct import supplier_api as connect_supplier_product_api
from api.SuppliersAPI.viewSuppliers import supplier_api as view_suppliers_api


# ✅ Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)


# ✅ Configure JWT
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change this in production!
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_SECURE'] = False  # True if using HTTPS
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

jwt = JWTManager(app)

# ✅ Register all Blueprints
# Customer Address APIs
app.register_blueprint(address_api)
app.register_blueprint(edit_address_api)
app.register_blueprint(delete_address_api)
app.register_blueprint(view_address_api)

# Customer Credit Card APIs
app.register_blueprint(credit_card_api)
app.register_blueprint(edit_credit_card_api)
app.register_blueprint(delete_credit_card_api)
app.register_blueprint(view_credit_card_api)

# Customer Account Login/Register APIs
app.register_blueprint(auth_api)
app.register_blueprint(customer_account_api)
app.register_blueprint(customer_change_api)

# Customer Cart APIs
app.register_blueprint(add_to_cart_api)
app.register_blueprint(remove_from_cart_api)
app.register_blueprint(view_cart_api)
app.register_blueprint(update_cart_item_api)

# Customer Order APIs
app.register_blueprint(place_order_api)
app.register_blueprint(view_current_order_api)
app.register_blueprint(view_past_orders_api)

# Customer Product Search
app.register_blueprint(product_search_api)

# Staff Product Management
app.register_blueprint(add_product_api)
app.register_blueprint(modify_product_api)
app.register_blueprint(delete_product_api)
app.register_blueprint(view_product_api)

# Staff Stock Management
app.register_blueprint(add_stock_api)
app.register_blueprint(check_inventory_api)
app.register_blueprint(warehouse_api)

# Staff Order Fulfillment
app.register_blueprint(update_order_status_api)

# Staff Supplier Management
app.register_blueprint(add_supplier_api)
app.register_blueprint(connect_supplier_product_api)
app.register_blueprint(view_suppliers_api)

# ✅ Home route
@app.route('/')
def home():
    return "Online Store Backend is Running!!"

# ✅ Run the app
if __name__ == '__main__':
    DBConnection.get_instance().connect()
    app.run(debug=True)
