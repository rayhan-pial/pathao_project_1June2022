import json
import uuid

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.checks import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import Group

# Create your views here.
from django.urls import reverse

from App_auth.forms import SignUpForm
from App_auth.models import Profile, User
from App_auth.views import is_customer, is_admin, is_boss_admin, is_admin_ISD, is_admin_OSD
from App_main.forms import BillingForm, ProfileForm, ProductModelForm, CustomerAddressForm
from App_main.models import ProductModel, Cart, Order, BillingAddress, ShortageOfProduct, CategoryModel


@login_required
@user_passes_test(is_customer)
def customer_dashboard(request):
    c = Cart.objects.filter(user=request.user)
    products = ProductModel.objects.all()
    total_cart = Cart.objects.filter(user=request.user, purchased=False)
    cart_prod = [x.item.product_name for x in total_cart]
    content = {
        'products': products,
        'cart': total_cart,
        'prod_name': cart_prod
    }
    return render(request, 'App_main/customer_dashboard.html', context=content)


@login_required
@user_passes_test(is_customer)
def add_to_cart(request):
    pk = request.POST.get('product_id')
    quantity = int(request.POST.get('product_asking_quantity'))
    prod = ProductModel.objects.get(id=pk)
    try:
        cart_item = Cart.objects.get(user=request.user, item=prod, purchased=False)
        cart_item.quantity += quantity
        cart_item.save()
    except:
        cart_item = Cart.objects.create(user=request.user, item=prod, quantity=quantity, purchased=False)
        cart_item.save()
    return HttpResponseRedirect(reverse('App_main:customer_dashboard'))


@login_required
@user_passes_test(is_customer)
def cart_showcase(request):
    carts = Cart.objects.filter(user=request.user, purchased=False)
    content = {
        'carts': carts
    }
    return render(request, 'App_main/cartView.html', context=content)


@login_required
@user_passes_test(is_customer)
def cart_update(request):
    pk = request.POST.get('product_id')
    quantity = int(request.POST.get('new_asking_quantity'))
    prod = ProductModel.objects.get(id=pk)
    cart_item = Cart.objects.get(user=request.user, item=prod, purchased=False)
    cart_item.quantity = quantity
    cart_item.save()
    return HttpResponseRedirect(reverse('App_main:cart-view'))


def total_price_count(List, total):
    if len(List) == 0:
        return total
    else:
        i = List[0]
        total += i.quantity * i.item.price_per_unit
        List.remove(i)
        return total_price_count(List, total)


@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    form = BillingForm(instance=saved_address)
    if request.method == "POST":
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingForm(instance=saved_address)
            messages.info(request, f"Shipping address saved!")

    cartItems = Cart.objects.filter(user=request.user, purchased=False)
    orderTotal = total_price_count(list(cartItems), 0)
    content = {
        'form': form,
        'cartItems': cartItems,
        'orderTotal': orderTotal,
        'saved_address': saved_address
    }
    return render(request, 'App_main/checkout.html', context=content)


def add_to_order(cart, order, total):
    if len(cart) == 0:
        return order
    else:
        i = cart[0]
        order.order_items.add(i)
        order.ordered = True
        order.payment_id = str(i.user)
        order.status = "Processing"
        order.order_id = str(i.user) + "-" + str(order.id)
        order.total_price = total
        cart.remove(i)
        return add_to_order(cart, order, total)


def delete_list(l_Delete):
    if len(l_Delete) == 0:
        return 0
    else:
        l_Delete[0].delete()
        delete_list(l_Delete)


@login_required
def purchase_action(request):
    order = Order.objects.create(user=request.user)
    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    total = total_price_count(list(cart_items), 0)
    add_to_order(list(cart_items), order, total).save()
    for item in cart_items:
        product = ProductModel.objects.get(id=item.item.id)
        if product.No_of_available < item.quantity:
            shortage = ShortageOfProduct(product=product)
            storageAmount = item.quantity - product.No_of_available
            shortage.storageAmount = storageAmount
            shortage.save()
            product.No_of_available = 0
        else:
            product.No_of_available -= item.quantity
        product.save()
        item.purchased = True
        item.save()
        orderDelete = Order.objects.filter(user=request.user, payment_id=None)
        delete_list(orderDelete)

    return HttpResponseRedirect(reverse('App_main:customer_dashboard'))


