from django.forms import ModelForm
from django.forms import modelformset_factory
from .models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Primeiro Nome',
                'type': 'text',
                'required': 'required'
            })
        self.fields['last_name'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Último Nome',
                'type': 'text',
                'required': 'required'
            })
        self.fields['email'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Email',
                'type': 'email',
                'required': 'required'
            })
