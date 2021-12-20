from django import forms

class passform(forms.Form):
    code = forms.CharField(max_length=6,min_length=6)
    