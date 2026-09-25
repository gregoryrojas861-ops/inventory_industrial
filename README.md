# Sistema Inteligente de Control de Inventario Industrial

Aplicación de inventario industrial desarrollada principalmente en Python con Streamlit, SQLite, SQLAlchemy, Pandas, NumPy, Scikit-learn, Plotly, OpenPyXL, ReportLab, QRCode, bcrypt y Pytest.

## 1. Windows + Visual Studio Code

Instala Python 3.11 o superior y abre la carpeta del proyecto en VS Code.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Si PowerShell bloquea la activación, usa:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## 2. Base de datos

SQLite se crea automáticamente como `inventario.db` en la raíz. SQLAlchemy crea las tablas al iniciar la aplicación.

## 3. Primer acceso

En desarrollo local puedes activar **Inicializar datos de prueba** para generar usuarios de ejemplo. En producción no existen credenciales por defecto ni un usuario `admin`/`Admin123!`.

Crea el primer usuario administrador desde la aplicación con una contraseña segura o configura un flujo exclusivo de alta de usuarios antes de poner el sistema en producción.

## 4. Datos de prueba

La inicialización genera materiales, proveedores, almacenes y movimientos ficticios para probar dashboards, alertas y análisis. No representa datos reales de ninguna empresa.

## 5. Flujo básico

1. Inicia sesión.
2. Revisa Dashboard.
3. Consulta Materiales.
4. Registra una entrada o salida en Movimientos.
5. Verifica el stock actualizado.
6. Consulta Auditoría.
7. Realiza un conteo en Inventario físico.
8. Ejecuta IA y predicción cuando exista historial.
9. Genera reportes Excel/CSV/PDF.
10. Crea un respaldo desde Respaldos.

## 6. Roles

ADMINISTRADOR, SUPERVISOR, ALMACENERO, ANALISTA y AUDITOR. El auditor dispone de permisos de consulta y no tiene permisos de modificación de inventario ni de auditoría.

## 7. Pruebas

```powershell
pytest -q
```

## 8. Seguridad

Las contraseñas se almacenan con bcrypt. No coloques secretos en el código. Para despliegues reales utiliza variables de entorno, control de acceso del servidor, copias de seguridad externas y una política formal de recuperación.

## 9. Alcance

El proyecto incluye persistencia, movimientos, trazabilidad básica, auditoría, roles, inventario físico, calidad, alertas, KPI, reportes, QR, respaldos y análisis predictivo. Antes de usarlo en producción industrial real deben validarse reglas contables, fiscales, serialización/lotes, concurrencia, políticas de aprobación y requisitos de ciberseguridad específicos de la organización.
