import json
from datetime import datetime
from flask import request, render_template, redirect, url_for, flash, session
from flask_login import login_required, login_user, logout_user, UserMixin, current_user
from werkzeug.security import check_password_hash
from app import app, db
from models import Component, PrebuiltPC, AdminUser

# Admin Authentication
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Erfolgreich angemeldet', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Ungültige Anmeldedaten', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('Erfolgreich abgemeldet', 'info')
    return redirect(url_for('admin_login'))

# Dashboard
@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard with overview statistics"""
    component_count = Component.query.count()
    active_component_count = Component.query.filter_by(is_active=True).count()
    prebuilt_count = PrebuiltPC.query.count()
    active_prebuilt_count = PrebuiltPC.query.filter_by(is_active=True).count()
    
    # Recent components
    recent_components = Component.query.order_by(Component.created_at.desc()).limit(5).all()
    
    # Recent prebuilt PCs
    recent_prebuilts = PrebuiltPC.query.order_by(PrebuiltPC.created_at.desc()).limit(5).all()
    
    stats = {
        'component_count': component_count,
        'active_component_count': active_component_count,
        'prebuilt_count': prebuilt_count,
        'active_prebuilt_count': active_prebuilt_count
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_components=recent_components,
                         recent_prebuilts=recent_prebuilts)

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
                         current_category=category)

@app.route('/admin/components/add', methods=['GET', 'POST'])
@login_required
def admin_add_component():
    """Add new component"""
    if request.method == 'POST':
        try:
            name = request.form['name']
            category = request.form['category']
            price = float(request.form['price'])
            
            # Parse specifications JSON
            try:
                specs = json.loads(request.form['specifications'])
            except json.JSONDecodeError:
                flash('Ungültiges JSON-Format in den Spezifikationen', 'error')
                return render_template('admin/add_component.html')
            
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

# Prebuilt PC Management
@app.route('/admin/prebuilts')
@login_required
def admin_prebuilts():
    """List all prebuilt PCs"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    
    query = PrebuiltPC.query
    if category:
        query = query.filter_by(category=category)
    
    prebuilts = query.order_by(PrebuiltPC.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = ['gaming', 'workstation', 'office', 'budget']
    
    return render_template('admin/prebuilts.html', 
                         prebuilts=prebuilts, 
                         categories=categories,
                         current_category=category)

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
            
            # Parse specifications JSON
            try:
                specs = json.loads(request.form['specifications'])
            except json.JSONDecodeError:
                flash('Ungültiges JSON-Format in den Spezifikationen', 'error')
                return render_template('admin/add_prebuilt.html')
            
            # Parse features JSON
            try:
                features = json.loads(request.form['features'])
                if not isinstance(features, list):
                    raise ValueError('Features müssen als Array definiert werden')
            except (json.JSONDecodeError, ValueError) as e:
                flash(f'Ungültiges JSON-Format in den Features: {str(e)}', 'error')
                return render_template('admin/add_prebuilt.html')
            
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
    fields = {
        'cpus': ['socket', 'cores', 'threads', 'base_clock', 'boost_clock', 'tdp', 'memory_support'],
        'motherboards': ['socket', 'chipset', 'form_factor', 'memory_slots', 'max_memory', 'memory_type'],
        'ram': ['type', 'capacity', 'speed', 'timings', 'voltage'],
        'gpus': ['memory', 'memory_type', 'core_clock', 'boost_clock', 'power_consumption', 'length'],
        'ssds': ['capacity', 'interface', 'form_factor', 'read_speed', 'write_speed'],
        'cases': ['form_factor', 'max_gpu_length', 'max_cpu_cooler_height', 'front_usb'],
        'psus': ['wattage', 'efficiency', 'modular', 'form_factor'],
        'coolers': ['type', 'height', 'compatible_sockets', 'tdp_rating']
    }
    
    return {'fields': fields.get(category, [])}