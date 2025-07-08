from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import AdminUser, Component, PrebuiltPC
import json

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with overview statistics"""
    component_count = Component.query.count()
    prebuilt_count = PrebuiltPC.query.count()
    active_components = Component.query.filter_by(is_active=True).count()
    active_prebuilts = PrebuiltPC.query.filter_by(is_active=True).count()
    
    stats = {
        'components': {
            'total': component_count,
            'active': active_components,
            'inactive': component_count - active_components
        },
        'prebuilts': {
            'total': prebuilt_count,
            'active': active_prebuilts,
            'inactive': prebuilt_count - active_prebuilts
        }
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
        else:
            flash('Ungültige Anmeldedaten', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('Erfolgreich abgemeldet', 'success')
    return redirect(url_for('index'))

# Component Management
@app.route('/admin/components')
@login_required
def admin_components():
    """List all components"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    
    query = Component.query
    if category:
        query = query.filter_by(category=category)
    
    components = query.order_by(Component.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = ['cpus', 'motherboards', 'ram', 'gpus', 'ssds', 'cases', 'psus', 'coolers']
    
    return render_template('admin/components.html', 
                         components=components, 
                         categories=categories,
                         selected_category=category)

@app.route('/admin/components/add', methods=['GET', 'POST'])
@login_required
def admin_add_component():
    """Add new component"""
    if request.method == 'POST':
        try:
            # Get basic info
            name = request.form['name']
            category = request.form['category']
            price = float(request.form['price'])
            
            # Build specifications based on category
            specs = {}
            
            if category == 'cpus':
                specs = {
                    'socket': request.form['socket'],
                    'cores': int(request.form['cores']),
                    'threads': int(request.form['threads']),
                    'base_clock': float(request.form['base_clock']),
                    'boost_clock': float(request.form['boost_clock']),
                    'tdp': int(request.form['tdp']),
                    'memory_support': request.form['memory_support']
                }
            elif category == 'motherboards':
                specs = {
                    'socket': request.form['socket'],
                    'chipset': request.form['chipset'],
                    'ram_slots': int(request.form['ram_slots']),
                    'ram_types': request.form['ram_types'].split(','),
                    'max_ram_speed': int(request.form['max_ram_speed']),
                    'max_ram_capacity': int(request.form['max_ram_capacity']),
                    'form_factor': request.form['form_factor'],
                    'power_consumption': int(request.form['power_consumption'])
                }
            elif category == 'ram':
                specs = {
                    'type': request.form['type'],
                    'capacity': int(request.form['capacity']),
                    'speed': int(request.form['speed']),
                    'modules': int(request.form['modules']),
                    'latency': request.form['latency'],
                    'power_consumption': int(request.form['power_consumption'])
                }
            elif category == 'gpus':
                specs = {
                    'memory': int(request.form['memory']),
                    'memory_type': request.form['memory_type'],
                    'base_clock': int(request.form['base_clock']),
                    'boost_clock': int(request.form['boost_clock']),
                    'power_consumption': int(request.form['power_consumption']),
                    'length': int(request.form['length']),
                    'width': int(request.form['width']),
                    'height': int(request.form['height'])
                }
            elif category == 'ssds':
                specs = {
                    'capacity': int(request.form['capacity']),
                    'interface': request.form['interface'],
                    'form_factor': request.form['form_factor'],
                    'read_speed': int(request.form['read_speed']),
                    'write_speed': int(request.form['write_speed'])
                }
            elif category == 'cases':
                specs = {
                    'form_factor': request.form['form_factor'],
                    'max_gpu_length': int(request.form['max_gpu_length']),
                    'max_cooler_height': int(request.form['max_cooler_height']),
                    'dimensions': {
                        'length': int(request.form['length']),
                        'width': int(request.form['width']),
                        'height': int(request.form['height'])
                    }
                }
            elif category == 'psus':
                specs = {
                    'wattage': int(request.form['wattage']),
                    'efficiency': request.form['efficiency'],
                    'modular': request.form.get('modular') == 'on',
                    'form_factor': request.form['form_factor']
                }
            elif category == 'coolers':
                compatible_sockets = request.form['compatible_sockets'].split(',')
                specs = {
                    'type': request.form['type'],
                    'height': int(request.form['height']),
                    'compatible_sockets': [s.strip() for s in compatible_sockets],
                    'tdp_rating': int(request.form['tdp_rating'])
                }
            
            component = Component(
                name=name,
                category=category,
                price=price,
                specifications=json.dumps(specs)
            )
            
            db.session.add(component)
            db.session.commit()
            
            flash(f'Komponente "{name}" erfolgreich hinzugefügt', 'success')
            return redirect(url_for('admin_components'))
            
        except Exception as e:
            flash(f'Fehler beim Hinzufügen der Komponente: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/add_component.html')

@app.route('/admin/components/<int:component_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_component(component_id):
    """Edit existing component"""
    component = Component.query.get_or_404(component_id)
    
    if request.method == 'POST':
        try:
            component.name = request.form['name']
            component.category = request.form['category']
            component.price = float(request.form['price'])
            component.is_active = bool(int(request.form.get('is_active', 1)))
            
            # Parse and validate specifications JSON
            try:
                specs = json.loads(request.form['specifications'])
                component.set_specs(specs)
            except json.JSONDecodeError:
                flash('Ungültiges JSON-Format in den Spezifikationen', 'error')
                return render_template('admin/edit_component.html', component=component)
            
            db.session.commit()
            flash(f'Komponente "{component.name}" erfolgreich aktualisiert', 'success')
            return redirect(url_for('admin_components'))
            
        except Exception as e:
            flash(f'Fehler beim Aktualisieren der Komponente: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_component.html', component=component)

@app.route('/admin/components/<int:component_id>/delete', methods=['POST'])
@login_required 
def admin_delete_component(component_id):
    """Delete component"""
    component = Component.query.get_or_404(component_id)
    
    try:
        db.session.delete(component)
        db.session.commit()
        flash(f'Komponente "{component.name}" erfolgreich gelöscht', 'success')
    except Exception as e:
        flash(f'Fehler beim Löschen der Komponente: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_components'))

# Prebuilt PCs
@app.route('/admin/prebuilts')
@login_required
def admin_prebuilts():
    """List all prebuilt PCs"""
    prebuilts = PrebuiltPC.query.order_by(PrebuiltPC.created_at.desc()).all()
    return render_template('admin/prebuilts.html', prebuilts=prebuilts)

@app.route('/admin/prebuilts/add', methods=['GET', 'POST'])
@login_required
def admin_add_prebuilt():
    """Add new prebuilt PC"""
    if request.method == 'POST':
        try:
            name = request.form['name']
            price = float(request.form['price'])
            category = request.form['category']
            description = request.form['description']
            image_url = request.form.get('image_url')
            
            # Create specifications dictionary
            specs = {
                'cpu': request.form['cpu'],
                'gpu': request.form['gpu'],
                'ram': request.form['ram'],
                'storage': request.form['storage'],
                'motherboard': request.form['motherboard'],
                'cooler': request.form['cooler'],
                'case': request.form['case'],
                'psu': request.form['psu']
            }
            
            # Parse features from textarea
            features_text = request.form['features']
            features = [f.strip() for f in features_text.split('\n') if f.strip()]
            
            prebuilt = PrebuiltPC(
                name=name,
                price=price,
                category=category,
                description=description,
                image_url=image_url if image_url else None,
                specifications=json.dumps(specs),
                features=json.dumps(features)
            )
            
            db.session.add(prebuilt)
            db.session.commit()
            
            flash(f'Fertig-PC "{name}" erfolgreich hinzugefügt', 'success')
            return redirect(url_for('admin_prebuilts'))
            
        except Exception as e:
            flash(f'Fehler beim Hinzufügen des Fertig-PCs: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/add_prebuilt.html')

@app.route('/admin/prebuilts/<int:prebuilt_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_prebuilt(prebuilt_id):
    """Edit existing prebuilt PC"""
    prebuilt = PrebuiltPC.query.get_or_404(prebuilt_id)
    
    if request.method == 'POST':
        try:
            prebuilt.name = request.form['name']
            prebuilt.price = float(request.form['price'])
            prebuilt.category = request.form['category']
            prebuilt.description = request.form['description']
            prebuilt.image_url = request.form.get('image_url') or None
            prebuilt.is_active = bool(int(request.form.get('is_active', 1)))
            
            # Parse and validate specifications JSON
            try:
                specs = json.loads(request.form['specifications'])
                prebuilt.set_specs(specs)
            except json.JSONDecodeError:
                flash('Ungültiges JSON-Format in den Spezifikationen', 'error')
                return render_template('admin/edit_prebuilt.html', prebuilt=prebuilt)
            
            # Parse and validate features JSON
            try:
                features = json.loads(request.form['features'])
                if not isinstance(features, list):
                    raise ValueError('Features müssen als Array definiert werden')
                prebuilt.set_features(features)
            except (json.JSONDecodeError, ValueError) as e:
                flash(f'Ungültiges JSON-Format in den Features: {str(e)}', 'error')
                return render_template('admin/edit_prebuilt.html', prebuilt=prebuilt)
            
            db.session.commit()
            
            flash(f'Fertig-PC "{prebuilt.name}" erfolgreich aktualisiert', 'success')
            return redirect(url_for('admin_prebuilts'))
            
        except Exception as e:
            flash(f'Fehler beim Aktualisieren des Fertig-PCs: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_prebuilt.html', prebuilt=prebuilt)

@app.route('/admin/prebuilts/<int:prebuilt_id>/delete', methods=['POST'])
@login_required
def admin_delete_prebuilt(prebuilt_id):
    """Delete prebuilt PC"""
    prebuilt = PrebuiltPC.query.get_or_404(prebuilt_id)
    
    try:
        db.session.delete(prebuilt)
        db.session.commit()
        flash(f'Fertig-PC "{prebuilt.name}" erfolgreich gelöscht', 'success')
    except Exception as e:
        flash(f'Fehler beim Löschen des Fertig-PCs: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_prebuilts'))

# API endpoints for dynamic forms
@app.route('/admin/api/component-fields/<category>')
@login_required
def get_component_fields(category): 
                         prebuilts=prebuilts,
                         categories=categories,
                         selected_category=category)

