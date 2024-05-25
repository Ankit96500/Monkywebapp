from channels.consumer import AsyncConsumer,SyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
import json
from chat.models import Thread,ChatMessage
from django.db.models import Q
from chat.models import CustomUser
from channels.db import database_sync_to_async
from datetime import datetime



class ChatSyncConsumer(SyncConsumer):

    def websocket_connect(self, event):   
        currentuser = self.scope['user']

        # print('current channel layer',self.channel_layer)
        # print('current channel name',self.channel_name)
        self.otheruser = self.scope['url_route']['kwargs']['CHAT_USER_ID']
        # print('other-user',self.otheruser)
        
        # here we update the status of the logged-in-user to online:
        
        currentuser = self.get_user_object(currentuser.id)
        currentuser.is_online = True
        currentuser.save()

        #  get users from db
        sent_by_obj = self.get_user_object(currentuser.id)    
        send_to_obj = self.get_user_object(self.otheruser)
        

        # check weather thread object is present or not else we create
        thread_present = self.Check_Thread(sent_by_obj,send_to_obj)

        """
            here when, user1 first time send msg to user2 , the first time time user1 will stuck in empty group bcos,on the first time msg .the code will get to know that user1 is serious to talk to user2,but for real time talk user1 has to refresh a page bcos after refresh it will move user1 to and main chat_room in,which both has got their room _id.
            and but user2 will see all msg in main room_id(the problem with the user 1).
            problem solved now they both chat on a real time without refresh (26,march,2024)
        """
        
        # it create a room for both users and in this room we circulate data
        if not thread_present:
            # we create room
            thread_obj = self.Create_Thread(sent_by_obj,send_to_obj)
            
            chat_room = self.get_room(sent_by_obj,send_to_obj)
            # we delete thread_obj bcos, if user deny to talk a chat user, so.for that we delete the thread..and it will recreate by the when user send msg to the other user. with sam room_id.
            thread_obj.delete()
        else:
            chat_room = self.get_room(sent_by_obj,send_to_obj)
    
        self.chat_room = chat_room
        async_to_sync(self.channel_layer.group_add)(
        chat_room ,self.channel_name
        )     
    
        self.send({
        'type':"websocket.accept",
        })

    
    def websocket_disconnect(self,event):
        
        # discard the group:
        self.channel_layer.group_discard(self.channel_name,self.chat_room)

        # print('disconnect',event,self.scope['user'],dd)
        # here we update the status of the logged-in-user to ofline:
        currentuser = self.scope['user']
        currentuser = self.get_user_object(currentuser.id)
        currentuser.is_online = False
        currentuser.save()
        raise StopConsumer()



    def websocket_receive(self, event):
        python_obj = json.loads(event['text'])
        # print('python obj',python_obj)
        
        # extract actual message
        message = python_obj.get('msg')
        sent_by_id = python_obj.get('sent_by_id')
        send_to_id = python_obj.get('send_to_id')

        if not message:
            # print('Error:: empty message')
            return False


        #  get users from db
        sent_by_obj = self.get_user_object(sent_by_id)    
        send_to_obj = self.get_user_object(send_to_id)
        

        # check weather thread object is present or not else we create
        thread_present = self.Check_Thread(sent_by_obj,send_to_obj)

        # print('thread pressent receve',thread_present)
        if not thread_present:
           
            thread_obj = self.Create_Thread(sent_by_obj,send_to_obj) 
        else:
            # we dont't need run ORM again bcos thread present get a single query set that we convert to object
            thread_obj = thread_present.first()


        if not sent_by_obj:
            return False
            # print('Error:: sent by user is incorrect')
        if not send_to_obj:
            return False
            # print('Error:: send to user is incorrect')
        if not thread_obj:
            return False
            # print('Error:: Thread id is incorrect')



        #  create chat messages
        self.Create_Message(sent_by_obj,thread_obj,message)

        self_user = self.scope['user']
        
        response = {
            'message' : message,
            'sender' : sent_by_obj.first_name,
            'receiver' : send_to_obj.first_name,
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chat_room,
            {
                'type':'chat_message',
                'text': json.dumps(response),
            }
        )


    def chat_message(self,event):
     
        self.send({
            "type": "websocket.send",
            "text": event['text'],
        })  

    def Create_Thread(self,sender,receiver):
        create = Thread.objects.create(first_person=sender,second_person=receiver)
        return create

    def get_user_object(self,user_id):
        qs = CustomUser.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    def Check_Thread(self,sent_by_id,send_to_id):
        # it return a query set
        qs =  Thread.objects.filter(Q(first_person=sent_by_id) | Q(second_person=sent_by_id)).filter(Q(first_person=send_to_id) | Q (second_person=send_to_id))
        if qs.exists():
            obj = qs
        else:
            obj = []
        return obj

    def Create_Message(self, user,thread, msg):
       
        ChatMessage.objects.create(user=user,thread=thread,message=msg)

    def get_room(self,sent_by_id,send_to_id):
        qs =  Thread.objects.filter(Q(first_person=sent_by_id) | Q(second_person=sent_by_id)).filter(Q(first_person=send_to_id) | Q (second_person=send_to_id))
        if qs.exists():
            for q in qs:
                room = q.room_id 
        return room




