from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from chat.models import Thread,CustomUser,ChatMessage,UserDetails,UserOTP,Search
from chat.forms import UserLoginForm,signupform,PasswordFormChange
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm,SetPasswordForm
from django.http import JsonResponse,HttpResponse
from django.db.models import Q
import json
from django.http import JsonResponse
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import time
from django.urls import reverse
from django.core.mail import send_mail
import os
# Create your views here.
from datetime import datetime
from django.utils import timezone

"""
project work properly. 
"""

@login_required
def chat(request):
    other_user_id = request.GET.get('otheruser_id')
    # print('other user id::::>',other_user_id)
    other_user_obj  = CustomUser.objects.get(id = other_user_id)

    # get the thread object:
    thread_query = Thread.objects.filter(Q(first_person=request.user)|Q(second_person=request.user)).filter(Q(first_person=other_user_obj)| Q(second_person=other_user_obj))

    thread_obj = thread_query.first()
    if thread_obj:
        
        # get chat messages of following thread:
        data = list(thread_obj.chatmessage_thread.values().order_by('timestamp'))
     
        formatted_data = [{'timestamp': timezone.localtime(item['timestamp']).strftime("%d %b, %Y %I:%M %p"),'user_fname':item['user_fname'],'message':item['message']} for item in data]
        # print('formmated data  strftime("%d/%m/%Y - %H:%M")',formatted_data )    

        return JsonResponse({"chat_messages": formatted_data,"thread_obj":str(thread_obj)})
    

    # print('chat messages',chat_messages)
   
    return JsonResponse({"chat_messages":'',"thread_obj":str(thread_obj)})

@login_required
def MessagePage(request,otheruser_id=None):
    # threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    if otheruser_id :
        otheruser = CustomUser.objects.get(id=otheruser_id)
        otheusername = f'{otheruser.first_name } {otheruser.last_name}'
        # print('other user name detect',otheusername)
      
    else:
        otheusername =''
        # print('no name detect')
    

    # here [thread] check wether request-user has any thread in database or not if not it send empty list on template. 
    thread = Thread.objects.filter(Q(first_person=request.user)|Q(second_person=request.user))
    user_lst = []
    for t in thread:
        if t.first_person == request.user:
            user_lst.append(t.second_person)
        elif t.second_person == request.user:
            user_lst.append(t.first_person)
  
    context = {
        'users':user_lst,
        'otheruser_id':otheruser_id,
        'otheuserfullname':otheusername,
    }
   
    return render(request, 'users.html', context)

@login_required
def DeleteUser(request):
    chatuser = request.GET.get('chat_user_id')
    
    # get chat user object.
    chatuser_obj = CustomUser.objects.get(id=chatuser)

    # get thread object.
    thread_query = Thread.objects.filter(Q(first_person=request.user)|Q(second_person=request.user)).filter(Q(first_person=chatuser_obj)| Q(second_person=chatuser_obj))
    # print(' before thread objects filter query',thread_query)
    
    thread_obj = thread_query.first()
    thread_obj.delete()

    return JsonResponse({"status":1})

# Normal VIews
@login_required
def Home(request,chat_user_id=None):
    # when user hit the chat user (message page) to get it details specificly...
    if chat_user_id:
        # print('chat user id comming.',chat_user_id)
        chatuser = CustomUser.objects.filter(id=chat_user_id)

        context = {
            "userquery":chatuser,
        }
        return render(request,"home.html",context=context)

    # here we handel search....AboutPage
    userserach = request.GET.get('usersearch')

    # save user search data in db..
    cmuser = CustomUser.objects.get(email=request.user)
    Search.objects.create(cmuser=cmuser,data=userserach)
    # print('usearch',userserach)
    if userserach:
       
        search_detail = CustomUser.objects.filter(Q(userdetails__college__istartswith=userserach)
                                            |Q(userdetails__college__icontains=userserach)
                                            |Q(userdetails__stream__istartswith=userserach)
                                            |Q(userdetails__stream__icontains=userserach))
        # print('serach data',search_detail)
        
        search_user = CustomUser.objects.filter(first_name__istartswith=userserach).select_related()
        # print('serach user',search_user)
        context={}
        if search_detail:
            context['userquery'] = search_detail

        if search_user:
            context['userquery'] = search_user


        return render(request,"home.html",context=context)

    # when user hit home only---------------
    userquery = CustomUser.objects.prefetch_related('userdetails').order_by("-timestamp")
    user_count = CustomUser.objects.all().count()
   
    # print('date time',time.localtime())

    context = {
        "userquery":userquery,
        "user_count":user_count
    }

    return render(request,"home.html",context=context)

