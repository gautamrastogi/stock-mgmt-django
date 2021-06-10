from django import forms
from .models import Stock, StockHistory
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from django import forms
from django.contrib.auth.models import User

class CreateUserForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['username', 'email', 'password1', 'password2']

class StockCreateForm(forms.ModelForm):
  class Meta:
    model = Stock
    fields = ['category', 'item_name', 'quantity']

  def clean_category(self):
    category = self.cleaned_data.get('category')
    if not category:
      raise forms.ValidationError('This field is required')
    # for instance in Stock.objects.all():
    #   if instance.category == category:
    #     raise forms.ValidationError(str(category) + ' is already created')
    return category


  def clean_item_name(self):
    item_name = self.cleaned_data.get('item_name')
    if not item_name:
      raise forms.ValidationError('This field is required')
    return item_name



class StockSearchForm(forms.ModelForm):
  export_to_CSV = forms.BooleanField(required=False)
  class Meta:
      model = Stock
      fields = ['category', 'item_name']





class StockUpdateForm(forms.ModelForm):
  class Meta:
    model = Stock
    fields = ['category', 'item_name', 'quantity']



class IssueForm(forms.ModelForm):
  class Meta:
    model = Stock
    fields = ['issue_quantity', 'issue_to']



class ReceiveForm(forms.ModelForm):
  class Meta:
    model = Stock
    fields = ['receive_quantity', 'receive_by']


class ReorderLevelForm(forms.ModelForm):
  class Meta:
    model = Stock
    fields = ['reorder_level']


class DateInput(forms.DateInput):
    input_type = 'date'



class StockHistorySearchForm(forms.ModelForm):
  export_to_CSV = forms.BooleanField(required=False)
  export_to_PDF = forms.BooleanField(required=False)
  start_date = forms.DateField(required=False,input_formats=['%Y-%m-%d'])
  end_date = forms.DateField(required=False,input_formats=['%Y-%m-%d'])
  class Meta:
    model = StockHistory
    fields = ['category', 'item_name', 'start_date', 'end_date', 'export_to_CSV', 'export_to_PDF']