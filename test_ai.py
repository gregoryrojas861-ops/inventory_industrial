from ai.prediction import forecast

def test_forecast_small_data():
    r=forecast([1,2,3]); assert len(r["forecast"])==7

def test_forecast_model():
    r=forecast([1,2,3,4,5,6,7,8]); assert r["method"]=="regresión_lineal"
