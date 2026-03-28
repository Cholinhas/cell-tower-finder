import requests
import folium
import webbrowser
import os

# ==================================================
# CONFIGURACIÓN - API KEY YA INCLUIDA
# ==================================================
API_KEY = "pk.b4527c7083f6b44d8b7e4b94ba88a32e"
# ==================================================

def limpiar_pantalla():
    """Limpia la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def obtener_coordenadas():
    """Solicita las coordenadas al usuario"""
    print("\n" + "=" * 60)
    print("📍 COORDENADAS DE BÚSQUEDA")
    print("=" * 60)
    print("Ejemplo: 41.9660289, -7.5284155")
    print("Puedes usar coordenadas de cualquier lugar del mundo.\n")
    
    while True:
        try:
            lat_input = input("🌐 Latitud: ").strip()
            lon_input = input("🌐 Longitud: ").strip()
            
            lat = float(lat_input)
            lon = float(lon_input)
            
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
            else:
                print("❌ Coordenadas fuera de rango. Latitud: -90 a 90, Longitud: -180 a 180")
        except ValueError:
            print("❌ Por favor, introduce números válidos (usa punto decimal, no coma)")

def obtener_radio():
    """Solicita el radio de búsqueda"""
    print("\n" + "=" * 60)
    print("📡 RADIO DE BÚSQUEDA")
    print("=" * 60)
    
    while True:
        try:
            radio = input("🔍 Radio en kilómetros (recomendado: 5-20): ").strip()
            radio_km = float(radio)
            
            if 0.5 <= radio_km <= 100:
                return radio_km
            else:
                print("❌ El radio debe estar entre 0.5 y 100 km")
        except ValueError:
            print("❌ Por favor, introduce un número válido")

def buscar_antenas(lat, lon, radio_km):
    """Busca antenas usando OpenCellID"""
    print("\n" + "=" * 60)
    print("🔍 BUSCANDO ANTENAS...")
    print("=" * 60)
    print(f"📍 Ubicación: {lat}, {lon}")
    print(f"📡 Radio: {radio_km} km")
    print(f"🔑 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    
    url = "https://opencellid.org/cell/getInArea"
    params = {
        'lat': lat,
        'lon': lon,
        'distance': radio_km,
        'format': 'json',
        'key': API_KEY
    }
    
    try:
        print("\n⏳ Conectando con OpenCellID...")
        response = requests.get(url, params=params, timeout=20)
        
        print(f"📡 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            cells = data.get('cells', [])
            return cells
        elif response.status_code == 401:
            print("❌ ERROR: API key inválida")
            return None
        elif response.status_code == 429:
            print("❌ ERROR: Demasiadas peticiones. Espera un minuto.")
            return None
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Tiempo de espera agotado")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def mostrar_resultados(cells, lat, lon, radio_km):
    """Muestra los resultados en consola y genera el mapa"""
    print("\n" + "=" * 60)
    print("📊 RESULTADOS")
    print("=" * 60)
    
    if not cells:
        print("❌ No se encontraron antenas en esta área.")
        print("\nPosibles causas:")
        print("  - Zona rural sin antenas registradas")
        print("  - Radio de búsqueda demasiado pequeño")
        print("  - La API key tiene límite diario alcanzado")
        return False
    
    print(f"✅ Encontradas {len(cells)} antenas en un radio de {radio_km} km")
    print("\n" + "-" * 60)
    
    # Mostrar primeras 15 antenas
    for i, cell in enumerate(cells[:15], 1):
        lat_cell = cell.get('lat', 'N/A')
        lon_cell = cell.get('lon', 'N/A')
        cell_id = cell.get('cellId', 'N/A')
        mnc = cell.get('mnc', 'N/A')
        rango = cell.get('range', 'N/A')
        
        # Identificar operador
        operador = "Desconocido"
        if mnc == 1:
            operador = "Vodafone"
        elif mnc == 3:
            operador = "Orange"
        elif mnc == 6:
            operador = "Vodafone (antiguo)"
        elif mnc == 7:
            operador = "Movistar"
        
        print(f"\n📡 Antena #{i}")
        print(f"   📍 Coordenadas: {lat_cell}, {lon_cell}")
        print(f"   🆔 Cell ID: {cell_id}")
        print(f"   📱 Operador: {operador}")
        print(f"   📏 Rango estimado: {rango} m")
    
    if len(cells) > 15:
        print(f"\n... y {len(cells) - 15} antenas más (aparecen todas en el mapa)")
    
    return True

def generar_mapa(cells, lat, lon):
    """Genera el mapa interactivo"""
    print("\n" + "=" * 60)
    print("🗺️ GENERANDO MAPA INTERACTIVO...")
    print("=" * 60)
    
    try:
        # Crear mapa
        mapa = folium.Map(location=[lat, lon], zoom_start=13)
        
        # Tu ubicación (rojo)
        folium.Marker(
            [lat, lon],
            popup="📍 <b>TU UBICACIÓN</b><br>Coordenadas exactas",
            icon=folium.Icon(color='red', icon='user', prefix='fa')
        ).add_to(mapa)
        
        # Antenas (azul)
        for cell in cells:
            lat_cell = cell.get('lat')
            lon_cell = cell.get('lon')
            if lat_cell and lon_cell:
                cell_id = cell.get('cellId', 'N/A')
                mnc = cell.get('mnc', 'N/A')
                
                operador = "Desconocido"
                if mnc == 1:
                    operador = "Vodafone"
                elif mnc == 3:
                    operador = "Orange"
                elif mnc == 7:
                    operador = "Movistar"
                
                popup_html = f"""
                <div style="font-family: monospace;">
                    <b>📡 ANTENA</b><br>
                    Cell ID: {cell_id}<br>
                    Operador: {operador}<br>
                    MNC: {mnc}
                </div>
                """
                
                folium.Marker(
                    [float(lat_cell), float(lon_cell)],
                    popup=popup_html,
                    icon=folium.Icon(color='blue', icon='signal', prefix='fa')
                ).add_to(mapa)
        
        # Guardar
        archivo = "mapa_antenas.html"
        mapa.save(archivo)
        print(f"✅ Mapa guardado como: {archivo}")
        
        # Abrir en navegador
        print("🌐 Abriendo mapa en el navegador...")
        webbrowser.open(archivo)
        
        return True
        
    except Exception as e:
        print(f"❌ Error al generar el mapa: {e}")
        return False

def main():
    """Función principal"""
    limpiar_pantalla()
    
    print("=" * 60)
    print("📡 BUSCADOR DE ANTENAS DE TELEFONÍA MÓVIL")
    print("=" * 60)
    print("\nEste programa busca antenas de telefonía móvil")
    print("cerca de las coordenadas que introduzcas.\n")
    print("Fuente: OpenCellID (base de datos global)")
    print(f"🔑 API Key cargada: {API_KEY[:8]}...{API_KEY[-4:]}\n")
    
    # Obtener coordenadas y radio
    lat, lon = obtener_coordenadas()
    radio = obtener_radio()
    
    # Confirmar
    print("\n" + "=" * 60)
    print("📋 CONFIRMA LOS DATOS")
    print("=" * 60)
    print(f"📍 Ubicación: {lat}, {lon}")
    print(f"📡 Radio: {radio} km")
    print("=" * 60)
    
    respuesta = input("¿Deseas continuar? (s/n): ").strip().lower()
    if respuesta != 's' and respuesta != 'si':
        print("\n❌ Búsqueda cancelada.")
        return
    
    # Buscar antenas
    cells = buscar_antenas(lat, lon, radio)
    
    if cells is None:
        print("\n❌ No se pudo completar la búsqueda.")
        return
    
    # Mostrar resultados y generar mapa
    if mostrar_resultados(cells, lat, lon, radio):
        generar_mapa(cells, lat, lon)
        
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO")
        print("=" * 60)
        print("💡 Puedes abrir 'mapa_antenas.html' en cualquier navegador.")
        print("   Los marcadores azules 📡 son las antenas encontradas.")
        print("   El marcador rojo 📍 es tu ubicación.")
    else:
        print("\n💡 Sugerencia: prueba con un radio mayor o en una zona urbana.")
    
    print("\n📌 Presiona Enter para salir...")
    input()

if __name__ == "__main__":
    main()