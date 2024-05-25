from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from chat import managers
import uuid



# User based Models.
# =========================================================

class BaseModel(models.Model):
    id = models.UUIDField(("id"),primary_key=True,editable=False,default=uuid.uuid4)
    updated_at = models.DateTimeField(("updated at"), auto_now=False, auto_now_add=True) 


class CustomUser(BaseModel,AbstractUser):
    email = models.EmailField(("email"), max_length=254,null=False,unique=True)
    username = models.CharField(("username"), max_length=50,null=True,blank=True)
    profile_pic = models.ImageField(("profile_pic"), upload_to="profile_pic", height_field=None, width_field=None, max_length=None,null=True,blank=True,default='userpic.jfif') 
    is_online = models.BooleanField(("status"),default=False)
    timestamp = models.DateTimeField(("time stamp"), auto_now=True, auto_now_add=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = managers.CustomUserManager()

    def save(self,*args,**kwargs):
        if not self.username:
            self.username = f'{self.first_name} {self.last_name}'
        if self.username:
            self.username = f'{self.first_name} {self.last_name}'
        return super().save(*args,**kwargs)



class Search(BaseModel):
    cmuser = models.ForeignKey(CustomUser, verbose_name=("search"), on_delete=models.CASCADE,related_name="search_set")
    data = models.CharField(("user search data"), max_length=150,null=True,blank=True)

class UserDetails(BaseModel):
    user = models.OneToOneField(CustomUser, verbose_name=("customuser"), on_delete=models.CASCADE,related_name='userdetails')

    college = models.CharField(("school/college"), max_length=150,null=True,blank=True)
    
    # for students
    stream = models.CharField(("class/stream"), max_length=150,null=True,blank=True)
    year = models.SmallIntegerField(("student year"),null=True,blank=True,default=0)

    # for teachers
    subject = models.CharField(("subjects"), max_length=500,null=True,blank=True,default=0)

    # choose category
    category = models.SmallIntegerField((" choose category"),null=True,blank=True)

    placelive = models.CharField(("placelive"), max_length=50,null=True,blank=True)

    insta_id = models.CharField(("instagram id"), max_length=50,null=True,blank=True)
    
    interest = models.TextField(("interest"), max_length=500,null=True,blank=True)
   
    @property
    def get_multiple_values_list(self):
        print(" call  get_multiple_values_list")
        return [value.strip() for value in self.interest.split(',')]

    @property
    def set_multiple_values_list(self, values_list):
        print("call set_multiple_values_list")
        self.interest = ','.join(values_list)

    # def __str__(self):
    #     return self.interest  # or any other field you want to display

# OTP based models.

class UserOTP(BaseModel):
    # id = models.UUIDField(("id"),primary_key=True,editable=False,default=uuid.uuid4)
    cmuser = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    time_st = models.DateTimeField(auto_now = True)
    otp = models.SmallIntegerField()
   

# Message Bassed Models.
class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    id = models.UUIDField(("id"),primary_key=True,editable=False,default=uuid.uuid4)
    first_person = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    room_id = models.CharField(("room id"), max_length=800,null=True,blank=True)

    objects = ThreadManager()
    class Meta:
        unique_together = ['first_person', 'second_person']
        ordering = ['-timestamp']


    def save(self, *args,**kwargs) -> None:
        if not self.room_id:
            self.room_id = f'room_id_{self.first_person.id}_{self.second_person.id}'

        if self.room_id:
            self.room_id = f'room_id_{self.first_person.id}_{self.second_person.id}'
        else:
            self.room_id = None
        return super().save(*args,**kwargs)

    # @property
    # def getroom(self):
    #     if self.room_id:
    #         self.room_id = f'room_id_{self.first_person.id}_{self.second_person.id}'
    #     else:
    #         self.room_id = None
    #     return self.room_id


class ChatMessage(models.Model):
    id = models.UUIDField(("id"),primary_key=True,editable=False,default=uuid.uuid4)
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_fname = models.CharField(("first_name"), max_length=50,null=True,blank=True)
    user_lname = models.CharField(("last_name"), max_length=50,null=True,blank=True)
    
  
    def save(self,*args,**kwargs):
        if not self.user_fname and not self.user_lname:
            self.user_fname = self.user.first_name
            self.user_lname = self.user.last_name
        
        if self.user_lname and self.user_lname:
            self.user_fname = self.user.first_name
            self.user_lname = self.user.last_name
           
        else:    
            pass
        return super().save(*args,**kwargs)




