import numpy as np
from sklearn.ensemble import IsolationForest

def detect(values):
    arr=np.asarray(values,dtype=float)
    if len(arr)<8: return np.zeros(len(arr),dtype=int).tolist(), "insuficiente"
    model=IsolationForest(random_state=42, contamination="auto").fit(arr.reshape(-1,1))
    return model.predict(arr.reshape(-1,1)).tolist(), "IsolationForest"
