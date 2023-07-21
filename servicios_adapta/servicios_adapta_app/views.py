from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.db import IntegrityError
import os
import pandas as pd
import openpyxl as xl
from django.http import HttpResponse
from airfilter import process
from results_ef_fo import pasar_resultados_effo
from django.contrib.auth.models import User
from ruido import create_analysis
from django.conf import settings
from .models import Medicion, Punto
from datetime import datetime
from django.contrib.sessions.models import Session
from .models import experienciaRazonSocial, experienciaProyecto, experienciaLocalizaciones, experienciaContrato
import zipfile

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
    
def menuExperiencia(request):
    if request.user.is_authenticated:
        return render(request, './servicios_adapta_app/experiencia_menu.html')
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
            input_files = request.FILES.getlist('input_file')
            radio_value = request.POST.get('opcion')
            if (radio_value == 'effo'):
                ef = True
            elif (radio_value == 'otro'):
                ef = False
            

            if mins == 60:
                temp_path = 'excel_templates/plantilla60.xlsx'
            elif mins == 30:
                temp_path = settings.EXCEL_TEMPLATES_30
            elif mins == 15:
                # temp_path = 'excel_templates/plantilla15.xlsx'
                temp_path = settings.EXCEL_TEMPLATES_15
            # temp_path = request.FILES.get('template')
            
            if(temp_path is not None):
                template = xl.load_workbook(temp_path)
                template_ws = template[template.sheetnames[1]]

                zip_filename = 'analisis_de_datos.zip'
                output_zip = zipfile.ZipFile(zip_filename, 'w')

                for input_file in input_files:
                    template_ws, excelname = create_analysis(input_file, template_ws, mins, ef)
                    output_path = os.path.join("", excelname)
                    template.save(output_path)
                    output_zip.write(output_path, excelname)
                    os.remove(output_path)

                output_zip.close()

                # Generate a response with the ZIP file attached
                with open(zip_filename, 'rb') as f:
                    response = HttpResponse(f.read())
                    response['Content-Type'] = 'application/zip'
                    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

                os.remove(zip_filename)
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

        # if fecha_filtro:
        #     fecha_filtro = datetime.strptime(fecha_filtro, "%Y-%m").strftime("%Y-%m")

        if request.method == 'POST':
            punto_filtro = request.session['punto_filtro']
            fecha_filtro = request.session['fecha_filtro']
            mediciones = Medicion.objects.all().order_by('fecha_inicio', 'punto__id')
            
            if punto_filtro:
                mediciones = mediciones.filter(punto_id=punto_filtro)
            
            if fecha_filtro:
                fecha_filtro = datetime.strptime(fecha_filtro, "%Y-%m")
                mediciones = mediciones.filter(fecha_inicio__year=fecha_filtro.year, fecha_inicio__month=fecha_filtro.month)
                fecha_filtro = fecha_filtro.strftime("%Y-%m")

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
                    'LA,F,20 (dB)': [medicion.l20 for medicion in mediciones],
                    'LA,F,30 (dB)': [medicion.l30 for medicion in mediciones],
                    'LA,F,40 (dB)': [medicion.l40 for medicion in mediciones],
                    'LA,F,50 (dB)': [medicion.l50 for medicion in mediciones],
                    'LA,F,60 (dB)': [medicion.l60 for medicion in mediciones],
                    'LA,F,70 (dB)': [medicion.l70 for medicion in mediciones],
                    'LA,F,80 (dB)': [medicion.l80 for medicion in mediciones],
                    'LA,F,90 (dB)': [medicion.l90 for medicion in mediciones],
                    'Estándar (dB)': [medicion.estandard for medicion in mediciones],
                }

                df = pd.DataFrame(data)
                df['Fecha'] = df['Fecha'].astype(str)
                df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
                df['Hora Inicio'] = df['Hora Inicio'].astype(str)
                df['Hora Inicio'] = df['Hora Inicio'].apply(eliminarFracciones)
                df['Hora Inicio'] = pd.to_datetime(df['Hora Inicio'], format='%H:%M:%S')
                df['Hora Inicio'] = df['Hora Inicio'].apply(lambda x: x.strftime('%H:%M') if pd.notnull(x) else '')
                #df['Hora Inicio'] = pd.to_datetime(df['Hora Inicio'], format='mixed', dayfirst=True).dt.strftime("%H:%M")
                df['Hora Fin'] = df['Hora Fin'].astype(str)
                df['Hora Fin'] = df['Hora Fin'].apply(eliminarFracciones)
                #df['Hora Fin'] = pd.to_datetime(df['Hora Fin'], format='mixed', dayfirst=True).dt.strftime("%H:%M")
                df['Hora Fin'] = pd.to_datetime(df['Hora Fin'], format='%H:%M:%S')
                df['Hora Fin'] = df['Hora Fin'].apply(lambda x: x.strftime('%H:%M') if pd.notnull(x) else '')
                df['LA,F,eq (dB)'] = df['LA,F,eq (dB)'].round(1)
                df['LA,F,10 (dB)'] = df['LA,F,10 (dB)'].round(1)
                df['LA,F,20 (dB)'] = df['LA,F,20 (dB)'].round(1)
                df['LA,F,30 (dB)'] = df['LA,F,30 (dB)'].round(1)
                df['LA,F,40 (dB)'] = df['LA,F,40 (dB)'].round(1)
                df['LA,F,50 (dB)'] = df['LA,F,50 (dB)'].round(1)
                df['LA,F,60 (dB)'] = df['LA,F,60 (dB)'].round(1)
                df['LA,F,70 (dB)'] = df['LA,F,70 (dB)'].round(1)
                df['LA,F,80 (dB)'] = df['LA,F,80 (dB)'].round(1)
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
                fecha_filtro = datetime.strptime(fecha_filtro, "%Y-%m")
                mediciones = mediciones.filter(fecha_inicio__year=fecha_filtro.year, fecha_inicio__month=fecha_filtro.month)
                fecha_filtro = fecha_filtro.strftime("%Y-%m")
            
            request.session['punto_filtro'] = punto_filtro
            request.session['fecha_filtro'] = fecha_filtro
            
            context = {'mediciones': mediciones, 'puntos': puntos, 'punto_filtro': punto_filtro, 'fecha_filtro': fecha_filtro }
            
            return render(request, './servicios_adapta_app/tabla_mediciones.html', context)
    else:
        return redirect('login')
    
