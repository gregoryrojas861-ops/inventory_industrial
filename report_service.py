import pandas as pd
from sqlalchemy import select
from database.models import Material, Movement, AuditLog

def materials_df(db):
    rows=db.scalars(select(Material)).all()
    return pd.DataFrame([{"Código":m.code,"Nombre":m.name,"Categoría":m.category,"Stock":m.stock,"Costo":m.cost,"Valor":m.stock*m.cost,"Mínimo":m.min_stock,"Reorden":m.reorder_point,"Criticidad":m.criticality,"Estado":m.status} for m in rows])

def movements_df(db):
    rows=db.scalars(select(Movement)).all()
    return pd.DataFrame([{"ID":r.id,"Material ID":r.material_id,"Usuario ID":r.user_id,"Tipo":r.movement_type,"Cantidad":r.quantity,"Anterior":r.previous_stock,"Posterior":r.resulting_stock,"Fecha":r.created_at} for r in rows])

def audit_df(db):
    rows=db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc())).all()
    return pd.DataFrame([{"ID":r.id,"Usuario":r.username,"Rol":r.role,"Acción":r.action,"Módulo":r.module,"Registro":r.record_id,"Descripción":r.description,"Resultado":r.result,"Fecha":r.created_at} for r in rows])
