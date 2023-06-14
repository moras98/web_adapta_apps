from django.db import models
import openpyxl as xl
from datetime import datetime

class Proyecto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Punto(models.Model):
    id = models.AutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"Punto {self.id} - Proyecto: {self.proyecto.nombre}"

class Medicion(models.Model):
    fecha_inicio = models.DateField()
    punto = models.ForeignKey(Punto, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    minutos = models.IntegerField()
    minuto_estabilizacion = models.IntegerField()
    laeq = models.FloatField()
    l10 = models.FloatField()
    l20 = models.FloatField()
    l30 = models.FloatField()
    l40 = models.FloatField()
    l50 = models.FloatField()
    l60 = models.FloatField()
    l70 = models.FloatField()
    l80 = models.FloatField()
    l90 = models.FloatField()
    estandard = models.FloatField()

    def __str__(self):
        return f"Medicion - Fecha: {self.fecha_inicio}, Punto: {self.punto.nombre}"

    def agregar_medicion(cls, excel_file):
        workbook = xl.load_workbook(excel_file, read_only=True, data_only=True)
        worksheet = workbook[workbook.sheetnames[1]]
        worksheet2 = workbook[workbook.sheetnames[2]]

        fecha_inicio = worksheet['A2'].value
        if (isinstance(fecha_inicio, str)):
            fecha_inicio = datetime.strptime(fecha_inicio, "%d/%m/%Y")
        punto_nombre = worksheet['D2'].value
        if '0' in punto_nombre:
            punto_nombre = punto_nombre.replace('0', '')
        punto_obj = Punto.objects.get(nombre = punto_nombre)
        punto = punto_obj.id
        hora_inicio = worksheet['B2'].value
        hora_fin = worksheet['C2'].value
        minutos = worksheet['I3'].value
        laeq = worksheet['I5'].value
        l10 = worksheet2['C3'].value
        l20 = worksheet2['D3'].value
        l30 = worksheet2['E3'].value
        l40 = worksheet2['F3'].value
        l50 = worksheet2['G3'].value
        l60 = worksheet2['H3'].value
        l70 = worksheet2['I3'].value
        l80 = worksheet2['J3'].value
        l90 = worksheet2['K3'].value
        estandard = 75

        i = 5
        while (worksheet['R'+str(i)].value == 'No'):
            i += 1

        minuto_estabilizacion = worksheet['L'+str(i)].value

        if not cls.objects.filter(fecha_inicio = fecha_inicio, punto = punto_obj, hora_inicio = hora_inicio).exists():
            medicion = cls(
                fecha_inicio = fecha_inicio,
                punto = punto_obj,
                hora_inicio = hora_inicio,
                hora_fin = hora_fin,
                minutos = minutos,
                minuto_estabilizacion = minuto_estabilizacion,
                laeq = laeq,
                l10 = l10,
                l20 = l20,
                l30 = l30,
                l40 = l40,
                l50 = l50,
                l60 = l60,
                l70 = l70,
                l80 = l80,
                l90 = l90,
                estandard = estandard,
            )
            medicion.save()
        else: return


class experiencia_Cliente(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class experiencia_Contacto(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    mail = models.EmailField()
    
    def __str__(self):
        return self.name
    
class experiencia_Localizacion(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class experiencia_Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class experiencia_Proyecto(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    cliente = models.ForeignKey(experiencia_Cliente, on_delete=models.CASCADE)
    contacto = models.ForeignKey(experiencia_Contacto, on_delete=models.CASCADE)
    localizaciones = models.ManyToManyField('experiencia_Localizacion')
    categoria = models.ForeignKey(experiencia_Categoria, on_delete=models.CASCADE)
    ficha = models.FileField(upload_to='fichas/', null=True, blank=True)
    comentarios = models.TextField()
    atestado_hecho = models.BooleanField()
    atestado_firmado = models.BooleanField()

    def __str__(self):
        return self.name
    

class experiencia_Contrato(models.Model):
    fecha_inicio = models.DateField(null=True, blank=True)  # Mes y año o vacío
    fecha_fin = models.DateField(null=True, blank=True)  # Mes y año, "en curso", "a la fecha" o vacío
    SECTOR_CHOICES = (
        ('sector1', 'Sector 1'),
        ('sector2', 'Sector 2'),
        ('sector3', 'Sector 3'),
        # Agrega aquí más opciones de sector según tus necesidades
    )
    sector = models.CharField(max_length=255, choices=SECTOR_CHOICES)
    id = models.CharField(max_length=10, unique=True)  # Formato AAMM_XX
    proyecto = models.ForeignKey(experiencia_Proyecto, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.id:
            # Obtener los últimos dos dígitos del año en fecha_inicio
            if self.fecha_inicio:
                ultimos_dos_digitos_ano = self.fecha_inicio.strftime("%y")
            else:
                ultimos_dos_digitos_ano = ""

            # Obtener los dos dígitos del mes en fecha_inicio
            if self.fecha_inicio:
                dos_digitos_mes = self.fecha_inicio.strftime("%m")
            else:
                dos_digitos_mes = ""

            # Obtener el último número de contrato para el mes y año especificados
            contratos_mes_anio = experiencia_Contrato.objects.filter(
                id__startswith=f"{ultimos_dos_digitos_ano}{dos_digitos_mes}"
            )
            ultimo_numero = contratos_mes_anio.count() + 1

            # Crear el ID en formato AAMM_XX
            self.id = f"{ultimos_dos_digitos_ano}{dos_digitos_mes}_{str(ultimo_numero).zfill(2)}"

        super().save(*args, **kwargs)