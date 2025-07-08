from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import Configuration, Component, PrebuiltPC
import json
import os

def load_components():
    """Load component data from MySQL database only"""
    components = {}
    
    try:
        # Load from MySQL database only
        db_components = Component.query.filter_by(is_active=True).all()
        for comp in db_components:
            if comp.category not in components:
                components[comp.category] = []
            
            comp_data = {
                'id': comp.id,
                'name': comp.name,
                'price': comp.price,
                **comp.get_specs()
            }
            components[comp.category].append(comp_data)
    except Exception as e:
        # If database is not connected, return empty structure
        print(f"Database error: {e}")
    
    # Initialize empty categories if no components exist yet
    if not components:
        components = {
            'cpus': [],
            'motherboards': [],
            'ram': [],
            'gpus': [],
            'ssds': [],
            'cases': [],
            'psus': [],
            'coolers': []
        }
    
    return components

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/konfigurator')
def configurator():
    components = load_components()
    return render_template('configurator.html', components=components)

@app.route('/fertig-pcs')
def prebuild():
    # Load from database first
    prebuilt_pcs = []
    db_prebuilts = PrebuiltPC.query.filter_by(is_active=True).all()
    
    if db_prebuilts:
        for pc in db_prebuilts:
            prebuilt_pcs.append({
                'id': pc.id,
                'name': pc.name,
                'price': pc.price,
                'image': pc.image_url,
                'category': pc.category,
                'description': pc.description,
                'specs': pc.get_specs(),
                'features': pc.get_features()
            })
    else:
        # Fallback data if database is empty
        prebuilt_pcs = [
        {
            "name": "Gaming Beast Pro",
            "price": 1899.99,
            "image": "https://via.placeholder.com/400x300/1a1a1a/0066cc?text=Gaming+Beast+Pro",
            "category": "gaming",
            "specs": {
                "cpu": "AMD Ryzen 7 7800X3D",
                "gpu": "NVIDIA RTX 4070 Super",
                "ram": "32GB DDR5-5600",
                "storage": "1TB NVMe SSD",
                "motherboard": "ASUS ROG Strix X670E-E",
                "cooler": "Corsair H100i RGB Elite",
                "case": "NZXT H7 Flow",
                "psu": "Corsair RM850x 850W"
            },
            "description": "Perfekt für Gaming in 1440p und 4K",
            "features": [
                "Optimiert für Gaming-Performance",
                "RGB-Beleuchtung",
                "Leise Wasserkühlung",
                "Zukunftssicher mit DDR5"
            ]
        },
        {
            "name": "Workstation Elite",
            "price": 2499.99,
            "image": "https://via.placeholder.com/400x300/2d2d2d/ff6b35?text=Workstation+Elite",
            "category": "workstation",
            "specs": {
                "cpu": "Intel Core i9-14900K",
                "gpu": "NVIDIA RTX 4080",
                "ram": "64GB DDR5-5600",
                "storage": "2TB NVMe SSD",
                "motherboard": "MSI MPG Z790 Carbon WiFi",
                "cooler": "Noctua NH-D15",
                "case": "Fractal Design Define 7",
                "psu": "Seasonic Focus GX-750 750W"
            },
            "description": "Ideal für Content Creation und professionelle Anwendungen",
            "features": [
                "Extreme Multi-Core Performance",
                "64GB RAM für schwere Workloads",
                "Premium-Luftkühlung",
                "Leises Design"
            ]
        },
        {
            "name": "Budget Gamer",
            "price": 899.99,
            "image": "https://via.placeholder.com/400x300/343a40/28a745?text=Budget+Gamer",
            "category": "gaming",
            "specs": {
                "cpu": "AMD Ryzen 5 7600X",
                "gpu": "NVIDIA RTX 4060",
                "ram": "16GB DDR5-5200",
                "storage": "500GB NVMe SSD",
                "motherboard": "ASRock B650M Pro4",
                "cooler": "Arctic Freezer 34 eSports",
                "case": "Cooler Master MasterBox Q300L",
                "psu": "be quiet! Pure Power 11 600W"
            },
            "description": "Solide Gaming-Performance für Einsteiger",
            "features": [
                "Beste Preis-Leistung",
                "1080p Gaming bereit",
                "Kompaktes Design",
                "Upgrade-freundlich"
            ]
        },
        {
            "name": "Content Creator Pro",
            "price": 1699.99,
            "image": "https://via.placeholder.com/400x300/6c757d/17a2b8?text=Content+Creator",
            "category": "workstation",
            "specs": {
                "cpu": "AMD Ryzen 7 7800X3D",
                "gpu": "NVIDIA RTX 4070 Super",
                "ram": "32GB DDR5-5600",
                "storage": "1TB NVMe SSD + 2TB HDD",
                "motherboard": "ASUS ROG Strix X670E-E",
                "cooler": "Corsair H100i RGB Elite",
                "case": "NZXT H7 Flow",
                "psu": "Corsair RM850x 850W"
            },
            "description": "Perfekt für Streaming, Video-Editing und Content Creation",
            "features": [
                "Streaming-optimiert",
                "Schnelle Render-Zeiten",
                "RGB-Beleuchtung",
                "Viel Speicherplatz"
            ]
        },
        {
            "name": "Office Professional",
            "price": 599.99,
            "image": "https://via.placeholder.com/400x300/f8f9fa/343a40?text=Office+Pro",
            "category": "office",
            "specs": {
                "cpu": "AMD Ryzen 5 7600X",
                "gpu": "Integrierte Grafik",
                "ram": "16GB DDR5-5200",
                "storage": "500GB NVMe SSD",
                "motherboard": "ASRock B650M Pro4",
                "cooler": "Arctic Freezer 34 eSports",
                "case": "Cooler Master MasterBox Q300L",
                "psu": "be quiet! Pure Power 11 600W"
            },
            "description": "Leistungsstarker Office-PC für professionelle Anwendungen",
            "features": [
                "Energieeffizient",
                "Leise im Betrieb",
                "Schnelle SSD",
                "Kompakte Bauweise"
            ]
        },
        {
            "name": "4K Gaming Monster",
            "price": 3299.99,
            "image": "https://via.placeholder.com/400x300/1a1a1a/dc3545?text=4K+Gaming+Monster",
            "category": "gaming",
            "specs": {
                "cpu": "Intel Core i9-14900K",
                "gpu": "NVIDIA RTX 4080",
                "ram": "64GB DDR5-6000",
                "storage": "2TB NVMe SSD",
                "motherboard": "MSI MPG Z790 Carbon WiFi",
                "cooler": "Corsair H100i RGB Elite",
                "case": "NZXT H7 Flow",
                "psu": "Corsair RM850x 850W"
            },
            "description": "Ultimative Gaming-Performance für 4K-Gaming ohne Kompromisse",
            "features": [
                "4K Gaming bereit",
                "Ray-Tracing aktiviert",
                "Extreme Performance",
                "Premium-Komponenten"
            ]
        }
        ]
    
    return render_template('prebuild.html', prebuilt_pcs=prebuilt_pcs)

