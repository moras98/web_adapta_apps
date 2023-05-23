from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import os
import pandas as pd
import openpyxl as xl
from django.http import HttpResponse
from airfilter import process
from django.contrib.auth.models import User
from ruido import create_analysis
from django.conf import settings
from .models import Medicion, Punto
from datetime import datetime
from django.contrib.sessions.models import Session

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, './servicios_adapta_app/index.html')
    else:
        return(redirect('login'))
    
def menuRuido(request):
    if request.user.is_authenticated:
        return render(request, './servicios_adapta_app/noise_menu.html')
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

        if request.method == 'POST':
            mins = int(request.POST.get('duracion'))
            input_file = request.FILES.get('input_file')
            radio_value = request.POST.get('opcion')
            if (radio_value == 'effo'):
                ef = True
            elif (radio_value == 'tgm'):
                ef = False

            temp_path = request.FILES.get('template')
            
            if(temp_path is not None):
                template = xl.load_workbook(temp_path)
                template_ws = template[template.sheetnames[1]]

                template_ws, excelname = create_analysis(input_file, template_ws ,mins, ef)
                output_path = os.path.join(""+excelname)
                template.save(output_path)
                # Generate a response with the output file attached
                with open(output_path, 'rb') as f:
                    response = HttpResponse(f.read())
                    response['Content-Type'] = 'application/vnd.ms-excel'
                    response['Content-Disposition'] = f'attachment; filename="{excelname}"'
                os.remove(output_path)
                return response
            else: return render(request, './servicios_adapta_app/process_noise.html')
        else:
            return render(request, './servicios_adapta_app/process_noise.html')       
    else:
        return redirect('login')
    

def mediciones_view(request):
    if request.user.is_authenticated:
        punto_filtro = request.session.get('punto_filtro', None)
        fecha_filtro = request.GET.get('fecha_filtro')

        if request.method == 'POST':
            punto_filtro = request.session['punto_filtro']
            fecha_filtro = request.session['fecha_filtro']
            mediciones = Medicion.objects.all().order_by('-fecha_inicio', 'punto__id')
            
            if punto_filtro:
                mediciones = mediciones.filter(punto_id=punto_filtro)
            
            if fecha_filtro:
                mediciones = mediciones.filter(fecha_inicio=fecha_filtro)
                

            # Generar el archivo Excel solo si hay mediciones filtradas
            if mediciones.exists():
                data = {
                    'Fecha': [medicion.fecha_inicio for medicion in mediciones],
                    'Punto': [medicion.punto.nombre for medicion in mediciones],
                    'Hora Inicio': [medicion.hora_inicio for medicion in mediciones],
                    'Hora Fin': [medicion.hora_fin for medicion in mediciones],
                    'Duración (min)': [medicion.minutos for medicion in mediciones],
                    'Tiempo de estabilización (min)': [medicion.minuto_estabilizacion for medicion in mediciones],
                    'LA,F,eq (dB)': [medicion.laeq for medicion in mediciones],
                    'LA,F,10 (dB)': [medicion.l10 for medicion in mediciones],
                    'LA,F,90 (dB)': [medicion.l90 for medicion in mediciones],
                    'Estándar (dB)': [medicion.estandard for medicion in mediciones],
                }

                df = pd.DataFrame(data)
                df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
                df['Hora Inicio'] = pd.to_datetime(df['Hora Inicio'], format="%H:%M:%S").dt.strftime("%H:%M")
                df['Hora Fin'] = pd.to_datetime(df['Hora Fin'], format="%H:%M:%S").dt.strftime("%H:%M")
                df['LA,F,eq (dB)'] = df['LA,F,eq (dB)'].round(1)
                df['LA,F,10 (dB)'] = df['LA,F,10 (dB)'].round(1)
                df['LA,F,90 (dB)'] = df['LA,F,90 (dB)'].round(1)

                excel_file = pd.ExcelWriter('tabla_mediciones.xlsx')
                df.to_excel(excel_file, sheet_name='Tabla de Mediciones', index=False)
                excel_file.close()

                request.session['punto_filtro'] = punto_filtro
                request.session['fecha_filtro'] = fecha_filtro

                with open('tabla_mediciones.xlsx', 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = 'attachment; filename=tabla_mediciones.xlsx'
                    return response   
        else:
            mediciones = Medicion.objects.all().order_by('fecha_inicio', 'punto__id')
            puntos = Punto.objects.all()
            punto_filtro = request.GET.get('punto')
            fecha_filtro = request.GET.get('fecha_filtro')

            if punto_filtro:
                mediciones = mediciones.filter(punto = punto_filtro)
            
            if fecha_filtro:
                mediciones = mediciones.filter(fecha_inicio=fecha_filtro)
            
            request.session['punto_filtro'] = punto_filtro
            request.session['fecha_filtro'] = fecha_filtro
            
            context = {'mediciones': mediciones, 'puntos': puntos, 'punto_filtro': punto_filtro, 'fecha_filtro': fecha_filtro }

            return render(request, './servicios_adapta_app/tabla_mediciones.html', context)
    else:
        return redirect('login')
    
def add_medicion(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            input_file = request.FILES.get('archivo_excel')
            Medicion.agregar_medicion(Medicion,excel_file=input_file)
            mediciones = mediciones = Medicion.objects.all().order_by('fecha_inicio', 'punto__id')
            puntos = Punto.objects.all()
            context = {'mediciones': mediciones, 'puntos':puntos }
            return render(request, './servicios_adapta_app/tabla_mediciones.html', context)
        else:
            return render(request, './servicios_adapta_app/add_medicion.html')
    else:
        return redirect('login')