def recommend(material, forecast_demand):
    projected=sum(forecast_demand)
    target=max(material.max_stock or 0, material.reorder_point or 0)
    qty=max(0.0,target-(material.stock or 0)+projected)
    return {"material":material.code,"recommended_quantity":round(qty,2),"reason":"Proyección histórica + nivel objetivo configurado." if projected else "No hay suficiente historial para una recomendación confiable."}