@app.route('/admin/prebuilts/add', methods=['GET', 'POST'])
@login_required
def admin_add_prebuilt():
    """Add new prebuilt PC"""
    if request.method == 'POST':
        try:
            name = request.form['name']
            price = float(request.form['price'])
            category = request.form['category']
            description = request.form['description']
            image_url = request.form['image_url']
            
            # Build specifications
            specs = {
                'cpu': request.form['cpu'],
                'gpu': request.form['gpu'],
                'ram': request.form['ram'],
                'storage': request.form['storage'],
                'motherboard': request.form['motherboard'],
                'cooler': request.form['cooler'],
                'case': request.form['case'],
                'psu': request.form['psu']
            }
            
            # Build features list
            features_text = request.form['features']
            features = [f.strip() for f in features_text.split('\n') if f.strip()]
            
            prebuilt = PrebuiltPC(
                name=name,
                price=price,
                category=category,
                description=description,
                image_url=image_url if image_url else None,
                specifications=json.dumps(specs),
                features=json.dumps(features)
            )
            
            db.session.add(prebuilt)
            db.session.commit()
            
            flash(f'Fertig-PC "{name}" erfolgreich hinzugefügt', 'success')
            return redirect(url_for('admin_prebuilts'))
            
        except Exception as e:
            flash(f'Fehler beim Hinzufügen des Fertig-PCs: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/add_prebuilt.html')

