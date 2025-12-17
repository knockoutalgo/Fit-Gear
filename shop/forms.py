from django import forms
from .models import Thing,Comment

class ThingForm(forms.ModelForm):
    class Meta:
        model=Thing
        fields=['name','price','desc','image_url']

class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields=['text']


        # in the field write only those thing which you want user to fill in the form of (input_form)
        
        