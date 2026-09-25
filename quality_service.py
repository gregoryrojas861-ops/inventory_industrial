from database.models import QualityRecord
from services.audit_service import audit

def record_quality(db,user,material,status,reason="",observations=""):
    if status not in {"APROBADO","PENDIENTE DE INSPECCIÓN","RECHAZADO","CUARENTENA"}: raise ValueError("Estado de calidad inválido.")
    rec=QualityRecord(material_id=material.id,lot=material.lot,inspector=user.full_name,status=status,reason=reason,observations=observations); material.status=status; db.add(rec); audit(db,user,"QUALITY_UPDATE","CALIDAD","Material",material.id,new={"status":status},description=f"Actualizó calidad de {material.code}"); db.commit(); return rec
