from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import os
import pandas as pd
import openpyxl as xl
from django.http import HttpResponse
from airfilter import process
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, './servicios_adapta_app/index.html')
    else:
        return(redirect('login'))

def air_data_filter(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            point_name = request.POST.get('point_name')
            standard_1 = request.POST.get('standard_1')
            standard_2 = request.POST.get('standard_2')
            output_file_name = request.POST.get('output_file_name')
            input_file = request.FILES.get('input_file')
            # Process the input file and generate the output file
            # data = pd.read_excel(input_file)
            filtered_data = process(input_file, point_name, standard_1, standard_2)
            output_path = os.path.join(output_file_name + '.xlsx')
            filtered_data.to_excel(output_path, index=False)
            # Generate a response with the output file attached
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read())
                response['Content-Type'] = 'application/vnd.ms-excel'
                response['Content-Disposition'] = f'attachment; filename="{output_file_name}.xlsx"'
            os.remove(output_path)
            return response
        else:
            return render(request, './servicios_adapta_app/filter_air.html')
    else:
        return redirect('login')
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            error_message = "Usuario o contraseña incorrectos. Por favor, inténtelo de nuevo."
    else:
        error_message = ""

    context = {'error_message': error_message}
    return render(request, './servicios_adapta_app/login.html', context)

def noise_processing(request):
    if request.user.is_authenticated:
        return
    else:
        return redirect('login')