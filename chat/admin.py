from django.contrib import admin
from chat.models import ChatMessage,Thread,CustomUser,UserDetails,UserOTP,Search

# Register your models here.


admin.site.register(ChatMessage)

class ChatMessage(admin.TabularInline):
    model = ChatMessage
    list_display=['timestamp']


class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    class Meta:
        model = Thread
   

admin.site.register(Thread, ThreadAdmin)


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display=['id','cmuser','data']



@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ['id','cmuser','otp','time_st']


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id','first_name','last_name','email','is_online',"username"]    



@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ['id','college','stream','placelive','insta_id','interest','user','year','subject','category']