def add_medicion(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            input_files = request.FILES.getlist('archivo_excel')
            for input_file in input_files:
                Medicion.agregar_medicion(Medicion,excel_file=input_file)
                mediciones = mediciones = Medicion.objects.all().order_by('fecha_inicio', 'punto__id')
                puntos = Punto.objects.all()
                context = {'mediciones': mediciones, 'puntos':puntos }
            return render(request, './servicios_adapta_app/tabla_mediciones.html', context)
        else:
            return render(request, './servicios_adapta_app/add_medicion.html')
    else:
        return redirect('login')
    
def borrar_medicion(request, medicion_id):
    if request.method == 'POST':
        # Obtener la instancia de la medición a borrar
        try:
            medicion = Medicion.objects.get(id=medicion_id)
            medicion.delete()
        except Medicion.DoesNotExist:
            # Manejar el caso cuando la medición no existe
            pass
    return redirect('tabla_mediciones')


def resultadosEFFO(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            input_files = request.FILES.getlist('input_files')

            zip_filename = 'resultados_effo.zip'
            output_zip = zipfile.ZipFile(zip_filename, 'w')

            results_ef, results_fo = pasar_resultados_effo(input_files)
            output_path1 = os.path.join("", 'GVC_FCC_R_NPS_EF_MMM_AAAA.xlsx')
            output_path2 = os.path.join("", 'GVC_FCC_R_NPS_FO_MMM_AAAA.xlsx')
            results_ef.save(output_path1)
            results_fo.save(output_path2)

            output_zip.write(output_path1, 'GVC_FCC_R_NPS_EF_MMM_AAAA.xlsx')
            output_zip.write(output_path2, 'GVC_FCC_R_NPS_FO_MMM_AAAA.xlsx')
            os.remove(output_path1)
            os.remove(output_path2)
            output_zip.close()
            
            # Generate a response with the ZIP file attached
            with open(zip_filename, 'rb') as f:
                response = HttpResponse(f.read())
                response['Content-Type'] = 'application/zip'
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

            os.remove(zip_filename)
            return response
        else:
            return render(request, './servicios_adapta_app/resultados_effo.html')
    else:
        return redirect('login')
    


def eliminarFracciones(tiempo):
    # Dividir el tiempo en partes (horas, minutos, segundos)
    partes = tiempo.split(':')
    
    # Eliminar las fracciones si están presentes
    partes_segundos = partes[2].split('.')
    partes[2] = partes_segundos[0]  # Mantener solo los segundos
    
    # Unir las partes nuevamente en un formato de tiempo
    tiempo_sin_fracciones = ':'.join(partes)
    
    return tiempo_sin_fracciones


def experienciaRazones(request):
    if request.user.is_authenticated:
        razones = experienciaRazonSocial.objects.all()
        context = {'razones': razones}
        return render(request, './servicios_adapta_app/experiencia_razones.html', context)
    else:
        return redirect('login')
    
def add_razon(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            nombre_razon = request.POST.get('nombre-razon')
            
            # Verificar si ya existe una razón social con el mismo nombre
            if experienciaRazonSocial.objects.filter(nombre=nombre_razon).exists():
                error_message = "Ya existe una razón social con ese nombre."
            else:
                # Crear una nueva instancia de experienciaRazonSocial con el nombre proporcionado
                experienciaRazonSocial.objects.create(nombre=nombre_razon)
                return redirect('experiencia-razones')

        else:
            error_message = ""
        return render(request, './servicios_adapta_app/experiencia_razones_form.html')
    else:
        return redirect('login')
    
def borrar_razon(request, razon_id):
    if request.method == 'POST':
        # Obtener la instancia de la medición a borrar
        try:
            razon = experienciaRazonSocial.objects.get(id=razon_id)
            razon.delete()
        except experienciaRazonSocial.DoesNotExist:
            # Manejar el caso cuando la medición no existe
            pass
    return redirect('experiencia-razones')
    
def experienciaProyectos(request):
    if request.user.is_authenticated:
        proyectos = experienciaProyecto.objects.all()
        context = {'proyectos': proyectos}
        return render(request, './servicios_adapta_app/experiencia_proyectos.html', context)
    else:
        return redirect('login')
    
def add_proyecto(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            nombre = request.POST.get('nombre-proyecto')
            contacto_nombre = request.POST.get('contacto-nombre')
            contacto_telefono = request.POST.get('contacto-telefono')
            contacto_mail = request.POST.get('contacto-mail')
            razon_id = request.POST.get('razon')
            localizaciones_ids = request.POST.getlist('localizacion')
            sector = request.POST.get('sector')

            proyecto = experienciaProyecto.objects.create(
                nombre=nombre,
                contacto_nombre=contacto_nombre,
                contacto_telefono=contacto_telefono,
                contacto_mail=contacto_mail,
                razon_id=razon_id,
                sector=sector
            )

            proyecto.localizacion.set(localizaciones_ids)

            return redirect('experiencia-proyectos')
        else:
            return render(request, './servicios_adapta_app/experiencia_proyectos_form.html', context={
                'razones_sociales': experienciaRazonSocial.objects.all(),
                'localizaciones': experienciaLocalizaciones.objects.all(),
                'SECTOR_CHOICES': experienciaProyecto.SECTOR_CHOICES
            })
    else:
        return redirect('login')
    
def borrar_proyecto(request, proyecto_id):
    if request.method == 'POST':
        # Obtener la instancia de la medición a borrar
        try:
            proyecto = experienciaProyecto.objects.get(id=proyecto_id)
            proyecto.delete()
        except experienciaProyecto.DoesNotExist:
            # Manejar el caso cuando la medición no existe
            pass
    return redirect('experiencia-proyectos')
    

def experienciaTabla(request):
    if request.user.is_authenticated:
        contratos = experienciaContrato.objects.all()

        return render(request, './servicios_adapta_app/experiencia_table.html', context={'contratos': contratos})
    else:
        return redirect('login')
    
def add_contrato(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            dia_inicio = request.POST.get('dia-inicio')
            mes_inicio = request.POST.get('mes-inicio')
            ano_inicio = request.POST.get('ano-inicio')
            # fecha_inicio = request.POST.get('fecha-inicio')
            fecha_inicio_str = f"{ano_inicio}-{mes_inicio}-{dia_inicio}"
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            except ValueError:
                # Manejar un formato de fecha incorrecto si es necesario
                # Aquí puedes agregar un mensaje de error o redirigir al usuario a una página de error
                return HttpResponse("Error: Formato de fecha incorrecto")
            
            dia_fin = request.POST.get('dia-fin')
            mes_fin = request.POST.get('mes-fin')
            ano_fin = request.POST.get('ano-fin')
            fecha_fin_str = f"{ano_fin}-{mes_fin}-{dia_fin}"
            if fecha_fin_str != "0000-00-00":
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            else:
                fecha_fin = "En curso"

            codigo = request.POST.get('codigo')
            cat_servicios = request.POST.get('cat-servicios')
            ficha = request.FILES.get('ficha')
            atestado = request.FILES.get('atestado')
            proyecto_id = request.POST.get('proyecto')
            # roles = obtener los roles seleccionados
            try:
                contrato = experienciaContrato.objects.create(
                    fechaInicio=fecha_inicio,
                    fechaFin=fecha_fin,
                    codigo=codigo,
                    catServicios=cat_servicios,
                    ficha=ficha,
                    atestado=atestado,
                    proyecto_id=proyecto_id
                )
            except IntegrityError:
                return HttpResponse("Error: Codigo ya existente")

            # Asignar los roles al contrato

            return redirect('experiencia-tabla')
        else:
            return render(request, './servicios_adapta_app/experiencia_form.html', context={
                'proyectos': experienciaProyecto.objects.all(),
                'CAT_CHOICES': experienciaContrato.CAT_CHOICES
            })
    else:
        return redirect('login')