@login_required
def AboutPage(request):
    return render(request,"about.html")


@login_required
def HelpPage(request):
    return render(request,"help.html")


@login_required
def EditUserProfile(request):
    user_obj = CustomUser.objects.get(email=request.user)
   
    if request.method =='POST':
        # if image not updated we took recent image
        image_file=user_obj.profile_pic 

        if  request.FILES.get('image'):
            image_file = request.FILES['image']
            
            # user_obj.profile_pic=image_file
            # user_obj.save()

            # # print('image file',image_file)
            # # Specify the directory where you want to save the uploaded image
            # upload_dir = os.path.join(settings.MEDIA_ROOT, 'profile_pic')
            # if not os.path.exists(upload_dir):
            #     os.makedirs(upload_dir)
            # # Save the uploaded image to the specified directory
            # image_path = os.path.join(upload_dir, image_file.name)
            # with open(image_path, 'wb') as f:
            #     for chunk in image_file.chunks():
            #         f.write(chunk)
            # # Return the URL of the saved image
            # image_url = os.path.join(settings.MEDIA_URL, 'profile_pic', image_file.name)
            # return JsonResponse({'image_url': image_url,'status':1})
       

       

        # here we save data..  
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')

        user_obj.first_name = first_name
        user_obj.last_name = last_name
        user_obj.profile_pic = image_file
        user_obj.save()
      
        return JsonResponse({'status':1})
    else:                                                                                                                                                   
        userformquery = CustomUser.objects.filter(email= request.user)
        userdetailform = UserDetails.objects.filter(user=user_obj)

        context = {
            'userformquery':userformquery,
            'userdetailform':userdetailform,
        }
        # print('EditUserProfile')
        return render(request,"editUserProfile.html",context=context)

@login_required
def EditPersonalInfo(request):
    user_obj = CustomUser.objects.get(email=request.user)
    userdetail_query = UserDetails.objects.filter(user=user_obj)
    if request.method == "POST":
        college = request.POST.get('college')
        stream = request.POST.get('stream')
        place = request.POST.get('place')
        insta = request.POST.get('insta')
        interest=request.POST.get('interest')
        year = request.POST.get('year')
        subject = request.POST.get('subject')
        user_id = request.POST.get('user_id')
        category = request.POST.get('category')
     
        # create data
        if not userdetail_query:
          
            user_obj = UserDetails.objects.create(user=user_obj,college=college,stream=stream,placelive=place,insta_id=insta,interest=interest,subject=subject,year=year,category=category)
            return JsonResponse({'status':0})

        # # update data
        else:
          
            userd_obj = UserDetails.objects.get(id=user_id)
            userd_obj.college=college
            userd_obj.stream=stream
            userd_obj.placelive=place
            userd_obj.insta_id=insta
            userd_obj.interest=interest
            userd_obj.subject=subject
            userd_obj.year=year
            userd_obj.category=category
            user_obj.updated_at = datetime.now()
            userd_obj.save()
            # print('userd objects',userd_obj)
            return JsonResponse({'status':1})



# USER AUTHENTICATION VIEWS..

@login_required
def ChangePassword(request):
    if request.method == 'POST':
        fm=PasswordFormChange(user=request.user,data=request.POST)
        if fm.is_valid():
            fm.save()
            # update_session_auth_hash(request,fm.user)
            # return redirect("chat:Home")
    else:
        fm=PasswordFormChange(user=request.user)
    return render(request,'changepassword.html',{'form':fm})



