# 🏥 API de Predicción de Desnutrición Infantil

Sistema de predicción de riesgo de desnutrición en niños menores de 5 años usando Machine Learning (Random Forest) y desplegado con FastAPI + Docker.

---

## 📋 Tabla de Contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Uso del API](#uso-del-api)
6. [Endpoints](#endpoints)
7. [Ejemplo de Predicción](#ejemplo-de-predicción)
8. [Docker](#docker)
9. [Capturas de Pantalla](#capturas-de-pantalla)

---

## 📖 Descripción del Proyecto

Este proyecto predice el riesgo de desnutrición infantil basándose en variables socioeconómicas, demográficas y de salud. Utiliza un modelo de **Random Forest** entrenado con datos sintéticos que simulan condiciones reales de Perú.

### Variables de entrada:
- Edad (meses)
- Sexo
- Peso (kg)
- Talla (cm)
- Ingresos familiares
- Educación de la madre
- Acceso a servicios básicos (agua, electricidad)
- Altitud
- Distancia al centro de salud

### Variables calculadas:
- IMC (Índice de Masa Corporal)
- Índice de servicios básicos

---

## 📁 Estructura del Proyecto
```
PREDICCION_DESNUTRITIVA/
│
├── api/
│   ├── app.py                      # Código principal del API
│   └── requirements.txt            # Dependencias de Python
│
├── models/
│   ├── random_forest_final.pkl     # Modelo entrenado
│   └── scaler.pkl                  # Escalador de características
│
├── datos/
│   └── raw/                        # Datos crudos (opcional)
│
├── Dockerfile                      # Configuración de Docker
├── .dockerignore                   # Archivos excluidos de Docker
└── README.md                       # Este archivo
```

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.12 | Lenguaje principal |
| FastAPI | 0.104.1 | Framework web |
| Uvicorn | 0.24.0 | Servidor ASGI |
| Scikit-learn | 1.5.1 | Machine Learning |
| Docker | Desktop | Contenerización |
| Pydantic | 2.5.0 | Validación de datos |

---

## 🚀 Instalación y Configuración

### **Opción 1: Instalación Local**

1. **Clonar el repositorio:**
```bash
git clone <URL_DEL_REPOSITORIO>
cd PREDICCION_DESNUTRITIVA
```

2. **Instalar dependencias:**
```bash
pip install -r api/requirements.txt
```

3. **Ejecutar el API:**
```bash
cd api
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

4. **Abrir en el navegador:**
```
http://localhost:8000/docs
```

---

### **Opción 2: Usando Docker (Recomendado)**

1. **Construir la imagen:**
```bash
docker build -t api-desnutricion .
```

2. **Ejecutar el contenedor:**
```bash
docker run -d -p 8000:8000 --name contenedor-desnutricion api-desnutricion
```

3. **Verificar que está corriendo:**
```bash
docker ps
```

4. **Abrir en el navegador:**
```
http://localhost:8000/docs
```

---

## 📡 Endpoints

### **1. GET /** - Información del API
**Respuesta:**
```json
{
  "mensaje": "API de Predicción de Desnutrición Infantil",
  "version": "1.0.0",
  "endpoints": {
    "docs": "/docs",
    "health": "/health",
    "predict": "/predict"
  }
}
```

### **2. GET /health** - Estado del servicio
**Respuesta:**
```json
{
  "status": "healthy",
  "modelo_cargado": true,
  "version": "1.0.0"
}
```

### **3. POST /predict** - Realizar predicción
**Request Body:**
```json
{
  "Edad_meses": 24,
  "Sexo": "M",
  "Peso_kg": 10.5,
  "Talla_cm": 82,
  "Ingresos_soles": 800,
  "Educacion_madre": "Primaria",
  "Acceso_agua": 0,
  "Acceso_electricidad": 0,
  "Altitud_msnm": 3800,
  "Distancia_salud_km": 15
}
```

**Respuesta:**
```json
{
  "riesgo": "Alto",
  "probabilidad": 0.981,
  "factores_clave": [
    "Peso bajo (<12 kg)",
    "Talla baja (<85 cm)",
    "Ingresos bajos (<1000 soles)",
    "Educación básica (Primaria)",
    "Sin acceso a agua potable",
    "Sin acceso a electricidad",
    "Alta altitud (>3500 msnm)",
    "Lejos del centro de salud (>10 km)"
  ],
  "recomendacion": "⚠️ PRIORIDAD ALTA: Evaluación médica URGENTE en 48 horas"
}
```

---

## 🧪 Ejemplo de Predicción

### **Usando cURL:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Edad_meses": 24,
    "Sexo": "M",
    "Peso_kg": 10.5,
    "Talla_cm": 82,
    "Ingresos_soles": 800,
    "Educacion_madre": "Primaria",
    "Acceso_agua": 0,
    "Acceso_electricidad": 0,
    "Altitud_msnm": 3800,
    "Distancia_salud_km": 15
  }'
```

### **Usando Python:**
```python
import requests

url = "http://localhost:8000/predict"
data = {
    "Edad_meses": 24,
    "Sexo": "M",
    "Peso_kg": 10.5,
    "Talla_cm": 82,
    "Ingresos_soles": 800,
    "Educacion_madre": "Primaria",
    "Acceso_agua": 0,
    "Acceso_electricidad": 0,
    "Altitud_msnm": 3800,
    "Distancia_salud_km": 15
}

response = requests.post(url, json=data)
print(response.json())
```

---

## 🐳 Docker

### **Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Comandos útiles:**
```bash
# Ver contenedores activos
docker ps

# Ver logs
docker logs contenedor-desnutricion

# Detener contenedor
docker stop contenedor-desnutricion

# Iniciar contenedor
docker start contenedor-desnutricion

# Eliminar contenedor
docker rm -f contenedor-desnutricion
```

---

## 📸 Capturas de Pantalla

### 1. Estructura del Proyecto
[Imagen 1: Explorer de VS Code]

### 2. Código del API (app.py)
[Imagen 1: Código completo]

### 3. Requirements.txt
[Imagen 2: Dependencias]

### 4. Dockerfile
[Imagen 4: Configuración Docker]

### 5. Dockerignore
[Imagen 3: Archivos excluidos]

### 6. Construcción de Imagen Docker
[Imagen 9: docker build]

### 7. Contenedor Corriendo
[Imagen 10: docker ps]

### 8. API Funcionando
[Imagen de http://localhost:8000/docs]

### 9. Predicción Exitosa
[Imagen de respuesta JSON con predicción]

---