@app.route('/api/validate-compatibility', methods=['POST'])
def validate_compatibility():
    """Validate PC component compatibility"""
    data = request.json
    components = load_components()
    
    errors = []
    warnings = []
    
    # Get selected components
    selected_cpu = next((cpu for cpu in components['cpus'] if cpu['id'] == data.get('cpu')), None)
    selected_mb = next((mb for mb in components['motherboards'] if mb['id'] == data.get('motherboard')), None)
    selected_ram = next((ram for ram in components['ram'] if ram['id'] == data.get('ram')), None)
    selected_gpu = next((gpu for gpu in components['gpus'] if gpu['id'] == data.get('gpu')), None)
    selected_cooler = next((cooler for cooler in components['coolers'] if cooler['id'] == data.get('cooler')), None)
    selected_case = next((case for case in components['cases'] if case['id'] == data.get('case')), None)
    selected_psu = next((psu for psu in components['psus'] if psu['id'] == data.get('psu')), None)
    
    # CPU and Motherboard socket compatibility
    if selected_cpu and selected_mb:
        if selected_cpu['socket'] != selected_mb['socket']:
            errors.append(f"CPU-Socket {selected_cpu['socket']} ist nicht kompatibel mit Motherboard-Socket {selected_mb['socket']}")
    
    # RAM compatibility with motherboard
    if selected_ram and selected_mb:
        if selected_ram['type'] not in selected_mb['ram_types']:
            errors.append(f"RAM-Typ {selected_ram['type']} wird vom Motherboard nicht unterstützt")
        if selected_ram['speed'] > selected_mb['max_ram_speed']:
            warnings.append(f"RAM-Geschwindigkeit {selected_ram['speed']}MHz überschreitet die maximale Motherboard-Geschwindigkeit {selected_mb['max_ram_speed']}MHz")
    
    # GPU and Case compatibility
    if selected_gpu and selected_case:
        if selected_gpu['length'] > selected_case['max_gpu_length']:
            errors.append(f"GPU-Länge {selected_gpu['length']}mm überschreitet die maximale Case-Länge {selected_case['max_gpu_length']}mm")
    
    # Cooler compatibility
    if selected_cooler and selected_cpu:
        if selected_cpu['socket'] not in selected_cooler['compatible_sockets']:
            errors.append(f"Kühler ist nicht kompatibel mit CPU-Socket {selected_cpu['socket']}")
    
    if selected_cooler and selected_case:
        if selected_cooler['height'] > selected_case['max_cooler_height']:
            errors.append(f"Kühler-Höhe {selected_cooler['height']}mm überschreitet die maximale Case-Höhe {selected_case['max_cooler_height']}mm")
    
    # Power supply wattage calculation
    total_wattage = 0
    if selected_cpu:
        total_wattage += selected_cpu['tdp']
    if selected_gpu:
        total_wattage += selected_gpu['power_consumption']
    if selected_mb:
        total_wattage += selected_mb['power_consumption']
    if selected_ram:
        total_wattage += selected_ram['power_consumption']
    
    # Add overhead for other components
    total_wattage += 100  # SSD, fans, etc.
    
    if selected_psu:
        recommended_wattage = total_wattage * 1.2  # 20% headroom
        if selected_psu['wattage'] < recommended_wattage:
            errors.append(f"Netzteil-Leistung {selected_psu['wattage']}W ist zu niedrig. Empfohlen: {recommended_wattage:.0f}W")
        elif selected_psu['wattage'] < total_wattage:
            errors.append(f"Netzteil-Leistung {selected_psu['wattage']}W ist unzureichend für den Gesamtverbrauch von {total_wattage}W")
    
    # Calculate total price
    total_price = 0
    for component_type, component_id in data.items():
        if component_id:
            component_list = components.get(component_type + 's', [])
            component = next((c for c in component_list if c['id'] == component_id), None)
            if component:
                total_price += component['price']
    
    return jsonify({
        'compatible': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'total_price': total_price,
        'total_wattage': total_wattage
    })

@app.route('/api/components/<category>')
def get_components(category):
    """Get components by category"""
    components = load_components()
    return jsonify(components.get(category, []))
