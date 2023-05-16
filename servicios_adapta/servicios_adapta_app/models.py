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
    l90 = models.FloatField()
    estandard = models.FloatField()

    def __str__(self):
        return f"Medicion - Fecha: {self.fecha_inicio}, Punto: {self.punto.name}"

    def agregar_medicion(cls, excel_file):
        workbook = xl.load_workbook(excel_file, read_only=True, data_only=True)
        worksheet = workbook[workbook.sheetnames[1]]
        worksheet2 = workbook[workbook.sheetnames[2]]

        fecha_inicio = worksheet['A2'].value
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
                l90 = l90,
                estandard = estandard,
            )
            medicion.save()
        else: return