def profile_view(request):
    profile = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm()
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            thisForm = form.save(commit=False)
            thisForm.user = request.user
            thisForm.save()
            return HttpResponseRedirect(reverse('App_main:profile-view'))

    content = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'App_main/profile_view.html', context=content)


# def profile_settings(request):
#     profile = Profile.objects.get(user=request.user)
#     form = ProfileForm(instance=profile)
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             thisForm = form.save(commit=False)
#             thisForm.user = request.user
#             thisForm.save()
#             return HttpResponseRedirect(reverse('App_main:settings'))
#
#     content = {
#         'form': form
#     }
#     return render(request, 'App_main/settings.html', context=content)


@login_required
@user_passes_test(is_customer)
def previous_orders(request):
    previous_order = Order.objects.filter(user=request.user)
    content = {
        'previous_orders': previous_order
    }
    return render(request, 'App_main/previous_orders.html', context=content)


# <! ------- Admin Start ------->
def checkAdmin(userList, x_result):
    if len(userList) == 0:
        return x_result
    else:
        if is_admin(userList[0]):
            pass
        else:
            x_result.append(userList[0])
        userList.remove(userList[0])
        return checkAdmin(userList, x_result)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    form = SignUpForm()
    customerForm = CustomerAddressForm()
    total_user = User.objects.filter(is_superuser=False)
    allCustomers = checkAdmin(list(total_user), [])
    total_customer = len(allCustomers)
    total_product = ProductModel.objects.all()
    total_orders = Order.objects.filter(status="Final approval from admin")
    completed_orders = Order.objects.filter(status='Completed')
    pending_order = []
    for i, j in zip(total_orders, completed_orders):
        if j == i:
            pass
        else:
            pending_order.append(i)
    total_shortages = ShortageOfProduct.objects.all()
    content = {
        'all_customers': allCustomers,
        'total_customer': total_customer,
        'total_product': total_product,
        'total_orders': total_orders,
        'total_shortage': total_shortages,
        'signupForm': form,
        'customerAddressForm': customerForm,
    }
    return render(request, 'App_main/Admin_dashboard.html', context=content)


@login_required
@user_passes_test(is_admin)
def admin_updates_asking_quantity(request):
    if request.method == 'POST':
        orderID = request.POST.get('orderID')
        quantity = request.POST.getlist('quantity')
        theOrders = Order.objects.get(id=orderID)
        for i, j in zip(theOrders.order_items.all(), quantity):
            j_int = int(j)
            if i.quantity < j_int:
                i.item.No_of_available -= (j_int - i.quantity)
            elif i.quantity > j_int:
                i.item.No_of_available += (i.quantity - j_int)
            i.item.save()
            i.quantity = j
            i.save()

        return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def update_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        product = ProductModel.objects.get(id=product_id)
        if price == "" and quantity == "":
            return HttpResponseRedirect(reverse('App_main:admin_dashboard'))
        elif price != "" and quantity != "":
            product.No_of_available += int(quantity)
            product.price_per_unit = int(price)
            product.save()
        elif quantity == "":
            product.price_per_unit = int(price)
            product.save()
        elif price == "":
            product.No_of_available += int(quantity)
            product.save()
    return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def delete_product(request, product_key):
    product = ProductModel.objects.get(id=product_key)
    product.delete()
    return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def delete_shortage_table(request, table_key):
    shortage_table = ShortageOfProduct.objects.get(id=table_key)
    shortage_table.delete()
    return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def register_user_by_admin(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        form2 = CustomerAddressForm(request.POST)
        if form.is_valid() and form2.is_valid():
            user = form.save()
            customerAddress = form2.save()
            sec_phone = form2.cleaned_data.get('primary_phone_number')
            prof = Profile(user=user, shop=customerAddress,
                           secondary_phone_number=sec_phone)
            prof.save()
            my_admin_group = Group.objects.get_or_create(name='CUSTOMER')
            my_admin_group[0].user_set.add(user)
            messages.info(request, "Successfully Registered")
            return HttpResponseRedirect(reverse('App_main:admin_dashboard'))
        else:
            messages.info(request, "Password doesn't match!!!")
            return redirect('App_main:admin_dashboard')


@login_required
@user_passes_test(is_admin)
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.status = request.POST.get("status_change")
        order.save()
        return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
def add_new_product(request):
    form = ProductModelForm()
    if request.method == 'POST':
        form = ProductModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('App_main:add-new-product'))

    content = {
        'form': form,
    }
    return render(request, 'App_main/add_new_product.html', context=content)


