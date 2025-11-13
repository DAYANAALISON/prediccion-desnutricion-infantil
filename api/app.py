from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import pickle
import numpy as np
from typing import List
import os

app = FastAPI(
    title="API Predicción Desnutrición Infantil",
    description="Predice riesgo de desnutrición en niños menores de 5 años",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelo y scaler
ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_modelo = os.path.join(ruta_base, 'models', 'random_forest_final.pkl')
ruta_scaler = os.path.join(ruta_base, 'models', 'scaler.pkl')

print(f"📂 Cargando modelo desde: {ruta_modelo}")
print(f"📂 Cargando scaler desde: {ruta_scaler}")

with open(ruta_modelo, 'rb') as f:
    modelo = pickle.load(f)

with open(ruta_scaler, 'rb') as f:
    scaler = pickle.load(f)

print("✅ Modelo y scaler cargados correctamente")

class NinoInput(BaseModel):
    Edad_meses: int = Field(..., ge=6, le=60, description="Edad en meses (6-60)")
    Sexo: str = Field(..., description="Sexo: 'M' o 'F'")
    Peso_kg: float = Field(..., gt=0, lt=50, description="Peso en kg")
    Talla_cm: float = Field(..., gt=0, lt=150, description="Talla en cm")
    Ingresos_soles: float = Field(..., ge=0, description="Ingresos mensuales en soles")
    Educacion_madre: str = Field(..., description="Educación: Primaria, Secundaria o Superior")
    Acceso_agua: int = Field(..., ge=0, le=1, description="Acceso a agua: 0=No, 1=Sí")
    Acceso_electricidad: int = Field(..., ge=0, le=1, description="Acceso a electricidad: 0=No, 1=Sí")
    Altitud_msnm: int = Field(..., ge=0, le=5000, description="Altitud en metros")
    Distancia_salud_km: float = Field(..., ge=0, description="Distancia al centro de salud en km")

    @field_validator('Sexo')
    def validar_sexo(cls, v):
        if v not in ['M', 'F']:
            raise ValueError("Sexo debe ser 'M' o 'F'")
        return v
    
    @field_validator('Educacion_madre')
    def validar_educacion(cls, v):
        if v not in ['Primaria', 'Secundaria', 'Superior']:
            raise ValueError("Educacion_madre debe ser: Primaria, Secundaria o Superior")
        return v

class Prediccion(BaseModel):
    riesgo: str
    probabilidad: float
    factores_clave: List[str]
    recomendacion: str

@app.get("/")
def root():
    return {
        "mensaje": "API de Predicción de Desnutrición Infantil",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "predict": "/predict"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "modelo_cargado": True,
        "version": "1.0.0"
    }

@app.post("/predict", response_model=Prediccion)
def predecir_riesgo(nino: NinoInput):
    imc = nino.Peso_kg / (nino.Talla_cm / 100) ** 2
    
    education_map = {'Primaria': 1, 'Secundaria': 2, 'Superior': 3}
    educacion_num = education_map[nino.Educacion_madre]
    
    sexo_num = 1 if nino.Sexo == 'M' else 0
    
    indice_servicios = (nino.Acceso_agua + nino.Acceso_electricidad) / 2
    
    features = np.array([[
        nino.Edad_meses,
        sexo_num,
        nino.Peso_kg,
        nino.Talla_cm,
        nino.Ingresos_soles,
        educacion_num,
        nino.Acceso_agua,
        nino.Acceso_electricidad,
        nino.Altitud_msnm,
        nino.Distancia_salud_km,
        imc,
        indice_servicios
    ]])
    
    features_scaled = scaler.transform(features)
    
    probabilidad = float(modelo.predict_proba(features_scaled)[0][1])
    riesgo = "Alto" if probabilidad >= 0.5 else "Bajo"
    
    factores = []
    if nino.Peso_kg < 12:
        factores.append("Peso bajo (<12 kg)")
    if nino.Talla_cm < 85:
        factores.append("Talla baja (<85 cm)")
    if nino.Ingresos_soles < 1000:
        factores.append("Ingresos bajos (<1000 soles)")
    if nino.Educacion_madre == 'Primaria':
        factores.append("Educación básica (Primaria)")
    if nino.Acceso_agua == 0:
        factores.append("Sin acceso a agua potable")
    if nino.Acceso_electricidad == 0:
        factores.append("Sin acceso a electricidad")
    if nino.Altitud_msnm > 3500:
        factores.append("Alta altitud (>3500 msnm)")
    if nino.Distancia_salud_km > 10:
        factores.append("Lejos del centro de salud (>10 km)")
    
    if probabilidad >= 0.8:
        recomendacion = "⚠️ PRIORIDAD ALTA: Evaluación médica URGENTE en 48 horas"
    elif probabilidad >= 0.5:
        recomendacion = "⚠️ PRIORIDAD MEDIA: Evaluación médica en 7 días"
    else:
        recomendacion = "✅ Seguimiento rutinario en controles CRED"
    
    return Prediccion(
        riesgo=riesgo,
        probabilidad=round(probabilidad, 3),
        factores_clave=factores if factores else ["Sin factores críticos detectados"],
        recomendacion=recomendacion
    )