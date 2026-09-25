import uuid
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import select, func
from database.database import init_db, SessionLocal
from database.models import User, Material, Movement, Supplier, Warehouse, Alert, AuditLog
from data.sample_data import seed
from services.inventory_service import create_material, inventory_summary
from services.movement_service import register_movement
from services.audit_service import audit
from services.alert_service import refresh_alerts
from services.report_service import materials_df, movements_df, audit_df
from services.backup_service import backup_database
from utils.security import verify_password, hash_password, has_permission, ROLES
from utils.calculations import safety_stock, reorder_point, eoq, coverage, rotation
from utils.exporters import excel_bytes, csv_bytes, pdf_bytes
from utils.qr_generator import make_qr
from ai.prediction import forecast
from database.database import is_demo_mode

st.set_page_config(page_title="Inventario Industrial",page_icon="🏭",layout="wide")
init_db()

def get_session(): return SessionLocal()

def login():
    st.title("🏭 Sistema Inteligente de Control de Inventario Industrial")
    st.caption("Gestión industrial con trazabilidad, auditoría, KPI e inteligencia analítica")
    with st.form("login"):
        u=st.text_input("Usuario"); p=st.text_input("Contraseña",type="password"); ok=st.form_submit_button("Ingresar")
    if ok:
        db=get_session(); user=db.scalar(select(User).where(User.username==u,User.active==True))
        if user and verify_password(p,user.password_hash):
            st.session_state.user_id=user.id; st.session_state.session_id=str(uuid.uuid4()); audit(db,user,"LOGIN","SEGURIDAD",description="Inicio de sesión"); db.commit(); st.rerun()
        else: st.error("Credenciales inválidas.")
    if is_demo_mode():
        st.info("Este entorno permite generar datos de prueba para desarrollo local. En producción no se crean credenciales ni usuarios por defecto.")
        if st.button("Inicializar datos de prueba"):
            db=get_session(); created=seed(db); st.success("Datos creados." if created else "La base ya contiene datos."); db.close()
    else:
        st.warning("Modo producción activo: no se permiten usuarios ni credenciales por defecto. Crea usuarios reales y configura las variables de entorno antes de continuar.")
    st.stop()

if "user_id" not in st.session_state: login()
db=get_session(); user=db.get(User,st.session_state.user_id)
if not user or not user.active: st.session_state.clear(); st.rerun()

def allowed(p): return has_permission(user.role,p)

def save_material():
    data={"code":st.session_state.mcode.strip(),"barcode":st.session_state.mbarcode.strip() or None,"name":st.session_state.mname.strip(),"description":st.session_state.mdesc,"category":st.session_state.mcat,"unit":st.session_state.munit,"cost":float(st.session_state.mcost),"stock":float(st.session_state.mstock),"min_stock":float(st.session_state.mmin),"max_stock":float(st.session_state.mmax),"safety_stock":float(st.session_state.msafety),"reorder_point":float(st.session_state.mreorder),"location":st.session_state.mloc,"criticality":st.session_state.mcrit,"status":"APROBADO"}
    create_material(db,user,data)

st.sidebar.title("🏭 Inventario Industrial")
st.sidebar.write(f"**{user.full_name}** · {user.role}")
menu=["Dashboard","Materiales","Movimientos","Inventario físico","Compras y proveedores","Calidad","IA y predicción","KPI","Reportes","Auditoría","Alertas","Usuarios y configuración","Respaldos"]
page=st.sidebar.radio("Módulo",menu)
if st.sidebar.button("Cerrar sesión"): audit(db,user,"LOGOUT","SEGURIDAD",description="Cierre de sesión"); db.commit(); st.session_state.clear(); st.rerun()

