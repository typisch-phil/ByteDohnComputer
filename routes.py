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
    # Load exclusively from MySQL database - no fallback data
    prebuilt_pcs = []
    
    try:
        db_prebuilts = PrebuiltPC.query.filter_by(is_active=True).order_by(PrebuiltPC.created_at.desc()).all()
        
        for pc in db_prebuilts:
            prebuilt_pcs.append({
                'id': pc.id,
                'name': pc.name,
                'price': pc.price,
                'image': pc.image_url or f"https://via.placeholder.com/400x300/2d2d2d/ff6b35?text={pc.name.replace(' ', '+')}",
                'category': pc.category,
                'description': pc.description,
                'specs': pc.get_specs(),
                'features': pc.get_features()
            })
    except Exception as e:
        print(f"Database error loading prebuilt PCs: {e}")
        # No fallback data - show empty list if database fails
        prebuilt_pcs = []
    
    return render_template('prebuild.html', prebuilts=prebuilt_pcs)

@app.route('/api/validate-compatibility', methods=['POST'])
def validate_compatibility():
    """Validate PC component compatibility"""
    try:
        data = request.json
        components = load_components()
        
        errors = []
        warnings = []
        
        # Get selected components - safely handle missing categories  
        # Map database categories to component types
        category_mapping = {
            'cpu': 'cpus',
            'motherboard': 'motherboards', 
            'ram': 'ram',
            'gpu': 'gpus',
            'ssd': 'ssds',
            'case': 'cases',
            'psu': 'psus',
            'cooler': 'coolers'
        }
        
        selected_cpu = None
        selected_mb = None
        selected_ram = None
        selected_gpu = None
        selected_cooler = None
        selected_case = None
        selected_psu = None
        
        # Handle all categories from the database structure
        all_components = {}
        for category in ['cpus', 'motherboards', 'ram', 'gpus', 'ssds', 'cases', 'psus', 'coolers']:
            all_components[category] = components.get(category, [])
        
        print(f"Debug - Received data: {data}")
        print(f"Debug - Available components: {list(components.keys())}")
        
        if data.get('cpu'):
            selected_cpu = next((cpu for cpu in all_components['cpus'] if cpu['id'] == data.get('cpu')), None)
            print(f"Debug - Selected CPU: {selected_cpu}")
        if data.get('motherboard'):
            selected_mb = next((mb for mb in all_components['motherboards'] if mb['id'] == data.get('motherboard')), None)
            print(f"Debug - Selected Motherboard: {selected_mb}")
        if data.get('ram'):
            selected_ram = next((ram for ram in all_components['ram'] if ram['id'] == data.get('ram')), None)
            print(f"Debug - Selected RAM: {selected_ram}")
        if data.get('gpu'):
            selected_gpu = next((gpu for gpu in all_components['gpus'] if gpu['id'] == data.get('gpu')), None)
        if data.get('cooler'):
            selected_cooler = next((cooler for cooler in all_components['coolers'] if cooler['id'] == data.get('cooler')), None)
        if data.get('case'):
            selected_case = next((case for case in all_components['cases'] if case['id'] == data.get('case')), None)
        if data.get('psu'):
            selected_psu = next((psu for psu in all_components['psus'] if psu['id'] == data.get('psu')), None)
        
        # CPU and Motherboard socket compatibility
        if selected_cpu and selected_mb:
            if selected_cpu.get('socket') != selected_mb.get('socket'):
                errors.append(f"CPU-Socket {selected_cpu.get('socket')} ist nicht kompatibel mit Motherboard-Socket {selected_mb.get('socket')}")
        
        # RAM compatibility
        if selected_ram and selected_mb:
            ram_type = selected_ram.get('type')
            # Handle both memory_type (string) and ram_types (array) formats
            mb_memory_types = selected_mb.get('memory_type')
            mb_ram_types = selected_mb.get('ram_types', [])
            
            print(f"Debug - RAM type: {ram_type}")
            print(f"Debug - MB memory_type: {mb_memory_types}")
            print(f"Debug - MB ram_types: {mb_ram_types}")
            
            # Check compatibility with either format
            compatible = False
            if mb_memory_types and ram_type == mb_memory_types:
                compatible = True
            elif mb_ram_types and ram_type in mb_ram_types:
                compatible = True
            
            if not compatible:
                supported_types = mb_memory_types or ', '.join(mb_ram_types) if mb_ram_types else 'Unbekannt'
                errors.append(f"RAM-Typ {ram_type} ist nicht kompatibel mit Motherboard (unterstützt: {supported_types})")
        elif selected_ram and not selected_mb:
            print(f"Debug - RAM selected but no motherboard found")
            errors.append(f"Kein kompatibles Motherboard ausgewählt für RAM-Typ {selected_ram.get('type')}")
        elif not selected_ram and selected_mb:
            print(f"Debug - Motherboard selected but no RAM found")
        
        # GPU and Case compatibility
        if selected_gpu and selected_case:
            if selected_gpu.get('length', 0) > selected_case.get('max_gpu_length', 999):
                errors.append(f"GPU zu lang ({selected_gpu.get('length')}mm) für das Gehäuse (max. {selected_case.get('max_gpu_length')}mm)")
        
        # Cooler compatibility
        if selected_cooler and selected_cpu:
            compatible_sockets = selected_cooler.get('compatible_sockets', [])
            if selected_cpu.get('socket') not in compatible_sockets:
                errors.append(f"Kühler nicht kompatibel mit CPU-Socket {selected_cpu.get('socket')}")
        
        if selected_cooler and selected_case:
            if selected_cooler.get('height', 0) > selected_case.get('max_cpu_cooler_height', 999):
                errors.append(f"Kühler zu hoch ({selected_cooler.get('height')}mm) für das Gehäuse (max. {selected_case.get('max_cpu_cooler_height')}mm)")
        
        # PSU power compatibility (basic check)
        if selected_psu and selected_cpu and selected_gpu:
            estimated_power = selected_cpu.get('tdp', 0) + selected_gpu.get('power_consumption', 0) + 150  # Base system power
            if selected_psu.get('wattage', 0) < estimated_power * 1.2:  # 20% headroom
                warnings.append(f"Netzteil könnte zu schwach sein. Geschätzt: {estimated_power}W, PSU: {selected_psu.get('wattage')}W")
    
        return jsonify({
            'compatible': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
    except Exception as e:
        print(f"Compatibility validation error: {e}")
        return jsonify({
            'compatible': True,
            'errors': [],
            'warnings': ['Kompatibilitätsprüfung temporär nicht verfügbar']
        })

@app.route('/api/components/<category>')
def get_components(category):
    """Get components by category"""
    components = load_components()
    return jsonify(components.get(category, []))