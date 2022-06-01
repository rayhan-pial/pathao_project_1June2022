from django.urls import path
from App_main import views

app_name = 'App_main'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.customer_dashboard, name='customer_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart-view/', views.cart_showcase, name='cart-view'),
    path('update-cart/', views.cart_update, name='update-cart'),
    path('checkout/', views.checkout, name='checkout-page'),
    path('purchase/', views.purchase_action, name='purchase'),
    path('profile-view/', views.profile_view, name='profile-view'),
    # path('setiings/', views.profile_settings, name='settings'),
    path('previous-order/', views.previous_orders, name='previous-order'),
    #     Admin
    path('register-with-admin/', views.register_user_by_admin, name='register-with-admin'),
    path('update-product/', views.update_product, name='update-product'),
    path('delete-product/<int:product_key>/', views.delete_product, name='delete-product'),
    path('add-new-product/', views.add_new_product, name='add-new-product'),
    path('add-new-category/', views.add_category, name='add-new-category'),
    path('delete-shortage-record/<int:table_key>/', views.delete_shortage_table, name='delete-shortage-record'),
    path('update-order-status/', views.update_order_status, name='update-order-status'),
    path('update-order-item-quantity/', views.admin_updates_asking_quantity, name='update-order-item-quantity'),
    path('invoice-generator/<int:OrderID>/', views.admin_generates_invoice, name='invoice-generator'),
    #     Admin
    path('boss-admin/', views.boss_admin_dashboard, name='boss_admin_dashboard'),
    path('admin-register-with-bossAdmin/', views.register_Adminuser_by_boss_admin, name='admin-register-with-bossAdmin'),
    path('user-register-with-bossAdmin/', views.register_user_by_boss_admin, name='user-register-with-bossAdmin'),
    path('boss-update-product/', views.boss_update_product, name='boss-update-product'),
    path('boss-delete-product/<int:product_key>/', views.boss_delete_product, name='boss-delete-product'),
    path('boss-add-new-product/', views.boss_add_new_product, name='boss-add-new-product'),
    path('boss-add-new-category/', views.boss_add_category, name='boss-add-new-category'),
    path('boss-delete-shortage-record/<int:table_key>/', views.boss_delete_shortage_table,
         name='boss-delete-shortage-record'),
    path('boss-update-order-status/', views.boss_update_order_status, name='boss-update-order-status'),
    path('boss-update-order-item-quantity/', views.boss_admin_updates_asking_quantity,
         name='boss-update-order-item-quantity'),
    path('boss-invoice-generator/<int:OrderID>/', views.boss_admin_generates_invoice, name='boss-invoice-generator'),
    # ISD
    path('ISD-admin/', views.ISD_admin_dashboard, name='ISD_admin_dashboard'),
    path('register-with-Isd-admin/', views.ISD_admin_register_customer, name='register-with-isd-admin'),
    path('Isd-update-product/', views.ISD_update_product, name='ISD-update-product'),
    path('Isd-delete-product/<int:product_key>/', views.ISD_delete_product, name='ISD-delete-product'),
    path('Isd-add-new-product/', views.ISD_add_new_product, name='ISD-add-new-product'),
    path('Isd-add-new-category/', views.ISD_add_category, name='ISD-add-new-category'),
    path('Isd-delete-shortage-record/<int:table_key>/', views.ISD_delete_shortage_table,
         name='ISD-delete-shortage-record'),
    path('Isd-update-order-status/', views.ISD_update_order_status, name='ISD-update-order-status'),
    path('Isd-update-order-item-quantity/', views.ISD_admin_updates_asking_quantity,
         name='ISD-update-order-item-quantity'),
    path('Isd-invoice-generator/<int:OrderID>/', views.ISD_admin_generates_invoice, name='ISD-invoice-generator'),
    # OSD
    path('OSD-admin/', views.OSD_admin_dashboard, name='OSD_admin_dashboard'),
    path('register-with-osd-admin/', views.OSD_admin_register_customer, name='register-with-osd-admin'),
    path('osd-update-product/', views.OSD_update_product, name='osd-update-product'),
    path('osd-delete-product/<int:product_key>/', views.OSD_delete_product, name='osd-delete-product'),
    path('osd-add-new-product/', views.OSD_add_new_product, name='osd-add-new-product'),
    path('osd-add-new-category/', views.OSD_add_category, name='osd-add-new-category'),
    path('osd-delete-shortage-record/<int:table_key>/', views.OSD_delete_shortage_table,
         name='osd-delete-shortage-record'),
    path('osd-update-order-status/', views.OSD_update_order_status, name='osd-update-order-status'),
    path('osd-update-order-item-quantity/', views.OSD_admin_updates_asking_quantity,
         name='osd-update-order-item-quantity'),
    path('osd-invoice-generator/<int:OrderID>/', views.OSD_admin_generates_invoice, name='osd-invoice-generator'),
    path('this_month_orders/', views.this_month_orders, name='this-month-order'),
]
