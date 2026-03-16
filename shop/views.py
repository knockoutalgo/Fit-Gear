from django.shortcuts import render,redirect
from django.http import HttpResponse
from urllib3 import request
from .models import Thing,Comment,Vote,CartItem
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import ThingForm,CommentForm
from django.contrib.auth import logout,login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db.models import Count

# Create your views here.

def mylogout(request):
    if request.method=='POST':
        logout(request)
        return redirect('shop:login')
    return render(request,'shop/logout.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop:shoppy')
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            #creates a session stores user_id 
            #sends sessionid cookie to browser
            #So after login, browser has:
            # sessionid=abc123
            # That’s it. No user data, no role, no permissions in cookie.
            login(request,user)
            return redirect('shop:shoppy')
        else :
            messages.error(request,"Invalid UserName or Password")
            return redirect('shop:login')
    return render(request,'shop/login.html')

# @login_required(login_url='shop:login')

def register(request):
    if request.user.is_authenticated:
        return redirect('shop:shoppy')
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        
        if not username or not email or not password or not confirm_password:
            messages.error(request,"All Fields are required")
            return redirect('shop:register')
        
        if password!=confirm_password:
            messages.error(request,"Password is not matching")
            return render(request,'shop/register.html',{
                'username':username,
                'email':email
            })
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "shop/register.html")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Use diff email this is in use.")
            return render(request, "shop/register.html")
        
        User.objects.create_user(username=username, email=email, password=password)

        messages.success(request,"Succesfully Registered !")

        return redirect('shop:login')
    
    return render(request,'shop/register.html')


@login_required(login_url='shop:login')
def shop(request):
    q = request.GET.get("q", "")
    thing = Thing.objects.all()
    print("Thing count in web:", thing.count())
    if q:
        thing = thing.filter(
            Q(title__icontains=q) | 
            Q(body__icontains=q)
        ).distinct()
    return render(request,'shop/base.html',{'samaan':thing, "q": q})

@login_required(login_url='shop:login')
def read(request, pk):
    thing = get_object_or_404(Thing, pk=pk)

    comments = thing.comments.select_related("user").order_by("-created_at")
    likes = thing.votes.filter(value=1).count()
    dislikes = thing.votes.filter(value=-1).count()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.thing = thing
            comment.user = request.user
            comment.save()
            return redirect("shop:read", pk=thing.pk)
    else:
        form = CommentForm()
    return render(
        request,
        "shop/read.html",
        {
            "s": thing,
            "comments": comments,
            "comment_form": form,
            "likes": likes,
            "dislikes": dislikes,
        },
    )

@login_required(login_url='shop:login')
def delete(request, pk):
    thing=get_object_or_404(Thing,pk=pk)

    if thing.user != request.user:
        print("holla")
        messages.error(request, "You are not allowed to delete this item.")
        return redirect('shop:shoppy')   # redirect to home

    if request.method == "POST":
        print("ko")
        thing.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('shop:shoppy')

    return render(request, 'shop/delete.html', {'perti': thing})

@login_required(login_url='shop:login')
def create(request):
    if request.method=='POST':
        form=ThingForm(request.POST)
        if form.is_valid():
            thing=form.save(commit=False)
            thing.user=request.user
            thing.save()
            return redirect('shop:shoppy')
    else:
        form=ThingForm()
    return render(request, 'shop/update.html',{'form': form})


@login_required(login_url='shop:login')
def update(request,pk):
    thing = get_object_or_404(Thing, user=request.user, pk=pk)

    if request.method=='POST':
        form=ThingForm(request.POST,request.FILES,instance=thing)
        if form.is_valid():
            form.save()
            return redirect ('shop:shoppy')
    else :
        form=ThingForm(instance=thing)

    return render(request,'shop/update.html',{'form':form})

@login_required(login_url='shop:login')
@require_POST
def vote_thing(request, pk, value):
    thing = get_object_or_404(Thing, pk=pk)
    value = int(value)  # 1 or -1

    vote, created = Vote.objects.get_or_create(
        thing=thing,
        user=request.user,
        defaults={"value": value},
    )

    if not created:
        # already existed -> just update value
        vote.value = value
        vote.save()

    return redirect("shop:read", pk=thing.pk)

@login_required(login_url='shop:login') 
def view_cart(request):
        print("hi")
        cart_items=CartItem.objects.filter(user=request.user)
        print(list(cart_items))
        return render(request,'shop/cart.html',{'cart_items':cart_items})

@login_required(login_url='shop:login')
def addtocart(request, pk):
     if request.method=='POST':
        print("hello")
        thing=get_object_or_404(Thing,pk=pk)
        user=request.user
        existing_cart_item = CartItem.objects.filter(thing=thing, user=user).first()
        if existing_cart_item:
            existing_cart_item.quantity += 1
            existing_cart_item.total_price = existing_cart_item.quantity * thing.price
            existing_cart_item.save()
        else:
            cart_items=CartItem.objects.create(thing=thing,user=user,total_price=thing.price)
        return redirect('shop:shoppy')