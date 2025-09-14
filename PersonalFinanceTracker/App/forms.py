from django import forms
from App.models import Users
from datetime import datetime

categories = [
    ('I', 'Income'),
    ('E', 'Expense'),
]

class LoginForm(forms.ModelForm):
    
    class Meta:
        model = Users
        fields = ('username','password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}),
        }
        
class RegForm(forms.ModelForm):

    class Meta:
        model = Users
        fields = ('username','password','name','lastName')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'lastName': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'username': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}),
        }

class InsertForm(forms.Form):
    description = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control mb-2'}))
    category = forms.ChoiceField(choices=categories, widget=forms.Select(attrs={'class': 'form-control mb-2'}))
    amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control mb-2'}))
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control mb-2'}),
        initial=datetime.today)
    created = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control mb-2'}),
        initial=datetime.today)
    
class UpdateForm(forms.Form):
    Id = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control mb-2'}))
    description = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control mb-2'}))
    category = forms.ChoiceField(choices=categories, widget=forms.Select(attrs={'class': 'form-control mb-2'}))
    amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control mb-2'}))
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control mb-2'}),
        initial=datetime.today)

    
class DeleteForm(forms.Form):
    Id = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control mb-2'}))