@app.route('/admin/prebuilts/<int:prebuilt_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_prebuilt(prebuilt_id):
    """Edit existing prebuilt PC"""
    prebuilt = PrebuiltPC.query.get_or_404(prebuilt_id)
    
    if request.method == 'POST':
        try:
            prebuilt.name = request.form['name']
            prebuilt.price = float(request.form['price'])
            prebuilt.category = request.form['category']
            prebuilt.description = request.form['description']
            prebuilt.image_url = request.form.get('image_url') or None
            prebuilt.is_active = bool(int(request.form.get('is_active', 1)))
            
            # Parse and validate specifications JSON
            try:
                specs = json.loads(request.form['specifications'])
                prebuilt.set_specs(specs)
            except json.JSONDecodeError:
                flash('Ungültiges JSON-Format in den Spezifikationen', 'error')
                return render_template('admin/edit_prebuilt.html', prebuilt=prebuilt)
            
            # Parse and validate features JSON
            try:
                features = json.loads(request.form['features'])
                if not isinstance(features, list):
                    raise ValueError('Features müssen als Array definiert werden')
                prebuilt.set_features(features)
            except (json.JSONDecodeError, ValueError) as e:
                flash(f'Ungültiges JSON-Format in den Features: {str(e)}', 'error')
                return render_template('admin/edit_prebuilt.html', prebuilt=prebuilt)
            
            db.session.commit()
            
            flash(f'Fertig-PC "{prebuilt.name}" erfolgreich aktualisiert', 'success')
            return redirect(url_for('admin_prebuilts'))
            
        except Exception as e:
            flash(f'Fehler beim Aktualisieren des Fertig-PCs: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_prebuilt.html', prebuilt=prebuilt)

@app.route('/admin/prebuilts/<int:prebuilt_id>/delete', methods=['POST'])
@login_required
def admin_delete_prebuilt(prebuilt_id):
    """Delete prebuilt PC"""
    prebuilt = PrebuiltPC.query.get_or_404(prebuilt_id)
    
    try:
        db.session.delete(prebuilt)
        db.session.commit()
        flash(f'Fertig-PC "{prebuilt.name}" erfolgreich gelöscht', 'success')
    except Exception as e:
        flash(f'Fehler beim Löschen des Fertig-PCs: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_prebuilts'))

