from base64 import urlsafe_b64decode
from email.message import EmailMessage
from lib2to3.pgen2.tokenize import generate_tokens
import logging
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from authentication import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils .encoding import force_bytes, force_text
from .token import generate_token
# import authentication

def home(request):
    return render(request,'index.html')


def signup(request):

    if request.method=="POST":
        username =request.POST['username']
        fname= request.POST['fname']
        lname= request.POST['lname']
        email= request.POST['email']
        pass1 = request.POST['pass1']
        pass2= request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request,"username already exists! Please try some other username")
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request,"email is used! please try some other mail")
            return redirect('home')

        if len(username)>10:
            messages.error(request,"username can not be more then 10")

        if pass1 != pass2:
            messages.error(request,"password did not match")
            

        if not username.isalnum():
            messages.error(request,"Username is not alpha numeric!")
            return redirect('home')

        myuser =User.objects.create_user(username,email,pass1)
        myuser.first_name= fname
        myuser.last_name= lname
        myuser.is_active= False

        myuser.save()
        messages.success(request,"you account created succefully. We have sent a confirmation email Please confirm email in order to activate your account")

        # Welcome email
        subject = "welcome buddy"
        message= "Hello" + myuser.first_name + "!! \n" + "Welocome to banjare!! \n thank you for visiting our website \n we have sent you a confirmation mail pleasw confirm you email address in order to activate your account. \n\n Thanking you"
        from_email=settings.EMAIL_HOST_USER
        to_list=[myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)


        # Email address confirmation Email

        current_site =get_current_site(request)
        email_subject='Confirm your Email @banjare-Login!!'
        message2=render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)
        })

        email= EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser,email]
        )

        email.fail_silently= True
        email.send()




        return redirect('signin')
    return render(request, "signup.html")


def signin(request):
    if request.method=='POST':
        username= request.POST['username']
        # email= request.POST['email']
        pass1= request.POST['pass1']

        user = authenticate(username=username,password=pass1)
        print(bool(user),"helo")

        if user is not None:
            login(request,user)
            fname= user.first_name
            return render(request,'index.html',{'fname':fname})
        else:
            messages.error(request,"Bad credentials")
            return redirect('home')

    return render(request, "signin.html")


def signout(request):
    logout(request)
    messages.success(request,"logged out succcesfully")
    return redirect('home')



def activate(request, uid64, token):
    try:
        uid=force_text(urlsafe_base64_decode(uid64))
        myuser= User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError, User.DoesNotExist):
        myuser=None
    

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_activate=True
        myuser.save()
        login(request,myuser)
        return redirect('home')

    else:
        return render(request, 'activation_failed.html')