@login_required
def add_category(request):
    if request.method == 'POST':
        cat = request.POST.get('cat-name')
        category = CategoryModel(name=cat)
        category.save()
        return HttpResponseRedirect(reverse('App_main:add-new-product'))


@login_required
def admin_generates_invoice(request, OrderID):
    order = Order.objects.get(id=OrderID)
    total = list(range(1, len(order.order_items.all()) + 1))
    zip_item = zip(total, list(order.order_items.all()))
    content = {
        'order': order,
        'total_and_order': zip_item,
    }
    return render(request, 'App_main/invoice_page.html', context=content)


# <! ------- Super Admin Start ------->

@login_required
@user_passes_test(is_boss_admin)
def boss_admin_dashboard(request):
    form = SignUpForm()
    customerForm = CustomerAddressForm()
    total_user = User.objects.filter(is_superuser=False)
    allCustomers = checkAdmin(list(total_user), [])
    total_customer = len(allCustomers)
    total_product = ProductModel.objects.all()
    total_orders = Order.objects.all()
    completed_orders = Order.objects.filter(status='Completed')
    pending_order = []
    for i, j in zip(total_orders, completed_orders):
        if j == i:
            pass
        else:
            pending_order.append(i)
    total_shortages = ShortageOfProduct.objects.all()
    content = {
        'all_customers': allCustomers,
        'total_customer': total_customer,
        'total_product': total_product,
        'total_orders': total_orders,
        'total_shortage': total_shortages,
        'signupForm': form,
        'customerAddressForm': customerForm,
    }
    return render(request, 'App_main/Boss_Admin_dashboard.html', context=content)


@login_required
@user_passes_test(is_boss_admin)
def boss_admin_updates_asking_quantity(request):
    if request.method == 'POST':
        orderID = request.POST.get('orderID')
        quantity = request.POST.getlist('quantity')
        theOrders = Order.objects.get(id=orderID)
        for i, j in zip(theOrders.order_items.all(), quantity):
            j_int = int(j)
            if i.quantity < j_int:
                i.item.No_of_available -= (j_int - i.quantity)
            elif i.quantity > j_int:
                i.item.No_of_available += (i.quantity - j_int)
            i.item.save()
            i.quantity = j
            i.save()
        return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def boss_update_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        product = ProductModel.objects.get(id=product_id)
        if price == "" and quantity == "":
            return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))
        elif price != "" and quantity != "":
            product.No_of_available += int(quantity)
            product.price_per_unit = int(price)
            product.save()
        elif quantity == "":
            product.price_per_unit = int(price)
            product.save()
        elif price == "":
            product.No_of_available += int(quantity)
            product.save()
    return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def boss_delete_product(request, product_key):
    product = ProductModel.objects.get(id=product_key)
    product.delete()
    return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def boss_delete_shortage_table(request, table_key):
    shortage_table = ShortageOfProduct.objects.get(id=table_key)
    shortage_table.delete()
    return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def register_Adminuser_by_boss_admin(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                adminCheckbox = request.POST.get('admin-type')
            except:
                adminCheckbox = None
                messages.info(request, "There are some problems!!!")
                return redirect('App_main:boss_admin_dashboard')
            if adminCheckbox:
                my_admin_group = Group.objects.get_or_create(name=adminCheckbox)
                my_admin_group[0].user_set.add(user)
                return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))
        else:
            messages.info(request, "Check your inputs again. You might make some mistake!!!")
            return redirect('App_main:boss_admin_dashboard')


