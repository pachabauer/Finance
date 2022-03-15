#IMPORTO LIBRERIAS QUE VOY A USAR
import pandas as pd, numpy as np
import yfinance as yf
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

start = "2022-01-01" #ESTABLEZCO FECHA DE INICIO

#ESTABLEZCO LOS TICKERS A TRAER
tickersCedears = ["AAPL","ABEV","ABT","ACH","ADBE","ADGO","AIG","AMD","AMX","AMZN","ANF","ARCO","AUY","AXP","AZN",
                  "BA","BABA","BAC","BBD","BIDU","BRKB",
                  "C","CAT","COST","CRM","CSCO","CVX",
                  "DESP","DISN",
                  "EBAY","ERJ",
                  "FB","FCX",
                  "GE","GGB","GILD","GLNT","GOLD","GOOGL","GS",
                  "HAL","HD","HMY","HPQ","HSBC",
                  "IBM","INTC","ITUB",
                  "JD","JPM",
                  "KO",
                  "LFC","LMT","LYG",
                  "MA","MCD","MELI","MMM","MO","MSFT",
                  "NFLX","NKE","NOKA","NVDA",
                  "OGZD",
                  "PAAS","PBR","PEP","PFE","PG","PYPL","PTR",
                  "QCOM",
                  "RIO",
                  "SAN","SAP","SBUX","SHEL","SHOP","SLB","SNOW","SONY","SPOT","SQ",
                  "T","TEN","TM","TMO","TSLA","TSM","TWTR","TXR",
                  "UGP","UL",
                  "V","VALE","VIST","VZ",
                  "WFC","WMT",
                  "X","XOM",
                  "ZM"]

#ARMO UN 1ER DATAFRAME CON LA COLUMNA CLOSE Y SACO LOS NA Y USO EL DATETIME PARA MANEJAR LAS FECHAS FACIL
try:
    carteraCedears = pd.DataFrame(yf.download(tickersCedears, start)["Close"])
except:
    pass

# CREO UN DICCIONARIO PARA ASIGNAR A CADA TICKER EL NOMBRE DE SU COMPANIA (es diferente el yf.download que el yf.Ticker). YAHOO FINANCE ESTA CON MUCHISIMO DELAY EN TICKER
nombreCedears = pd.read_excel('Listado Cedears.xlsx')
nombreCedears = nombreCedears.set_index('ticker')['denominacion'] .to_dict()

carteraCedears.dropna(inplace=False)
carteraCedears.index = pd.to_datetime(carteraCedears.index)

carteraCedears['Año'] = carteraCedears.index.year #ESTABLEZCO LA COLUMNA AÑO PARA HACER EL GROUPBY POSTERIOR
carteraCedears.dropna(inplace=False)

#AGRUPO POR ACTIVO Y CALCULO POR AÑO SU MIN,MAX,MIN Y ULTIMO PRECIO DE AÑO
carteraCedearsAño = pd.DataFrame(carteraCedears.groupby('Año')[tickersCedears].agg([np.min,np.max,np.mean,'last']))
carteraCedearsAño = carteraCedears.round(2)

#GENERO EL NUEVO DATAFRAME QUE TRAE SOLO TICKERS Y MIN,MAX,MEAN,CLOSE Y TOmax
carteraCedearsFinal = pd.DataFrame(carteraCedears[tickersCedears].agg([np.min,np.max,np.mean]))
carteraCedearsFinal = carteraCedearsFinal.round(2)

inicio  =pd.DataFrame(carteraCedears.iloc[[0]]) #ASI TRAE EL PRIMER DIA DEL AÑO
inicio.drop(['Año'], axis=1, inplace=True)
inicio = inicio.round(2)

cierres = pd.DataFrame(carteraCedears.iloc[[-1]]) #ASI SE TRAE EL CLOSE DEL ÚLTIMO DÍA EN CURSO
cierres.drop(['Año'], axis=1, inplace=True)
cierres = cierres.round(2)

#EL IGNORE_INDEX ES NECESARIO PARA QUE NO SE MEZCLE VALORES DATE CON STRINGS Y SE TORNE INMANEJABLE
carteraCedearsFinal = carteraCedearsFinal.append([cierres,inicio], ignore_index=True)
carteraCedearsFinal = carteraCedearsFinal.transpose()
carteraCedearsFinal.columns = ['Mín_Hist','Max_Hist','Prom','Precio_Cierre','Precio_Inicio']
carteraCedearsFinal.drop(['Prom'], axis=1, inplace=True)

#DIVIDO CLOSE Y MAX PARA SABER CUANTO BAJO
carteraCedearsFinal['Baja%DesdeMax22'] = round(carteraCedearsFinal['Precio_Cierre'] / carteraCedearsFinal['Max_Hist'],2) -1
#DIVIDO MAX Y CLOSE PARA SABER CUANTO TIENE QUE SUBIR
carteraCedearsFinal['SubaHastaMax22'] = round(carteraCedearsFinal['Max_Hist'] / carteraCedearsFinal['Precio_Cierre'],2) -1
#DIVIDO CIERRE E INICIO PARA LOS QUE SUBIERON EN EL AÑO
carteraCedearsFinal['SubanEn22'] = round(carteraCedearsFinal['Precio_Cierre'] / carteraCedearsFinal['Precio_Inicio'],2) -1
carteraCedearsFinal.dropna(inplace=True)
carteraCedearsFinal['denominacion'] = carteraCedearsFinal.index.map(nombreCedears)

