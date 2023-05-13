import pandas as pd
import numpy as np
import openpyxl as xl
import datetime

def df_from_file(path):
    df = pd.read_excel(path)
    #separar columna fecha
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], dayfirst=True)
    df['Date'] = df['TimeStamp'].dt.date
    return df

def arr_df_days(df):
    arr = [group[1] for group in df.groupby(['Date'])]
    return arr

def filer_data(df):
    num = len(df[(df['Humidity (% RH)'] > 85) & (df['Wind Speed (mtr/sec)'] < 0.5) & (df['Temperature (Celsius)'] < 8)])
    if num > 0:
        filtered_df = df.drop(df[(df['Humidity (% RH)'] > 85) & (df['Wind Speed (mtr/sec)'] < 0.5) & (df['Temperature (Celsius)'] < 8)].index)
        filtered_df = filtered_df.reset_index(drop=True)
        return filtered_df
    else: return df
    
def day_means(df):
    new_df = df.drop(['TimeStamp', 'Date', 'Comments'], axis=1)
    new_df = new_df.mean(axis=0)
    new_df['Date'] = df['Date'].iloc[0]
    return new_df

def vector_mean(df):
    if(len(df) >= 216):
        total = len(df)
        rad_arr = np.radians(df['Wind Direction (degrees)'])
        sin_arr = np.sin(rad_arr)
        cos_arr = np.cos(rad_arr)
        u = (1/total)*np.sum(sin_arr)
        v = (1/total)*np.sum(cos_arr)

        if ((u > 0) & (v >0)):
            wind_dir = np.arctan(u/v)
        elif ((u < 0) & (v > 0)):
            wind_dir = np.arctan(u/v) + 360
        else:
            wind_dir = np.arctan(u/v) + 180
        
        return u, v, wind_dir
    else:
        return '-', '-', '-'
               

def day_row(df):
    day_df = day_means(df)
    day_df['u'], day_df['v'] , day_df['Predominant Wind Direction']= vector_mean(df)
    day_df['Length'] = len(df)
    if (len(df) < 216):
        day_df['PM2.5 particles (ug/m^3)'] = "-"
        day_df['PM10 particles (ug/m^3)'] = "-"
    
    #de serie a df y reordenar
    day_df_frame = day_df.to_frame()
    columns = day_df_frame.index.values.tolist()
    oredered_df = pd.DataFrame()
    for val in columns:
        oredered_df[val] = [day_df[val]]
    
    return oredered_df

def conc_dfs(rows):
    days_df = pd.concat(rows, ignore_index=True)
    #reorder by month
    days_df = days_df.sort_values('Date')
    return days_df

def final_df(df, pt, est1, est2):
    new_columns = ['Fecha', 
               'Punto', 
               'Cantidad de datos', 
               'Temperatura (°C)', 
               'Velocidad del viento (m/s)', 
               'Dirección predominante del viento', 
               'Humedad promedio (%)',
               'PM2.5 (μg/Nm3)',
               'PM10 (μg/Nm3)',
               'Estándar PM2.5 (μg/Nm3)',
               'Estándar PM10 (μg/Nm3)']
    
    new_df = pd.DataFrame(columns=new_columns)
    new_df[new_columns[0]] = df['Date']
    new_df[new_columns[1]] = pt
    new_df[new_columns[2]] = df['Length']
    new_df[new_columns[3]] = df['Temperature (Celsius)']
    new_df[new_columns[4]] = df['Wind Speed (mtr/sec)']
    new_df[new_columns[5]] = df['Predominant Wind Direction']
    new_df[new_columns[6]] = df['Humidity (% RH)']
    new_df[new_columns[7]] = df['PM2.5 particles (ug/m^3)']
    new_df[new_columns[8]] = df['PM10 particles (ug/m^3)']
    new_df[new_columns[9]] = est1
    new_df[new_columns[10]] = est2
    
    return new_df 


def process(file_path, pt, est1, est2):
    df = df_from_file(file_path)
    arr = arr_df_days(df)
    rows_arr = [day_row(row) for row in arr]
    month_df = conc_dfs(rows_arr)
    save_df = final_df(month_df, pt, est1, est2)
    return save_df
    # save_df.to_excel(filefolder + "/" + save_name + '.xlsx', index=False)
    # print('Saved as: ' + save_name)

