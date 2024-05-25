from chat import views
from django.urls import path

app_name = "chat"

urlpatterns = [
    # path('chat/<slug:other_user_id>',views.chat, name="chatuser"),
    path('chatuser/',views.chat, name="chatuser"),
    path('delete-user/',views.DeleteUser,name="DeleteUser"),

    path('message/',views.MessagePage,name="MessagePage"),
    path('message/<slug:otheruser_id>/',views.MessagePage,name="MessagePage"),


    path('signup/',views.Sign_Up,name="Sign_Up"),
    path('resend-otp/',views.resend_otp,name = "resend_otp"),
    
    path('home/',views.Home,name="Home"),
    path('home/<slug:chat_user_id>/',views.Home,name="Home"),

    path('logout/',views.logout_user,name="logout_user"),
    
    path('my-edit-profile/',views.EditUserProfile,name="EditUserProfile"),
    path('my-personal-info/',views.EditPersonalInfo,name= "EditPersonalInfo"),

    path('about/',views.AboutPage,name="AboutPage"),
    path('help/',views.HelpPage,name="HelpPage"),

    path('changepassword/',views.ChangePassword,name="ChangePassword"),

 

]