if page=="Dashboard":
    if not allowed("inventory.read"): st.error("Sin permisos."); st.stop()
    refresh_alerts(db); s=inventory_summary(db); st.title("Dashboard")
    cols=st.columns(5)
    for c,label,val in zip(cols,["Valor inventario","Materiales","Críticos","Agotados","Stock bajo"],[f"$ {s['value']:,.2f}",s['materials'],s['critical'],s['out'],s['low']]): c.metric(label,val)
    df=materials_df(db)
    if not df.empty:
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(px.bar(df.nlargest(10,"Valor"),x="Código",y="Valor",title="Top 10 por valor"),use_container_width=True)
        with c2: st.plotly_chart(px.pie(df,names="Criticidad",title="Criticidad del inventario"),use_container_width=True)
    st.subheader("Alertas activas"); alerts=db.scalars(select(Alert).where(Alert.resolved==False).order_by(Alert.created_at.desc())).all(); st.dataframe(pd.DataFrame([{"Nivel":a.level,"Tipo":a.alert_type,"Mensaje":a.message,"Fecha":a.created_at} for a in alerts]),use_container_width=True)

elif page=="Materiales":
    st.title("Materiales")
    if allowed("inventory.write"):
        with st.expander("➕ Registrar material"):
            for key,val in [("mcode","MAT-NEW"),("mbarcode",""),("mname",""),("mdesc",""),("mcat","Materia Prima"),("munit","unidad"),("mcost",0.0),("mstock",0.0),("mmin",0.0),("mmax",100.0),("msafety",10.0),("mreorder",20.0),("mloc",""),("mcrit","MEDIA")]: st.session_state.setdefault(key,val)
            st.text_input("Código",key="mcode"); st.text_input("Código de barras",key="mbarcode"); st.text_input("Nombre",key="mname"); st.text_area("Descripción",key="mdesc"); a,b,c=st.columns(3); a.text_input("Categoría",key="mcat"); b.text_input("Unidad",key="munit"); c.number_input("Costo",min_value=0.0,key="mcost"); a,b,c=st.columns(3); a.number_input("Stock inicial",min_value=0.0,key="mstock"); b.number_input("Stock mínimo",min_value=0.0,key="mmin"); c.number_input("Stock máximo",min_value=0.0,key="mmax"); a,b,c=st.columns(3); a.number_input("Stock seguridad",min_value=0.0,key="msafety"); b.number_input("Punto reorden",min_value=0.0,key="mreorder"); c.text_input("Ubicación",key="mloc"); st.selectbox("Criticidad",["BAJA","MEDIA","ALTA","CRÍTICA"],key="mcrit")
            if st.button("Guardar material"):
                try: save_material(); st.success("Material guardado."); st.rerun()
                except Exception as e: db.rollback(); st.error(str(e))
    df=materials_df(db); st.dataframe(df,use_container_width=True)
    if not df.empty:
        code=st.selectbox("QR de material",df["Código"].tolist()); m=db.scalar(select(Material).where(Material.code==code)); st.download_button("Descargar QR",make_qr(f"MATERIAL:{m.code}|{m.name}"),file_name=f"QR_{m.code}.png",mime="image/png")

elif page=="Movimientos":
    st.title("Entradas y salidas")
    if allowed("movements.write"):
        mats=db.scalars(select(Material).order_by(Material.code)).all(); wh=db.scalars(select(Warehouse)).all()
        if mats:
            with st.form("movement"):
                m=st.selectbox("Material",mats,format_func=lambda x:f"{x.code} · {x.name}"); typ=st.selectbox("Tipo",["COMPRA","DEVOLUCIÓN","PRODUCCIÓN","CONSUMO","VENTA","DAÑO","PÉRDIDA","AJUSTE_POSITIVO","AJUSTE_NEGATIVO"]); qty=st.number_input("Cantidad",min_value=0.01); reason=st.text_input("Motivo"); notes=st.text_area("Observaciones"); submit=st.form_submit_button("Registrar movimiento")
            if submit:
                try: register_movement(db,user,m.id,qty,typ,reason,m.warehouse_id,notes=notes); st.success("Movimiento registrado y stock actualizado."); st.rerun()
                except Exception as e: db.rollback(); st.error(str(e))
    st.dataframe(movements_df(db),use_container_width=True)