# SIGNUP FUNCTION

def Sign_Up(request):
    if request.method == 'POST':
        get_otp = request.POST.get('otp') #213243 #None

        # her we cheack wrong output of OTP ex: adsghab121 
        if get_otp:
            get_user = request.POST.get('user')
            user = CustomUser.objects.get(email = get_user)
            for char in get_otp:
                symbols = "!@#$%^&*()-_=+[{]}|;:<.>/?`~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                if char in symbols:
                    messages.warning(request, f'Symbols And Alphabets Are Not Allowed !!')
                    return render(request, 'signup.html',{'otp': True,'user': user})

            if int(get_otp) == UserOTP.objects.filter(cmuser = user).last().otp:
                user.is_active = True
                user.save()
                # print('if block')
                messages.success(request, f'{user.first_name}, Your Account Has Created !! ')
                return redirect('LogInPage')
            else:
                messages.warning(request, f'You Entered a Wrong OTP')
                return render(request, 'signup.html', {'otp': True, 'user': user})


        fm=signupform(request.POST)
    
        if fm.is_valid():
            fn = fm.cleaned_data['first_name']
            ln = fm.cleaned_data['last_name']
            em = fm.cleaned_data['email']
            fm.save()
            
            user = CustomUser.objects.get(email=em)
            user.is_active = False
            user.save()

            # here we write the logic for OTP verification:
            user_otp = random.randint(1000, 9999)
            UserOTP.objects.create(cmuser = user, otp = user_otp)
            mess = f"Dear {user.first_name},\n\nYou recently requested a password reset for your account. To proceed, please use the following one-time password (OTP). \n\n\nOTP: {user_otp} \n\nIf you did not request this password reset, please ignore this message. For security reasons, please do not share this OTP with anyone.\n\n\nThank you,"
        
            # print('mess',mess)
          
            subject = 'VERIFY ! Monky Signup'
            # msg = f'we send this message for you {user.first_name} ?'
            try:
                send_mail(
                    subject,
                    mess,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                messages.warning(request, f'Please Check Your Mail Box.')
                return render(request, 'signup.html', {'otp': True, 'user': user})
            except:
                # if connection disconnected it will delete the user..
                user.delete()

                return HttpResponse('<h1>Internet Connection has Dis-connected, Please refresh the page and try again.</h1>')           
            # return redirect('LogInPage')

    else:
        fm=signupform()    
    return render(request,'signup.html',{'form':fm})


# RESEND otp:   
def resend_otp(request):
    if request.method == "GET":
        get_user = request.GET['user']
        if CustomUser.objects.filter(email = get_user).exists() and not CustomUser.objects.get(email = get_user).is_active:
            user = CustomUser.objects.get(email=get_user)
            user_otp = random.randint(1000, 9999)
            UserOTP.objects.create(cmuser = user, otp = user_otp)
            mess = f"Dear {user.first_name},\nYou recently requested a password reset for your account. To proceed, please use the following one-time password (OTP). \nOTP : {user_otp} \nIf you did not request this password reset, please ignore this message. For security reasons, please do not share this OTP with anyone.\n\nThank you,"
           
            subject = 'VERIFY ! Monky Signup'

            send_mail(
                subject,
                mess,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            # print('user otp',user_otp)
            
            return JsonResponse({"status":1})

        return JsonResponse({"status":0})


def LogInPage(request):
    if request.user.is_authenticated:
        return redirect('chat:Home')
        
    if request.method == "POST":
     
        form = UserLoginForm(request=request,data=request.POST)
        if form.is_valid():
            email= form.cleaned_data['username']
            password= form.cleaned_data['password']

            user = authenticate(request,email = email, password = password)
           
            if user is not None:
                login(request,user)
                return redirect('chat:Home')

    else:
        form = UserLoginForm()
       
    context = {
        'form':form
    }

    return render(request,'user/login.html',context=context)



# logout function:

def logout_user(request):
    logout(request)
    return redirect('LogInPage')


