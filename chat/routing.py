from chat import consumers 

from django.urls import path

websocket_urlpattern = [
    path('ws/chat/<str:CHAT_USER_ID>/',consumers.ChatSyncConsumer.as_asgi()),
    # path('ws/chat/<str:CHAT_USER_ID>/',consumers.AChatSyncConsumer.as_asgi()),
  
]


'''
 def websocket_connect(self, event):   
        user = self.scope['user']

        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        async_to_sync(self.channel_layer.group_add)(
        chat_room ,self.channel_name
       )     
      
        self.send({
           'type':"websocket.accept",
       })
    
    def websocket_disconnect(self,event):
        print('disconnect',event)
        raise StopConsumer()


    def websocket_receive(self, event):
        python_obj = json.loads(event['text'])
        print('python obj',python_obj)
        
        # extract actual message
        message = python_obj.get('msg')
        sent_by_id = python_obj.get('sent_by_id')
        send_to_id = python_obj.get('send_to_id')

        if not message:
            print('Error:: empty message')
            return False


        #  get users from db
        sent_by_obj = self.get_user_object(sent_by_id)    
        send_to_obj = self.get_user_object(send_to_id)
        

        # check weather thread object is present or not else we create
        thread_present = self.Check_Thread(sent_by_obj,send_to_obj)

        print('thread pressent',thread_present)
        if not thread_present:
           
            thread_obj = self.Create_Thread(sent_by_obj,send_to_obj) 
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
        self.Create_Message(sent_by_obj,thread_obj,message)

        other_user_chat_room = f'user_chatroom_{send_to_id}'
        self_user = self.scope['user']
        
        response = {
            'message' : message
        }

        {
            'sent_by':"",
            'thread_id':""
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chat_room,
            {
                'type':'chat_message',
                'text': json.dumps(response),
            }
        )

        async_to_sync(self.channel_layer.group_send)(
            other_user_chat_room,
            {
                'type':'chat_message',
                'text':json.dumps(response),
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
        qs = User.objects.filter(id=user_id)
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





'''