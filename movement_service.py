from datetime import datetime
from database.models import Material, Movement
from services.audit_service import audit

IN_TYPES={"COMPRA","DEVOLUCIÓN","PRODUCCIÓN","TRANSFERENCIA_ENTRADA","AJUSTE_POSITIVO"}
OUT_TYPES={"CONSUMO","VENTA","DAÑO","PÉRDIDA","TRANSFERENCIA_SALIDA","AJUSTE_NEGATIVO","PRODUCCIÓN_SALIDA"}

def register_movement(db,user,material_id,quantity,movement_type,reason="",warehouse_id=None,lot="",serial_number="",notes="",status="APROBADO"):
    if quantity <= 0: raise ValueError("La cantidad debe ser mayor que cero.")
    m=db.get(Material,material_id)
    if not m: raise ValueError("Material no encontrado.")
    if m.status in {"RECHAZADO","CUARENTENA"} and movement_type in OUT_TYPES:
        raise ValueError("El material no está habilitado para consumo/salida.")
    previous=m.stock or 0
    delta=quantity if movement_type in IN_TYPES else -quantity if movement_type in OUT_TYPES else 0
    if movement_type not in IN_TYPES|OUT_TYPES: raise ValueError("Tipo de movimiento inválido.")
    resulting=previous+delta
    if resulting < 0: raise ValueError("Stock insuficiente.")
    mv=Movement(material_id=material_id,user_id=user.id,warehouse_id=warehouse_id,movement_type=movement_type,reason=reason,quantity=quantity,previous_stock=previous,resulting_stock=resulting,lot=lot or m.lot,serial_number=serial_number or m.serial_number,notes=notes,status=status)
    m.stock=resulting; m.last_movement=datetime.utcnow()
    db.add(mv); db.flush()
    audit(db,user,"MOVEMENT","MOVIMIENTOS","Movement",mv.id,old={"stock":previous},new={"stock":resulting,"quantity":quantity,"type":movement_type},description=f"Registró {movement_type} de {quantity} {m.unit} de {m.code}")
    db.commit(); return mv
