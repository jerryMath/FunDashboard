from django.shortcuts import render
from .forms import *
from .filters import OrderFilter
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import *
from django.contrib.auth.models import Group
from django.http import JsonResponse, StreamingHttpResponse
from pykafka import KafkaClient


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='customer')  # a customer group
            user.groups.add(group)
            Customer.objects.create(
                user=user,
            )

            messages.success(request, f"Account was created by {username}")
            return redirect('login')

    context = {'form': form}
    return render(request, 'api/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "Username or password is incorrect")

    context = {}
    return render(request, 'api/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()
    total_orders = orders.count()
    total_delivered = orders.filter(status='Delivered').count()
    total_pending = orders.filter(status='Pending').count()

    last_five_orders = Order.objects.all().order_by('-date_created')[0:5]

    context = {'orders': orders,
               'last_five_orders': last_five_orders,
               'customers': customers,
               'total_customers': total_customers,
               'total_orders': total_orders,
               'total_delivered': total_delivered,
               'total_pending': total_pending}

    return render(request, 'api/dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    total_orders = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer': customer,
               'total_orders': total_orders,
               'orders': orders,
               'myFilter': myFilter}

    return render(request, 'api/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createCustomer(request):
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}

    return render(request, 'api/create_customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateCustomer(request, pk):
    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form,
               'customer': customer}

    return render(request, 'api/update_customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)

    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    # form = OrderForm(initial={'customer': customer})

    if request.method == 'POST':
        # form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('home')

    context = {'formset': formset}

    return render(request, 'api/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)

    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}

    return render(request, 'api/update_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context = {'order': order}

    return render(request, 'api/delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'customer'])
def userPage(request):
    user_id = request.user.id
    latest_customer = Customer.objects.filter(user_id=user_id).last()
    orders = latest_customer.order_set.all()

    total_orders = orders.count()
    total_delivered = orders.filter(status='Delivered').count()
    total_pending = orders.filter(status='Pending').count()

    context = {'orders': orders,
               'total_orders': total_orders,
               'total_delivered': total_delivered,
               'total_pending': total_pending}

    return render(request, 'api/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'api/account_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()

    return render(request, 'api/charts.html', {'products': products})


# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
# def charts(request):
#     context = {
#         'customers': 7,
#     }
#
#     return render(request, 'accounts/charts.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def get_data(request):
    item_names = []
    item_prices = []
    for ele in Product.objects.all():
        item_names.append(ele.name)
        item_prices.append(ele.price)
    data = {
        'item_names': item_names,
        'item_prices': item_prices
    }
    return JsonResponse(data)


# Kafka
def get_kafka_client():
    return KafkaClient(hosts='localhost:9092')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def bus_data(request):
    return render(request, 'api/bus.html', {})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def bus_topic(request, topic):
    client = get_kafka_client()

    def events():
        for i in client.topics[topic].get_simple_consumer():
            # yield i.value.decode()
            yield 'data:{0}\n\n'.format(i.value.decode())

    return StreamingHttpResponse(events(), content_type='text/event-stream')