def register_user_by_boss_admin(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        form2 = CustomerAddressForm(request.POST)
        if form.is_valid() and form2.is_valid():
            user = form.save()
            customerAddress = form2.save()
            sec_phone = form2.cleaned_data.get('primary_phone_number')
            prof = Profile(user=user, shop=customerAddress,
                           secondary_phone_number=sec_phone)
            prof.save()
            my_admin_group = Group.objects.get_or_create(name='CUSTOMER')
            my_admin_group[0].user_set.add(user)
            messages.info(request, "Successfully Registered")
            return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))
        else:
            messages.info(request, "Password doesn't match!!!")
            return redirect('App_main:boss_admin_dashboard')



@login_required
@user_passes_test(is_boss_admin)
def boss_update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.status = request.POST.get("status_change")
        order.save()
        return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def boss_add_new_product(request):
    form = ProductModelForm()
    if request.method == 'POST':
        form = ProductModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('App_main:boss-add-new-product'))

    content = {
        'form': form,
    }
    return render(request, 'App_main/boss_add_new_product.html', context=content)


@login_required
@user_passes_test(is_boss_admin)
def boss_add_category(request):
    if request.method == 'POST':
        cat = request.POST.get('cat-name')
        category = CategoryModel(name=cat)
        category.save()
        return HttpResponseRedirect(reverse('App_main:boss-add-new-product'))


@login_required
@user_passes_test(is_boss_admin)
def boss_admin_generates_invoice(request, OrderID):
    order = Order.objects.get(id=OrderID)
    total = list(range(1, len(order.order_items.all()) + 1))
    zip_item = zip(total, list(order.order_items.all()))
    content = {
        'order': order,
        'total_and_order': zip_item,
    }
    return render(request, 'App_main/invoice_page.html', context=content)


# <!-- Admin OSD -->

@login_required
@user_passes_test(is_admin_OSD)
def OSD_admin_dashboard(request):
    form = SignUpForm()
    customerForm = CustomerAddressForm()
    total_user = User.objects.filter(is_superuser=False, groups=2)
    t_user = []
    for i in total_user:
        try:
            if i.profile_user.shop.city != "Dhaka":
                t_user.append(i)
        except:
            pass
    total_customer = len(t_user)
    total_product = ProductModel.objects.all()
    total_orders = Order.objects.all()
    t_order = []
    for i in total_orders:
        try:
            if i.user.profile_user.shop.city != "Dhaka":
                t_order.append(i)
        except:
            pass
    completed_orders = Order.objects.filter(status='Completed')
    pending_order = []
    for i, j in zip(total_orders, completed_orders):
        if j == i:
            pass
        else:
            pending_order.append(i)
    total_shortages = ShortageOfProduct.objects.all()
    content = {
        'all_customers': t_user,
        'total_customer': total_customer,
        'total_product': total_product,
        'total_orders': t_order,
        'no_of_total_orders': len(t_order),
        'total_shortage': total_shortages,
        'signupForm': form,
        'customerAddressForm': customerForm,
    }
    return render(request, 'App_main/OSD_Admin_dashboard.html', context=content)


