from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import CustomUserForms
from django.contrib.auth import authenticate, login, logout
from . models import *
from django.http import JsonResponse
import json

# Create your views here.
def home(request):
    products = Product.objects.filter(trending = 1)
    return render(request, 'shop/index.html', {'products':products})

def register(request):
    form = CustomUserForms()
    if request.method == 'POST':
        form = CustomUserForms(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registeration success you can login now..')
            return redirect('/login')
    return render(request, 'shop/register.html', {'form':form})

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method=='POST':
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request, username=name, password=pwd)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in Successfully')
                return redirect('/')
            else:
                messages.error(request, 'Invalid credentials')
                return redirect('/')
        return render(request, 'shop/login.html')

    
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Logged Out Successfully')
    return redirect('/')

def collections(request):
    category = Category.objects.filter(status=0)
    return render(request, 'shop/collections.html', {'category': category})


def collectionsview(request, name):
    if (Category.objects.filter(name=name, status=0)):
        products = Product.objects.filter(category__name=name)
        return render(request, 'shop/products/index.html', {'products':products, "category_name":name})
    else:
        messages.warning(request, 'No such Category Found')
        return redirect('collections')
    
def product_details(request, cname, pname):
    if(Category.objects.filter(name=cname, status=0)):
        if(Product.objects.filter(name=pname, status=0)):
            products = Product.objects.filter(name=pname, status=0).first()
            return render(request, 'shop/products/product_details.html', {'products':products})
        else:
            messages.warning(request, 'No such products Found')
            return redirect('collections')
    else:
        messages.warning(request, 'No such Category Found')
        return redirect('collections')
    

def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            # Fix: Changed default from 10 to 1
            product_qyt = int(data.get('product_qyt', 1))  
            product_id = data.get('pid')
            
            if product_qyt <= 0 or not product_id:
                return JsonResponse({'status': 'Invalid data'}, status=400)
                
            try:
                product = Product.objects.get(id=product_id)
                if product.quantity >= product_qyt:
                    cart_item, created = Cart.objects.get_or_create(
                        user=request.user,
                        product_id=product_id,
                        defaults={'product_qyt': product_qyt}
                    )
                    if not created:
                        # Check if adding more won't exceed stock
                        new_qty = cart_item.product_qyt + product_qyt
                        if new_qty <= product.quantity:
                            cart_item.product_qyt = new_qty
                            cart_item.save()
                            return JsonResponse({'status': 'Cart updated'})
                        else:
                            return JsonResponse({'status': 'Not enough stock'})
                    return JsonResponse({'status': 'Added to cart'})
                else:
                    return JsonResponse({'status': 'Out of stock'})
            except Product.DoesNotExist:
                return JsonResponse({'status': 'Product not found'}, status=404)
            except Exception as e:
                return JsonResponse({'status': f'Error: {str(e)}'}, status=500)
        else:
            return JsonResponse({'status': 'Login required'}, status=401)
    else:
        return JsonResponse({'status': 'Invalid request'}, status=400)
    
def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request, 'shop/cart.html', {'cart':cart})
    else:
        return redirect('/login')
    
    
def remove_cart(request, cid):
    cartitem = Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect('/cart')
    

def fav_page(request):
    if request.user.is_authenticated:
        if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                product_id = data.get('pid')
                product_status = Product.objects.filter(id=product_id).first()
                
                if product_status:
                    if Favourite.objects.filter(user=request.user.id, product_id=product_id):
                        return JsonResponse({'status': 'Product Already Added in Favourite'}, status=200)            
                    else:
                        Favourite.objects.create(user=request.user, product_id=product_id)
                        return JsonResponse({'status': 'Product Added to Favourite'}, status=200)
                else:
                    return JsonResponse({'status': 'Product not found'}, status=404)
            except Exception as e:
                return JsonResponse({'status': f'Error: {str(e)}'}, status=400)
        elif request.method == "GET":
            fav = Favourite.objects.filter(user=request.user)
            return render(request, 'shop/fav.html', {'fav': fav})
        else:
            return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=401)
    
def add_to_fav(request):
    if request.user.is_authenticated:
        fav=Favourite.objects.filter(user=request.user)
        return render(request, 'shop/fav.html', {'fav':fav})
    else:
        return redirect('/')
    
    
def remove_fav(request, fid):
    cartitem = Cart.objects.get(id=fid)
    cartitem.delete()
    return redirect('/fav')