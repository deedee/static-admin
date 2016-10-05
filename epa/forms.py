
from django.forms import ModelForm, Form, ValidationError, CharField, EmailField, PasswordInput, \
    IntegerField, HiddenInput
from django.core.exceptions import FieldError
from django.contrib.auth.models import User
from epa.models import UploadData
from EPA_Admin.settings import EPA_ALLOWABLE_FILE_TYPES, EPA_IMAGE_VALID_HEADER, FILE_IMAGE
from epa import helper

import datetime
import imghdr


class UploadDataForm(ModelForm):
    class Meta:
        model = UploadData
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UploadDataForm, self).__init__(*args, **kwargs)

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']
        if uploaded_file:
            if not helper.file_checker(uploaded_file.name, EPA_ALLOWABLE_FILE_TYPES):
                raise ValidationError("only accept image and txt file")
            _file = uploaded_file.name.split('/')
            self.data['file_name'] = _file[len(_file) - 1]
            self.data['date'] = datetime.datetime.now()
            if helper.file_checker(self.data['file_name'], [FILE_IMAGE]):
                self.data['type'] = 0
            else:
                self.data['type'] = 1
            if self.request:
                self.data['user'] = self.request.user.id

        return uploaded_file

    def save(self):
        model = super(UploadDataForm, self).save()
        if model.type == 0:
            if imghdr.what(model.file.path) not in EPA_IMAGE_VALID_HEADER:
                model.delete()
                raise FieldError('Image file is not valid')
        super(UploadDataForm, self).save()


class LoginForm(Form):
    username = CharField()
    password = CharField(widget=PasswordInput())
    next = CharField(widget=HiddenInput, required=False, initial='/')


class RegisterForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    username = CharField(min_length=3)
    old_password = CharField(min_length=3, widget=PasswordInput(), required=False)
    password = CharField(min_length=3, widget=PasswordInput())
    password2 = CharField(min_length=3, widget=PasswordInput())
    email = EmailField()
    new_user = True

    def clean_email(self):
        """
        Validate email field
        """

        _email = self.cleaned_data['email']
        user = User.objects.filter(email=_email)
        if user.count() == 1:
            if self.new_user or (not self.new_user and user[0].id != int(self.cleaned_data['id'])):
                raise ValidationError('Email is already used')
        elif user.count() > 1:
             raise ValidationError('Email is already used')

        return _email

    def clean(self):
        """
        Other validation rules before we save it
        """
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password != password2:
            raise ValidationError("Passwords don't match")

        return self.cleaned_data
