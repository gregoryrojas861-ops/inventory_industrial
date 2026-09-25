from io import BytesIO
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

def excel_bytes(df):
    b=BytesIO()
    with pd.ExcelWriter(b,engine="openpyxl") as w: df.to_excel(w,index=False,sheet_name="Reporte")
    b.seek(0); return b

def csv_bytes(df): return df.to_csv(index=False).encode("utf-8-sig")

def pdf_bytes(df,title="Reporte"):
    b=BytesIO(); doc=SimpleDocTemplate(b,pagesize=letter)
    data=[list(df.columns)]+df.fillna("").astype(str).values.tolist(); data=data[:1001]
    table=Table(data,repeatRows=1); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0A192F")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.25,colors.grey)])); doc.build([table]); b.seek(0); return b
