import pandas as pd

def consumption_stats(df):
    if df.empty: return {}
    x=df.copy(); x["quantity"]=pd.to_numeric(x["quantity"],errors="coerce").fillna(0)
    return {"total":float(x.quantity.sum()),"average":float(x.quantity.mean()),"std":float(x.quantity.std() or 0),"count":int(len(x))}
