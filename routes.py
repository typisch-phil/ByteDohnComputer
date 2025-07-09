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
        selected_cpu = next((cpu for cpu in components.get('cpus', []) if cpu['id'] == data.get('cpu')), None)
        selected_mb = next((mb for mb in components.get('motherboards', []) if mb['id'] == data.get('motherboard')), None)
        selected_ram = next((ram for ram in components.get('ram', []) if ram['id'] == data.get('ram')), None)
        selected_gpu = next((gpu for gpu in components.get('gpus', []) if gpu['id'] == data.get('gpu')), None)
        selected_cooler = next((cooler for cooler in components.get('coolers', []) if cooler['id'] == data.get('cooler')), None)
        selected_case = next((case for case in components.get('cases', []) if case['id'] == data.get('case')), None)
        selected_psu = next((psu for psu in components.get('psus', []) if psu['id'] == data.get('psu')), None)
        
        # CPU and Motherboard socket compatibility
        if selected_cpu and selected_mb:
            if selected_cpu.get('socket') != selected_mb.get('socket'):
                errors.append(f"CPU-Socket {selected_cpu.get('socket')} ist nicht kompatibel mit Motherboard-Socket {selected_mb.get('socket')}")
        
        # RAM compatibility
        if selected_ram and selected_mb:
            if selected_ram.get('type') != selected_mb.get('memory_type'):
                errors.append(f"RAM-Typ {selected_ram.get('type')} ist nicht kompatibel mit Motherboard ({selected_mb.get('memory_type')})")
        
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