elif page=="Inventario físico":
    st.title("Inventario físico y conciliación")
    mats=db.scalars(select(Material)).all()
    if allowed("physical.write") and mats:
        with st.form("physical"):
            m=st.selectbox("Material",mats,format_func=lambda x:f"{x.code} · {x.name}"); physical=st.number_input("Cantidad física",min_value=0.0); submit=st.form_submit_button("Registrar conteo")
        if submit:
            diff=physical-m.stock; val=diff*m.cost; from database.models import PhysicalInventory; rec=PhysicalInventory(material_id=m.id,system_quantity=m.stock,physical_quantity=physical,difference=diff,difference_value=val,counted_by=user.id); db.add(rec); audit(db,user,"PHYSICAL_COUNT","INVENTARIO_FISICO","PhysicalInventory",description=f"Conteo {m.code}: diferencia {diff}"); db.commit(); st.success("Conteo guardado. El ajuste requiere autorización según política.")
    from database.models import PhysicalInventory
    rows=db.scalars(select(PhysicalInventory).order_by(PhysicalInventory.created_at.desc())).all(); st.dataframe(pd.DataFrame([{"Material ID":r.material_id,"Sistema":r.system_quantity,"Físico":r.physical_quantity,"Diferencia":r.difference,"Valor":r.difference_value,"Estado":r.status,"Fecha":r.created_at} for r in rows]),use_container_width=True)

elif page=="Compras y proveedores":
    st.title("Compras y proveedores")
    st.subheader("Proveedores"); sups=db.scalars(select(Supplier)).all(); st.dataframe(pd.DataFrame([{"Código":s.code,"Proveedor":s.name,"Lead time":s.avg_lead_time,"Cumplimiento":round(s.on_time_rate*100,1)} for s in sups]),use_container_width=True)
    st.info("La recepción de compras puede generar movimientos de entrada y queda auditada. La estructura de órdenes está persistida en SQLite.")

elif page=="Calidad":
    st.title("Control de calidad")
    from database.models import QualityRecord
    mats=db.scalars(select(Material)).all()
    if allowed("quality.write") and mats:
        with st.form("quality"):
            m=st.selectbox("Material",mats,format_func=lambda x:f"{x.code} · {x.name}"); status=st.selectbox("Estado",["APROBADO","PENDIENTE DE INSPECCIÓN","RECHAZADO","CUARENTENA"]); reason=st.text_input("Motivo"); obs=st.text_area("Observaciones"); ok=st.form_submit_button("Guardar inspección")
        if ok:
            db.add(QualityRecord(material_id=m.id,lot=m.lot,inspector=user.full_name,status=status,reason=reason,observations=obs)); m.status=status; audit(db,user,"QUALITY_UPDATE","CALIDAD","Material",m.id,new={"status":status},description=f"Inspección de calidad {m.code}"); db.commit(); st.success("Registro de calidad guardado.")
    rows=db.scalars(select(QualityRecord).order_by(QualityRecord.created_at.desc())).all(); st.dataframe(pd.DataFrame([{"Material":r.material_id,"Inspector":r.inspector,"Estado":r.status,"Motivo":r.reason,"Fecha":r.created_at} for r in rows]),use_container_width=True)

elif page=="IA y predicción":
    st.title("Inteligencia artificial")
    st.caption("Las predicciones usan únicamente historial almacenado. Con pocos datos se muestra una confianza limitada.")
    mats=db.scalars(select(Material)).all(); m=st.selectbox("Material",mats,format_func=lambda x:f"{x.code} · {x.name}") if mats else None
    if m:
        movs=db.scalars(select(Movement).where(Movement.material_id==m.id).order_by(Movement.created_at)).all(); values=[r.quantity for r in movs if r.movement_type in {"CONSUMO","VENTA","PRODUCCIÓN_SALIDA","DAÑO","PÉRDIDA"}]
        result=forecast(values,7); st.write(f"**Método:** {result['method']} · **Confiabilidad:** {result['confidence']}"); st.write(result["forecast"])
        if result["forecast"]: st.plotly_chart(px.line(x=list(range(1,8)),y=result["forecast"],markers=True,title="Demanda proyectada"),use_container_width=True)
        st.info("La recomendación de compra debe validarse con los parámetros industriales configurados y las restricciones reales de abastecimiento.")

