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
    
    # RAM compatibility
    if selected_ram and selected_mb:
        if selected_ram['type'] != selected_mb['memory_type']:
            errors.append(f"RAM-Typ {selected_ram['type']} ist nicht kompatibel mit Motherboard ({selected_mb['memory_type']})")
    
    # GPU and Case compatibility
    if selected_gpu and selected_case:
        if selected_gpu['length'] > selected_case['max_gpu_length']:
            errors.append(f"GPU zu lang ({selected_gpu['length']}mm) für das Gehäuse (max. {selected_case['max_gpu_length']}mm)")
    
    # Cooler compatibility
    if selected_cooler and selected_cpu:
        if selected_cpu['socket'] not in selected_cooler['compatible_sockets']:
            errors.append(f"Kühler nicht kompatibel mit CPU-Socket {selected_cpu['socket']}")
    
    if selected_cooler and selected_case:
        if selected_cooler['height'] > selected_case['max_cpu_cooler_height']:
            errors.append(f"Kühler zu hoch ({selected_cooler['height']}mm) für das Gehäuse (max. {selected_case['max_cpu_cooler_height']}mm)")
    
    # PSU power compatibility (basic check)
    if selected_psu and selected_cpu and selected_gpu:
        estimated_power = selected_cpu['tdp'] + selected_gpu['power_consumption'] + 150  # Base system power
        if selected_psu['wattage'] < estimated_power * 1.2:  # 20% headroom
            warnings.append(f"Netzteil könnte zu schwach sein. Geschätzt: {estimated_power}W, PSU: {selected_psu['wattage']}W")
    
    return jsonify({
        'compatible': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    })

@app.route('/api/components/<category>')
def get_components(category):
    """Get components by category"""
    components = load_components()
    return jsonify(components.get(category, []))