# API endpoints for dynamic forms
@app.route('/admin/api/component-fields/<category>')
@login_required
def get_component_fields(category):
    """Get form fields for specific component category"""
    fields = {}
    
    if category == 'cpus':
        fields = {
            'socket': {'type': 'text', 'label': 'Socket', 'required': True},
            'cores': {'type': 'number', 'label': 'Kerne', 'required': True},
            'threads': {'type': 'number', 'label': 'Threads', 'required': True},
            'base_clock': {'type': 'number', 'label': 'Basistakt (GHz)', 'step': '0.1', 'required': True},
            'boost_clock': {'type': 'number', 'label': 'Boost-Takt (GHz)', 'step': '0.1', 'required': True},
            'tdp': {'type': 'number', 'label': 'TDP (W)', 'required': True},
            'memory_support': {'type': 'text', 'label': 'Speicher-Unterstützung', 'required': True}
        }
    elif category == 'motherboards':
        fields = {
            'socket': {'type': 'text', 'label': 'Socket', 'required': True},
            'chipset': {'type': 'text', 'label': 'Chipsatz', 'required': True},
            'ram_slots': {'type': 'number', 'label': 'RAM-Slots', 'required': True},
            'ram_types': {'type': 'text', 'label': 'RAM-Typen (kommagetrennt)', 'required': True},
            'max_ram_speed': {'type': 'number', 'label': 'Max. RAM-Geschwindigkeit (MHz)', 'required': True},
            'max_ram_capacity': {'type': 'number', 'label': 'Max. RAM-Kapazität (GB)', 'required': True},
            'form_factor': {'type': 'text', 'label': 'Formfaktor', 'required': True},
            'power_consumption': {'type': 'number', 'label': 'Stromverbrauch (W)', 'required': True}
        }
    # Add other categories...
    
    return jsonify(fields)