'''

class AChatSyncConsumer(AsyncConsumer):
    

    async def websocket_connect(self, event):   
        currentuser = self.scope['user']
        # print('logged-in-user',currentuser.id)

        self.otheruser = self.scope['url_route']['kwargs']['CHAT_USER_ID']
        # print('other-user',self.otheruser)
        
        # here we update the status of the logged-in-user to online:
        
        currentuser = await self.get_user_object(currentuser.id)
        currentuser.is_online = True
        currentuser.save()

        #  get users from db
        sent_by_obj = await self.get_user_object(currentuser.id)    
        send_to_obj = await self.get_user_object(self.otheruser)
        

        # check weather thread object is present or not else we create
        thread_present = await self.Check_Thread(sent_by_obj,send_to_obj)

        # print('thread pressent connect',thread_present)
        
        # it create a room for both users and in this room we circulate data
        if not thread_present:
            
            chat_room = f'userchat_room_{currentuser.id}'
            self.chat_room = chat_room
            await self.channel_layer.group_add(
            chat_room ,self.channel_name
            )     
        
            await self.send({
            'type':"websocket.accept",
            })
            
        else:
            chat_room = await self.get_room(sent_by_obj,send_to_obj)
            # print('type of chat room in connect',type(chat_room))
            # print('chat room in connect',chat_room)
            self.chat_room = chat_room
            await self.channel_layer.group_add(
            chat_room ,self.channel_name
            )     
        
            await self.send({
            'type':"websocket.accept",
            })


    async def websocket_disconnect(self,event):
        print('disconnect',event,self.scope['user'])
        
        # discard the group:
        await self.channel_layer.group_discard(self.channel_name,self.chat_room)


        # here we update the status of the logged-in-user to ofline:
        currentuser = self.scope['user']
        print('current usr in dis connect function',currentuser)
        currentuser = self.get_user_object(currentuser.id)
        currentuser.is_online = False
        currentuser.save()
        raise StopConsumer()


    async def websocket_receive(self, event):
        python_obj = json.loads(event['text'])
        # print('python obj',python_obj)
        
        # extract actual message
        message = python_obj.get('msg')
        sent_by_id = python_obj.get('sent_by_id')
        send_to_id = python_obj.get('send_to_id')

        if not message:
            print('Error:: empty message')
            return False


        #  get users from db
        sent_by_obj = await self.get_user_object(sent_by_id)    
        send_to_obj = await self.get_user_object(send_to_id)
        

        # check weather thread object is present or not else we create
        thread_present = await self.Check_Thread(sent_by_obj,send_to_obj)

        # print('thread pressent receve',thread_present)
        if not thread_present:
            
            thread_obj = await self.Create_Thread(sent_by_obj,send_to_obj) 
        else:
            # we dont't need run ORM again bcos thread present get a single query set that we convert to object
            thread_obj = thread_present.first()


        if not sent_by_obj:
            print('Error:: sent by user is incorrect')
        if not send_to_obj:
            print('Error:: send to user is incorrect')
        if not thread_obj:
            print('Error:: Thread id is incorrect')



        #  create chat messages
        await self.Create_Message(sent_by_obj,thread_obj,message)

        self_user = self.scope['user']
        
        response = {
            'message' : message,
            'sender' : sent_by_obj.first_name,
            'receiver' : send_to_obj.first_name,
        }

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type':'chat_message',
                'text': json.dumps(response),
            }
        )


    async def chat_message(self,event):
        
        await self.send({
            "type": "websocket.send",
            "text": event['text'],
        })  

    @database_sync_to_async
    def Create_Thread(self,sender,receiver):
        create = Thread.objects.create(first_person=sender,second_person=receiver)
        return create

    @database_sync_to_async
    def get_user_object(self,user_id):
        qs = CustomUser.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def Check_Thread(self,sent_by_id,send_to_id):
        # it return a query set
        qs =  Thread.objects.filter(Q(first_person=sent_by_id) | Q(second_person=sent_by_id)).filter(Q(first_person=send_to_id) | Q (second_person=send_to_id))
        if qs.exists():
            obj = qs
        else:
            obj = []
        return obj

    @database_sync_to_async
    def Create_Message(self, user,thread, msg):
        ChatMessage.objects.create(user=user,thread=thread,message=msg)

    @database_sync_to_async
    def get_room(self,sent_by_id,send_to_id):
        qs =  Thread.objects.filter(Q(first_person=sent_by_id) | Q(second_person=sent_by_id)).filter(Q(first_person=send_to_id) | Q (second_person=send_to_id))
        if qs.exists():
            for q in qs:
                room = q.room_id 
        return room

'''
