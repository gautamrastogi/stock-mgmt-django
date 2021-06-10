from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
from django.contrib import messages
import csv
# from reportlab.pdfgen import canvas  
# import io

# from django.template.loader import render_to_string
# from weasyprint import HTML
# import tempfile
# from django.db.models import Sum
from .models import Stock, StockHistory
from .forms import StockCreateForm, StockSearchForm, StockUpdateForm, IssueForm, ReceiveForm, ReorderLevelForm, StockHistorySearchForm, CreateUserForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
# Create your views here.
import os


def registerPage(request):
	form = CreateUserForm()

	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			user = form.cleaned_data.get('username')
			messages.success(request, 'Account was created for ' + user)
			return redirect('login')

	context = {
	"form": form
	}
	return render(request, "register.html",context)

def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.info(request, 'Username or Passwrd is incorrect')
			return redirect('login')
	context = {}
	return render(request, "login.html",context)


def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login/')
def home(request):
	title = 'Welcome: This is the Home Page'
	context = {
	"title": title,
	}
	#return redirect('/list_items')
	return render(request, "home.html",context)


@login_required
def list_items(request):
	form = StockSearchForm(request.POST or None)
	title = 'List of Items'
	queryset = Stock.objects.all()
	paginator = Paginator(queryset, 6)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context = {
		"title": title,
		"queryset": queryset,
		"form": form,
		"queryset":page_obj
	}
	if request.method == 'POST':
		queryset = Stock.objects.filter(#category__icontains=form['category'].value(),
									item_name__icontains=form['item_name'].value()
									)

		if form['export_to_CSV'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
			writer = csv.writer(response)
			writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
			instance = queryset
			for stock in instance:
				writer.writerow([stock.category, stock.item_name, stock.quantity])
			return response

		context = {
			"form":form,
			"title": title,
			"queryset": queryset,
			"queryset":page_obj
		}
	return render(request, "list_items.html", context)


@login_required
def add_items(request):
	form = StockCreateForm(request.POST or None)
	if form.is_valid():
		form.save()
		messages.success(request, 'Successfully Saved')
		return redirect('/list_items')
	context = {
		"form": form,
		"title": "Add Items"
	}
	return render(request, "add_items.html", context)


def update_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = StockUpdateForm(instance =queryset)
	if request.method == 'POST':
		form = StockUpdateForm(request.POST, instance= queryset)
		if form.is_valid():
			form.save()
			messages.success(request, 'Successfully Saved')
			return redirect('/list_items')
	context = {
		'form': form
	}
	return render(request, 'add_items.html', context)


def delete_items(request,pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"queryset": queryset,
	}
	if request.method == 'POST':
		queryset.delete()
		messages.success(request, 'Successfully Deleted')
		return redirect('/list_items')
	return render(request, 'delete_items.html',context)



def stock_detail(request,pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"queryset": queryset,
	}
	return render(request, 'stock_detail.html',context)




def issue_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = IssueForm(request.POST or None, instance = queryset)
	if form.is_valid():
		instance = form.save()
		instance.receive_quantity = 0
		instance.quantity -= instance.issue_quantity
		instance.issue_by = str(request.user)
		messages.success(request, "Issued Successfully " + str(instance.quantity) + " " + str(instance.item_name) + "- now left in Store")
		instance.save()
		return redirect('/stock_detail/' + str(instance.id)) 
	context = {
		"title": 'Issue ' + str(queryset.item_name),
		"queryset": queryset,
		"form": form,
		"username": 'Issue by: '+ str(request.user),
	}
	return render(request, 'add_items.html',context)




def receive_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReceiveForm(request.POST or None, instance = queryset)
	if form.is_valid():
		instance = form.save()
		instance.issue_quantity = 0
		instance.quantity += instance.receive_quantity
		instance.receive_by = str(request.user)
		messages.success(request, "Received Successfully " + str(instance.quantity) + " " + str(instance.item_name) + "- now left in Store")
		instance.save()
		return redirect('/stock_detail/' + str(instance.id)) 
	context = {
		"title": 'Receive ' + str(queryset.item_name),
		"queryset": queryset,
		"form": form,
		"username": 'Receive By: '+ str(request.user),
	}
	return render(request, 'add_items.html',context)


def reorder_level(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReorderLevelForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Reorder level for " + str(instance.item_name) + " is updated to " + str(instance.reorder_level))

		return redirect("/list_items")
	context = {
			"instance": queryset,
			"form": form,
		}
	return render(request, "add_items.html", context)




@login_required
def list_history(request):
	header = 'LIST OF ITEMS'
	form = StockHistorySearchForm(request.POST or None)
	queryset = StockHistory.objects.all()
	paginator = Paginator(queryset, 6)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
        
	context = {
		"header": header,
		"queryset": queryset,
		"form": form,
		"queryset":page_obj
	}
	if request.method == 'POST':
		category = form['category'].value()
		queryset = StockHistory.objects.filter(item_name__icontains=form['item_name'].value(), last_updated__range=[form['start_date'].value(), form['end_date'].value()])
		cont = {}
		paginator = Paginator(queryset, 6)
		page_number = request.GET.get('page')
		page_obj = paginator.get_page(page_number)

		if (category != ''):
			queryset = queryset.filter(category_id=category)

		if form['export_to_CSV'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
			writer = csv.writer(response)
			writer.writerow(
				['CATEGORY', 
				'ITEM NAME',
				'QUANTITY', 
				'ISSUE QUANTITY', 
				'RECEIVE QUANTITY', 
				'RECEIVE BY', 
				'ISSUE BY', 
				'LAST UPDATED'])
			instance = queryset
			for stock in instance:
				writer.writerow(
				[stock.category, 
				stock.item_name, 
				stock.quantity, 
				stock.issue_quantity, 
				stock.receive_quantity, 
				stock.receive_by, 
				stock.issue_by, 
				stock.last_updated])
			return response


		# if form['export_to_PDF'].value() == True:
		# 	response = HttpResponse(content_type='application/pdf')
		# 	response['Content-Disposition'] = 'attachment; filename="Stock History.pdf"'
		# 	response['Content-Transfer-Encoding'] = 'binary'

		# 	writer = csv.writer(response)
		# 	writer.writerow(
		# 		['CATEGORY', 
		# 		'ITEM NAME',
		# 		'QUANTITY', 
		# 		'ISSUE QUANTITY', 
		# 		'RECEIVE QUANTITY', 
		# 		'RECEIVE BY', 
		# 		'ISSUE BY', 
		# 		'LAST UPDATED'])
		# 	instance = queryset
		# 	for stock in instance:
		# 		writer.writerow(
		# 		[stock.category, 
		# 		stock.item_name, 
		# 		stock.quantity, 
		# 		stock.issue_quantity, 
		# 		stock.receive_quantity, 
		# 		stock.receive_by, 
		# 		stock.issue_by, 
		# 		stock.last_updated])
		# 	return response

		context = {
		"form": form,
		"header": header,
		"queryset": queryset,
		"queryset":page_obj
	}
	return render(request, "list_history.html",context)




# def getpdf(request):  
#     response = HttpResponse(content_type='application/pdf')  
#     response['Content-Disposition'] = 'attachment; filename="Stock History.pdf"'  
#     p = canvas.Canvas(response)  
#     p.setFont("Times-Roman", 55)  
#     p.drawString(100,700, "Hello, Javatpoint.")  
#     p.showPage()  
#     p.save()  
#     return response  

