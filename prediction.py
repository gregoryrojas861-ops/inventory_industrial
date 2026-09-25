import numpy as np
from sklearn.linear_model import LinearRegression

def forecast(values, periods=7):
    values=np.asarray(values,dtype=float)
    if len(values)<2: return {"method":"insuficiente","forecast":[],"confidence":"limitada"}
    if len(values)<5:
        base=float(np.mean(values)); return {"method":"promedio_móvil","forecast":[round(base,2)]*periods,"confidence":"limitada"}
    x=np.arange(len(values)).reshape(-1,1); model=LinearRegression().fit(x,values)
    future=np.arange(len(values),len(values)+periods).reshape(-1,1)
    pred=np.maximum(model.predict(future),0)
    return {"method":"regresión_lineal","forecast":np.round(pred,2).tolist(),"confidence":"moderada"}