elif page=="KPI":
    st.title("Indicadores KPI")
    df=movements_df(db); mats=materials_df(db)
    consumption=float(df.loc[df["Tipo"].isin(["CONSUMO","VENTA","PRODUCCIÓN_SALIDA"]),"Cantidad"].sum()) if not df.empty else 0
    value=float(mats["Valor"].sum()) if not mats.empty else 0
    c1,c2,c3,c4=st.columns(4); c1.metric("Valor inventario",f"$ {value:,.2f}"); c2.metric("Consumo registrado",f"{consumption:,.2f}"); c3.metric("Movimientos",len(df)); c4.metric("Rotación aprox.",round(consumption/value,4) if value else 0)
    st.dataframe(mats,use_container_width=True)

elif page=="Reportes":
    st.title("Reportes")
    typ=st.selectbox("Reporte",["Inventario","Movimientos","Auditoría"]); df=materials_df(db) if typ=="Inventario" else movements_df(db) if typ=="Movimientos" else audit_df(db)
    st.dataframe(df,use_container_width=True); st.download_button("Excel",excel_bytes(df),file_name="reporte.xlsx"); st.download_button("CSV",csv_bytes(df),file_name="reporte.csv"); st.download_button("PDF",pdf_bytes(df,typ),file_name="reporte.pdf")

elif page=="Auditoría":
    if not allowed("audit.read"): st.error("Sin permisos."); st.stop()
    st.title("Auditoría — solo lectura"); st.dataframe(audit_df(db),use_container_width=True)

elif page=="Alertas":
    st.title("Alertas inteligentes"); refresh_alerts(db); alerts=db.scalars(select(Alert).order_by(Alert.created_at.desc())).all(); st.dataframe(pd.DataFrame([{"ID":a.id,"Nivel":a.level,"Tipo":a.alert_type,"Mensaje":a.message,"Resuelta":a.resolved,"Fecha":a.created_at} for a in alerts]),use_container_width=True)

elif page=="Usuarios y configuración":
    st.title("Usuarios y configuración")
    if user.role=="ADMINISTRADOR":
        with st.form("newuser"):
            un=st.text_input("Usuario"); fn=st.text_input("Nombre completo"); pw=st.text_input("Contraseña",type="password"); role=st.selectbox("Rol",sorted(ROLES)); ok=st.form_submit_button("Crear usuario")
        if ok:
            if db.scalar(select(User).where(User.username==un)): st.error("Usuario ya existe.")
            elif len(pw)<8: st.error("La contraseña debe tener al menos 8 caracteres.")
            else: db.add(User(username=un,full_name=fn,password_hash=hash_password(pw),role=role)); audit(db,user,"CREATE","USUARIOS",description=f"Creó usuario {un}"); db.commit(); st.success("Usuario creado.")
        users=db.scalars(select(User)).all(); st.dataframe(pd.DataFrame([{"Usuario":u.username,"Nombre":u.full_name,"Rol":u.role,"Activo":u.active} for u in users]),use_container_width=True)
    else: st.info("Solo el administrador gestiona usuarios y configuración sensible.")

elif page=="Respaldos":
    st.title("Copias de seguridad")
    if user.role=="ADMINISTRADOR":
        if st.button("Crear respaldo"):
            p=backup_database(); st.success(f"Respaldo creado: {p.name}")
            with open(p,"rb") as f: st.download_button("Descargar respaldo",f.read(),file_name=p.name,mime="application/octet-stream")
    else: st.info("Solo el administrador puede crear/restaurar respaldos.")

db.close()
