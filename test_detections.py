"""
Script de prueba para el sistema de detecciones de Odin Vision
Simula el flujo completo desde la configuración hasta la recepción de detecciones
"""

import requests
import json
from typing import Optional

# Configuración
BASE_URL = "http://localhost:8000"
# Obtén tu token haciendo login primero
TOKEN = "YOUR_TOKEN_HERE"  # Reemplazar con tu token JWT

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def print_response(title: str, response: requests.Response):
    """Imprime la respuesta de forma legible"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_1_create_patio():
    """Paso 1: Crear un patio de prueba"""
    print("\n🏢 PASO 1: Creando patio de prueba...")
    
    data = {
        "patio_id": "patio_test_001",
        "name": "Patio de Prueba",
        "description": "Patio para pruebas del sistema de detecciones",
        "location": "Edificio de Pruebas, Planta Baja",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/patios",
        headers=headers,
        json=data
    )
    
    print_response("Crear Patio", response)
    
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_2_create_camera(patio_id: int):
    """Paso 2: Crear una cámara de prueba"""
    print("\n📹 PASO 2: Creando cámara de prueba...")
    
    data = {
        "mac": "AA:BB:CC:DD:EE:01",
        "name": "Cámara de Prueba 1",
        "model": "Hikvision DS-2CD2143G0-I",
        "ip_address": "192.168.1.100",
        "patio_id": patio_id,
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/cameras",
        headers=headers,
        json=data
    )
    
    print_response("Crear Cámara", response)
    
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_3_send_detection_from_camera():
    """Paso 3: Simular envío de detección desde cámara (sin autenticación)"""
    print("\n📸 PASO 3: Simulando envío desde cámara Hikvision...")
    
    # Este endpoint NO requiere autenticación
    data = {
        'patio_id': 'patio_test_001',
        'mac': 'AA:BB:CC:DD:EE:01',
        'image_path': '/captures/2025-12-09/test_image_001.jpg'
    }
    
    # Simular archivo de imagen (opcional)
    # files = {'image': open('test_image.jpg', 'rb')}
    
    response = requests.post(
        f"{BASE_URL}/detections/upload",
        data=data
        # files=files  # Descomentar si tienes una imagen
    )
    
    print_response("Envío desde Cámara", response)
    
    if response.status_code == 201:
        return response.json().get("detection_id")
    return None


def test_4_get_pending_detections():
    """Paso 4: Obtener detecciones pendientes de procesar"""
    print("\n🔍 PASO 4: Obteniendo detecciones pendientes...")
    
    response = requests.get(
        f"{BASE_URL}/detections?processed=false&limit=10",
        headers=headers
    )
    
    print_response("Detecciones Pendientes", response)
    
    if response.status_code == 200:
        return response.json()
    return []


def test_5_update_detection_with_ai_results(detection_id: int):
    """Paso 5: Actualizar detección con resultados de IA"""
    print("\n🤖 PASO 5: Actualizando detección con resultados de IA...")
    
    data = {
        "detection_type": "threat",
        "confidence": 0.95,
        "objects_detected": {
            "threat_level": "high",
            "objects": [
                {
                    "class": "person",
                    "confidence": 0.98,
                    "bbox": [100, 200, 300, 400]
                },
                {
                    "class": "weapon",
                    "confidence": 0.92,
                    "bbox": [150, 250, 200, 300]
                }
            ]
        },
        "processed": True,
        "processing_time": 0.5
    }
    
    response = requests.patch(
        f"{BASE_URL}/detections/{detection_id}",
        headers=headers,
        json=data
    )
    
    print_response("Actualizar Detección", response)


def test_6_get_detection_details(detection_id: int):
    """Paso 6: Obtener detalles completos de la detección"""
    print("\n📊 PASO 6: Obteniendo detalles de la detección...")
    
    response = requests.get(
        f"{BASE_URL}/detections/{detection_id}/details",
        headers=headers
    )
    
    print_response("Detalles de Detección", response)


def test_7_get_stats():
    """Paso 7: Obtener estadísticas generales"""
    print("\n📈 PASO 7: Obteniendo estadísticas...")
    
    # Estadísticas generales
    response = requests.get(
        f"{BASE_URL}/detections/stats",
        headers=headers
    )
    print_response("Estadísticas Generales", response)
    
    # Estadísticas de patio
    response = requests.get(
        f"{BASE_URL}/patios/1/stats",
        headers=headers
    )
    print_response("Estadísticas de Patio", response)
    
    # Estadísticas de cámara
    response = requests.get(
        f"{BASE_URL}/cameras/1/stats",
        headers=headers
    )
    print_response("Estadísticas de Cámara", response)


def test_8_list_all():
    """Paso 8: Listar todos los recursos"""
    print("\n📋 PASO 8: Listando todos los recursos...")
    
    # Listar patios
    response = requests.get(f"{BASE_URL}/patios", headers=headers)
    print_response("Todos los Patios", response)
    
    # Listar cámaras
    response = requests.get(f"{BASE_URL}/cameras", headers=headers)
    print_response("Todas las Cámaras", response)
    
    # Listar detecciones
    response = requests.get(f"{BASE_URL}/detections?limit=5", headers=headers)
    print_response("Últimas Detecciones", response)


def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*60)
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE DETECCIONES")
    print("="*60)
    
    if TOKEN == "YOUR_TOKEN_HERE":
        print("\n❌ ERROR: Debes configurar tu TOKEN primero")
        print("1. Haz login: POST /auth/jwt/login")
        print("2. Copia el token")
        print("3. Reemplaza 'YOUR_TOKEN_HERE' en este script")
        return
    
    # Ejecutar pruebas en orden
    patio_id = test_1_create_patio()
    if not patio_id:
        print("\n❌ Error creando patio. Verifica que tengas permisos de ADMIN")
        return
    
    camera_id = test_2_create_camera(patio_id)
    if not camera_id:
        print("\n❌ Error creando cámara")
        return
    
    detection_id = test_3_send_detection_from_camera()
    if not detection_id:
        print("\n❌ Error enviando detección desde cámara")
        return
    
    test_4_get_pending_detections()
    test_5_update_detection_with_ai_results(detection_id)
    test_6_get_detection_details(detection_id)
    test_7_get_stats()
    test_8_list_all()
    
    print("\n" + "="*60)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)


if __name__ == "__main__":
    main()
