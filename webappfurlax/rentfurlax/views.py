from django.http  import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
# from app.forms import CustomUserChangeForm
from django.contrib.auth import login, authenticate, logout #add this
from django.contrib import messages, auth
from django.contrib.auth.forms import AuthenticationForm
from rentfurlax.models import Category, Furniture, Profile, RentalOptions,Invoice, LineItem
from django.contrib.auth.models import User # new

from datetime import datetime
from datetime import timedelta
from datetime import date
#from django.contrib.sessions.models import Session Session.objects.all().delete()
def homePage(request):
    return render(request , "index.html")

def loginPage(request):
    print('login page', request.method)
    if request.method == "POST":
        form = AuthenticationForm(request, data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                print('login success', username)
                return redirect("/dashboard")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "login.html",{"login_form":form})

def registerPage(request):
    #request.query_params
    print('register ', request.method)
    if request.method == "POST":
        user = User.objects.create_user(request.POST['username'],
                                        password=request.POST['password1'], 
                                        email=request.POST['email'],
                                        first_name=request.POST['fname'], 
                                        last_name=request.POST['lname'])
        profile = Profile.objects.create(user=user,phone= request.POST['phone'], address = request.POST['address'])
        #auth.login(request,user)
        messages.success(request, "Registration successful." )
        return redirect('/login')
    return render (request, "register.html")

def logoutPage(request):
    try:
        del request.session['cartitems']
    except:
        pass
	
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("/")

def addToCartItem(request, category, id):
    print('id add to cart', id)
    rental = request.GET['rental']
    if not request.user.is_authenticated:
         return redirect('/item/'+category+'/'+str(id)+"?message=Please login")
    cartitems = []
    if request.session.get('cartitems'):
        cartitems = request.session.get('cartitems')
        print(cartitems)
        for item in cartitems:
            print('id in if', item['id'], type(item['id']))
            if int(item['id']) == id:
                print('item already added')
                return redirect('/item/'+category+'/'+str(id)+'?msg=Item already added')
            
        cartitems.append({"id":id,"rentalid":rental})
        request.session['cartitems'] = cartitems
    else:
        print('else')
        cartitems = [{"id":id, 'rentalid':rental}]
        request.session['cartitems'] = cartitems
    print('3',request.session.get('cartitems'))
    return redirect('/item/'+category+'/'+str(id))

def dashboardPage(request):
    return render(request , "dashboard.html")

def itemPage(request, category): 
    print('item page')   
    categoryobj = Category.objects.get(type=category)
    items = Furniture.objects.filter(category=categoryobj)
    #print(items)
    data={"items":items,"title":category}
    if not items:
         data={"items":items,"title":category}
         return render(request , "item.html", data)
    rentals = []
    for item in items:
        rentals.append(item.rentaloptions.get(tenure=3))
 
    #print('rentals',rentals)
    zipped = zip(items, rentals)
    data = {"items": zipped, "title":category}
    return render(request , "item.html", data)

def detailsPage(request, category, id):    
    furniture = Furniture.objects.get(pk=id)
    rentals = furniture.rentaloptions.values()
    #print(furniture)
    #print(rentals)

    # calculating end date by adding 4 days
    deliverydate = date.today() + timedelta(days=furniture.noofdays)
    data = {"id":id,"furniture":furniture,"rentals":rentals,
            "deldate":deliverydate}
    return render(request , "details.html", data)

def cartPage(request):
    if not request.session.get('cartitems'):
         return redirect('/')
    cartitems = request.session.get('cartitems')
    order = []
    total = 0
    for item in cartitems:
        furniture = Furniture.objects.get(pk=item['id'])
        rental = RentalOptions.objects.get(pk=item['rentalid'])
        deliverydate = date.today() + timedelta(days=furniture.noofdays)

        cartobj = {"name":furniture.name, "deldate":  deliverydate,
                    "imageurl":furniture.imageurl, "color":furniture.color
                    ,"size":furniture.size,
                    "tenure":rental.tenure,"price":rental.ratepermonth
                    }
        total += rental.ratepermonth * rental.tenure
        order.append(cartobj)
    print('\n**********************************')
    print(order)
    print(total)
    print('\n**********************************')
    return render(request , "cart.html",{"cartitems":order,"total":total})

def checkoutPage(request):
    cartitems = request.session.get('cartitems')
    order = []
    total = 0
    username = request.user
    customer = User.objects.get(username=username)
    print('customer',customer)
    profile = Profile.objects.get(user=customer)
    print('profile',profile)
    invoice = Invoice.objects.create(customer=customer,
                                     deliveryaddress=profile.address,
                                     status='ORDERED', orderdate=date.today())
   
    for item in cartitems:
        furniture = Furniture.objects.get(pk=item['id'])
        rental = RentalOptions.objects.get(pk=item['rentalid'])
        #deliverydate = date.today() + timedelta(days=furniture.noofdays)
        total += rental.ratepermonth * rental.tenure
        lineitem = LineItem.objects.create(invoice=invoice,
                                           rentalOptions=rental,quantity=1, total=rental.ratepermonth * rental.tenure,
                                   deliverydate=date.today() + timedelta(days=furniture.noofdays))
        
    Invoice.objects.filter(pk=invoice.id).update(invoiceamount=total)
    invoice_instance = Invoice.objects.get(id=invoice.id)
    print('invoice', invoice_instance)
    try:
        del request.session['cartitems']
        request.session.modified = True
    except:
        pass
    return render(request , "checkout.html",{"invoice":invoice_instance})

def orderPage(request):
    username = request.user
    customer = User.objects.get(username=username)
    invoices = Invoice.objects.filter(customer=customer)
    return render(request, "orders.html", {"invoices":invoices})
    