#RENOMBRO LOS INDEX, TRANSMUTO EL DATAFRAME Y ORDENO DESCENDENTE Y BORRO PROM QUE NO ES UTIL
#SELECCIONO LOS 20 PRIMEROS
df_ordenado = carteraCedearsFinal.sort_values(by=['Baja%DesdeMax22'] ,ascending=True)
df_ordenado.drop(['Mín_Hist','Max_Hist','Precio_Cierre','Precio_Inicio','SubanEn22'], axis=1, inplace=True)
ordenadoSubasHasta = carteraCedearsFinal.sort_values(by=['SubaHastaMax22'],ascending=False)
ordenadoSubieron = carteraCedearsFinal.sort_values(by=['SubanEn22'],ascending=False)
df_ordenado['Baja%DesdeMax22'] = (df_ordenado['Baja%DesdeMax22'] * 100)
df_ordenado['Baja%DesdeMax22'] = df_ordenado['Baja%DesdeMax22'].astype(int)
df_ordenado['SubaHastaMax22'] = (df_ordenado['SubaHastaMax22'] * 100)
df_ordenado['SubaHastaMax22'] = df_ordenado['SubaHastaMax22'].astype(int)
ordenadoSubieron['SubanEn22'] = (ordenadoSubieron['SubanEn22'] * 100)
ordenadoSubieron['SubanEn22'] = ordenadoSubieron['SubanEn22'].astype(int)

#carteraCedearsFinal["nombreTicker"] = carteraCedearsFinal.index.map(listaTicker)
df_ordenado = df_ordenado.head(20)
ordenadoSubieron = ordenadoSubieron.head(20)

#EXPORTO EL DATAFRAME A EXCEL
datoexcelCedears = pd.ExcelWriter("CedearsToMax.xlsx")
carteraCedearsFinal.to_excel(datoexcelCedears)
datoexcelCedears.save()

# NORMALIZO LOS COLORES PARA DEFINIR UN RANGOS DE COLORES.
tamañosBajas = df_ordenado['Baja%DesdeMax22']
tamañosBajas2 = [abs(i) for i in tamañosBajas]
norm = matplotlib.colors.Normalize(vmin=min(tamañosBajas), vmax=max(tamañosBajas))
colores = [matplotlib.cm.Spectral(norm(value)) for value in tamañosBajas]

# FIGURA > BAJAS
f, ax = plt.subplots(figsize=(16, 10))
sns.set_color_codes("bright")
sns.barplot(y=df_ordenado['denominacion'],x=tamañosBajas2, data=df_ordenado,palette="RdBu")
initialx=0
for p in ax.patches:
    plt.rcParams["font.weight"] = "bold"
    ax.text(p.get_width(),initialx+p.get_height()/6,"  {:1.0f}%".format(p.get_width()),fontsize=15)
    initialx+=1
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
ax.set(xlabel='', ylabel='')
plt.show()

# FIGURA CUÁNTO POR SUBIR
# NORMALIZO LOS COLORES PARA DEFINIR UN RANGOS DE COLORES.
tamañosSubas = df_ordenado['SubaHastaMax22']
tamañosSubas2 = [abs(i) for i in tamañosSubas]
norm = matplotlib.colors.Normalize(vmin=min(tamañosSubas), vmax=max(tamañosSubas))
colores = [matplotlib.cm.Spectral(norm(value)) for value in tamañosSubas]

f, ax = plt.subplots(figsize=(16, 10))
sns.set_color_codes("bright")
sns.barplot(y=df_ordenado['denominacion'],x=tamañosSubas2, data=df_ordenado,palette="ocean")
initialx=0
for p in ax.patches:
    plt.rcParams["font.weight"] = "bold"
    ax.text(p.get_width(),initialx+p.get_height()/6,"  {:1.0f}%".format(p.get_width()),fontsize=15)
    initialx+=1

plt.xticks(fontsize=14)
plt.yticks(fontsize=13)
ax.set(xlabel='', ylabel='')
plt.show()

# FIGURA SUBIERON 2022
# NORMALIZO LOS COLORES PARA DEFINIR UN RANGOS DE COLORES.
tamañosSubieron = ordenadoSubieron['SubanEn22']
tamañosSubieron2 = [abs(i) for i in tamañosSubieron]
norm = matplotlib.colors.Normalize(vmin=min(tamañosSubieron), vmax=max(tamañosSubieron))
colores = [matplotlib.cm.Spectral(norm(value)) for value in tamañosSubieron]

f, ax = plt.subplots(figsize=(16, 10))
sns.set_color_codes("bright")
sns.barplot(y=ordenadoSubieron['denominacion'],x=tamañosSubieron2, data=df_ordenado,palette="summer")
initialx=0
for p in ax.patches:
    plt.rcParams["font.weight"] = "bold"
    ax.text(p.get_width(),initialx+p.get_height()/6,"  {:1.0f}%".format(p.get_width()),fontsize=15)
    initialx+=1

plt.xticks(fontsize=14)
plt.yticks(fontsize=13)
ax.set(xlabel='', ylabel='')
plt.show()