@login_required
@user_passes_test(is_admin_OSD)
def OSD_admin_updates_asking_quantity(request):
    if request.method == 'POST':
        orderID = request.POST.get('orderID')
        quantity = request.POST.getlist('quantity')
        theOrders = Order.objects.get(id=orderID)
        for i, j in zip(theOrders.order_items.all(), quantity):
            j_int = int(j)
            if i.quantity < j_int:
                i.item.No_of_available -= (j_int - i.quantity)
            elif i.quantity > j_int:
                i.item.No_of_available += (i.quantity - j_int)
            i.item.save()
            i.quantity = j
            i.save()
        return HttpResponseRedirect(reverse('App_main:OSD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_OSD)
def OSD_update_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        product = ProductModel.objects.get(id=product_id)
        if price == "" and quantity == "":
            return HttpResponseRedirect(reverse('App_main:OSD_admin_dashboard'))
        elif price != "" and quantity != "":
            product.No_of_available += int(quantity)
            product.price_per_unit = int(price)
            product.save()
        elif quantity == "":
            product.price_per_unit = int(price)
            product.save()
        elif price == "":
            product.No_of_available += int(quantity)
            product.save()
    return HttpResponseRedirect(reverse('App_main:OSD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_OSD)
def OSD_delete_product(request, product_key):
    product = ProductModel.objects.get(id=product_key)
    product.delete()
    return HttpResponseRedirect(reverse('App_main:OSD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_OSD)
def OSD_delete_shortage_table(request, table_key):
    shortage_table = ShortageOfProduct.objects.get(id=table_key)
    shortage_table.delete()
    return HttpResponseRedirect(reverse('App_main:OSD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_OSD)
def OSD_admin_register_customer(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        form2 = CustomerAddressForm(request.POST)
        if form.is_valid() and form2.is_valid():
            user = form.save()
            customerAddress = form2.save()
            sec_phone = form2.cleaned_data.get('primary_phone_number')
            prof = Profile(user=user, shop=customerAddress,
                           secondary_phone_number=sec_phone)
            prof.save()
            my_admin_group = Group.objects.get_or_create(name='CUSTOMER')
            my_admin_group[0].user_set.add(user)
            messages.info(request, "Successfully Registered")
            return HttpResponseRedirect(reverse('App_main:OSD_admin_dashboard'))
        else:
            messages.info(request, "Password doesn't match!!!")
            return redirect('App_main:OSD_admin_dashboard')


@login_required
@user_passes_test(is_admin_OSD)
def OSD_update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.status = request.POST.get("status_change")
        order.save()
        return HttpResponseRedirect(reverse('App_main:OSD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_OSD)
def OSD_add_new_product(request):
    form = ProductModelForm()
    if request.method == 'POST':
        form = ProductModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('App_main:OSD-add-new-product'))

    content = {
        'form': form,
    }
    return render(request, 'App_main/OSD_Admin_add_new_product.html', context=content)


@login_required
@user_passes_test(is_admin_OSD)
def OSD_add_category(request):
    if request.method == 'POST':
        cat = request.POST.get('cat-name')
        category = CategoryModel(name=cat)
        category.save()
        return HttpResponseRedirect(reverse('App_main:OSD-add-new-product'))


@login_required
@user_passes_test(is_admin_OSD)
def OSD_admin_generates_invoice(request, OrderID):
    order = Order.objects.get(id=OrderID)
    total = list(range(1, len(order.order_items.all()) + 1))
    zip_item = zip(total, list(order.order_items.all()))
    content = {
        'order': order,
        'total_and_order': zip_item,
    }
    return render(request, 'App_main/invoice_page.html', context=content)


# <!-- Admin ISD -->

@login_required
@user_passes_test(is_admin_ISD)
def ISD_admin_dashboard(request):
    form = SignUpForm()
    customerAddressForm = CustomerAddressForm()
    total_user = User.objects.filter(is_superuser=False, groups=2)
    t_user = []
    for i in total_user:
        try:
            if i.profile_user.shop.city == "Dhaka":
                t_user.append(i)
        except:
            pass
    total_customer = len(t_user)
    total_product = ProductModel.objects.all()
    total_orders = Order.objects.all()
    t_order = []
    for i in total_orders:
        try:
            if i.user.profile_user.shop.city == "Dhaka":
                t_order.append(i)
        except:
            pass
    completed_orders = Order.objects.filter(status='Completed')
    pending_order = []
    for i, j in zip(total_orders, completed_orders):
        if j == i:
            pass
        else:
            pending_order.append(i)
    total_shortages = ShortageOfProduct.objects.all()
    content = {
        'all_customers': t_user,
        'total_customer': total_customer,
        'total_product': total_product,
        'total_orders': total_orders,
        'total_shortage': total_shortages,
        'signupForm': form,
        'customerAddressForm': customerAddressForm,
    }
    return render(request, 'App_main/ISD_Admin_dashboard.html', context=content)


@login_required
@user_passes_test(is_admin_ISD)
def ISD_admin_updates_asking_quantity(request):
    if request.method == 'POST':
        orderID = request.POST.get('orderID')
        quantity = request.POST.getlist('quantity')
        theOrders = Order.objects.get(id=orderID)
        for i, j in zip(theOrders.order_items.all(), quantity):
            j_int = int(j)
            if i.quantity < j_int:
                i.item.No_of_available -= (j_int - i.quantity)
            elif i.quantity > j_int:
                i.item.No_of_available += (i.quantity - j_int)
            i.item.save()
            i.quantity = j
            i.save()
        return HttpResponseRedirect(reverse('App_main:ISD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_ISD)
def ISD_update_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        product = ProductModel.objects.get(id=product_id)
        if price == "" and quantity == "":
            return HttpResponseRedirect(reverse('App_main:ISD_admin_dashboard'))
        elif price != "" and quantity != "":
            product.No_of_available += int(quantity)
            product.price_per_unit = int(price)
            product.save()
        elif quantity == "":
            product.price_per_unit = int(price)
            product.save()
        elif price == "":
            product.No_of_available += int(quantity)
            product.save()
    return HttpResponseRedirect(reverse('App_main:ISD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_ISD)
def ISD_delete_product(request, product_key):
    product = ProductModel.objects.get(id=product_key)
    product.delete()
    return HttpResponseRedirect(reverse('App_main:ISD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_ISD)
def ISD_delete_shortage_table(request, table_key):
    shortage_table = ShortageOfProduct.objects.get(id=table_key)
    shortage_table.delete()
    return HttpResponseRedirect(reverse('App_main:ISD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_ISD)
def ISD_admin_register_customer(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        form2 = CustomerAddressForm(request.POST)
        if form.is_valid() and form2.is_valid():
            user = form.save()
            customerAddress = form2.save()
            sec_phone = form2.cleaned_data.get('primary_phone_number')
            prof = Profile(user=user, shop=customerAddress,
                           secondary_phone_number=sec_phone)
            prof.save()
            my_admin_group = Group.objects.get_or_create(name='CUSTOMER')
            my_admin_group[0].user_set.add(user)
            messages.info(request, "Successfully Registered")
            return HttpResponseRedirect(reverse('App_main:ISD_admin_dashboard'))
        else:
            messages.info(request, "Password doesn't match!!!")
            return redirect('App_main:ISD_admin_dashboard')


@login_required
@user_passes_test(is_admin_ISD)
def ISD_update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.status = request.POST.get("status_change")
        order.save()
        return HttpResponseRedirect(reverse('App_main:ISD_admin_dashboard'))


@login_required
@user_passes_test(is_admin_ISD)
def ISD_add_new_product(request):
    form = ProductModelForm()
    if request.method == 'POST':
        form = ProductModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('App_main:ISD-add-new-product'))

    content = {
        'form': form,
    }
    return render(request, 'App_main/ISD_Admin_add_new_product.html', context=content)


@login_required
@user_passes_test(is_admin_ISD)
def ISD_add_category(request):
    if request.method == 'POST':
        cat = request.POST.get('cat-name')
        category = CategoryModel(name=cat)
        category.save()
        return HttpResponseRedirect(reverse('App_main:ISD-add-new-product'))


@login_required
@user_passes_test(is_admin_ISD)
def ISD_admin_generates_invoice(request, OrderID):
    order = Order.objects.get(id=OrderID)
    total = list(range(1, len(order.order_items.all()) + 1))
    zip_item = zip(total, list(order.order_items.all()))
    content = {
        'order': order,
        'total_and_order': zip_item,
    }
    return render(request, 'App_main/invoice_page.html', context=content)


diction = {
    "January": 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12,
}

@login_required
def this_month_orders(request):
    content = {
    }
    order_this_month = {}
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        total_order_in_that_month = Order.objects.filter(created__month=diction[month], created__year=year, status="Completed")
        content['order_of_this_month'] = total_order_in_that_month
    return render(request, 'App_main/this_month_orders.html', context=content)


@login_required
def home(request):
    user_ = request.user
    if is_admin(user_):
        return HttpResponseRedirect(reverse('App_main:admin_dashboard'))
    if is_admin_OSD(user_):
        return HttpResponseRedirect(reverse('App_main:OSD_admin_dashboard'))
    if is_admin_ISD(user_):
        return HttpResponseRedirect(reverse('App_main:ISD_admin_dashboard'))
    if is_boss_admin(user_):
        return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))
