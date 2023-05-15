import pandas as pd
import numpy as np
import openpyxl as xl

#import csv
def csv_df(path):
    df = pd.read_csv(path)
    return df

#load template excel
def template_excel(path):
    temp_wb = xl.load_workbook(path)
    return temp_wb

#name code
def name_code_and_date(path):
    if ("\\" in path):
        codigo = path.split("\\")[-1]
    else:
        codigo = path.split("/")[-1]

    codigo = codigo.split(".")[0]

    #check if name is ef/fo or not
    if ("FO") not in path:
        if ("_") in codigo:
            date = codigo.split("_")[-1]
            codigo = codigo.split("_")[0]
        else:
            date = ""
    else:
        date = codigo.split("_")[1]
    
    return codigo, date

def create_analysis(csv, mins, ef, save):
    
    #selecting temp_path
    if (mins == 30):
        temp_path = "./noise_templates/template_30.xlsx"
    elif (mins == 15):
        temp_path = "./noise_templates/template_15.xlsx"
    elif (mins == 60):
        temp_path = "./noise_templates/template_60.xlsx"
    
    #loading
    template = template_excel(temp_path)
    template_ws = template[template.sheetnames[1]]

    data = csv_df(csv)
    name_code, date_code = name_code_and_date(csv)

    #columns
    columnas_data = []
    for col in data.columns:
        columnas_data.append(col)

    #total time of analysis
    total_mins = int(len(data)/60)

    if (mins < total_mins):
        total_rows = (mins * 60)
    else:
        total_rows = total_mins * 60
        
    data = data[0:total_rows]

    #convert to dateTime else error
    data["Fecha"] = pd.to_datetime(data["Fecha"], dayfirst=True)
    data["Tiempo"] = pd.to_datetime(data["Tiempo"], format="mixed")

    #inserting data at excel worksheet
    template_ws["A2"].value = data[columnas_data[0]][0]
    template_ws["B2"].value = data[columnas_data[1]][0]
    template_ws["C2"].value = data[columnas_data[1]][total_rows-1]
    template_ws["D2"].value = name_code

    i = 0
    j = 5

    while i < total_rows:
        template_ws['A'+str(j)].value = data[columnas_data[1]][i]
        template_ws['B'+str(j)].value = data[columnas_data[2]][i]
        j += 1
        i += 1

    if (ef) and ('FO' not in name_code):
        save = save + name_code + "_Operación_" + date_code + ".xlsx"
    elif (not ef):
        save = save + name_code + date_code + ".xlsx"

    template.save(save)
    
