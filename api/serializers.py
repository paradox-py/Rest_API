from datetime import datetime,timedelta
import random
from django.conf import settings
from rest_framework import serializers
from .models import User 
from .custom_errors import PlainValidationError
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator






#User registartion serializer:
class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField( write_only = True)
    class Meta:
        model = User
        fields = ('email','username','first_name','last_name','score','password','confirm_password')
        extra_kwargs = {
            'password':{'write_only':True},
            'email' : {
                "validators" : 
                    [UniqueValidator(
                        queryset=User.objects.all(),
                        message="This email already exist!"
                    )]}}
        
    #object level validations:
    def validate(self,data):
        print("here")
        password = data.get('password')
        print(password)
        confirm_password = data.get('confirm_password')
        print(confirm_password)
        if password != confirm_password:
            raise PlainValidationError({'message':' Password do not match '})
        return data
    def create(self,validate_data):
      return User.objects.create_user(**validate_data)




#user login serializer
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255)
    class Meta:
        model = User
        fields = ['email','password']