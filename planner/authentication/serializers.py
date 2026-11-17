from rest_framework import serializers

from . models import Profile

class ProfileSerailizer(serializers.ModelSerializer):

    class Meta:

        model = Profile

        fields = ['username','first_name','email','password','role','tech']

        extra_kwargs = {'password':{'write_only':True}}

        read_only_fields = ['email']