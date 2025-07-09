// PC Configurator JavaScript

class PCConfigurator {
    constructor() {
        this.selectedComponents = {
            cpu: null,
            motherboard: null,
            ram: null,
            gpu: null,
            ssd: null,
            case: null,
            psu: null,
            cooler: null
        };
        
        this.components = {};
        this.currentStep = 1;
        this.totalSteps = 8;
        
        this.init();
    }
    
    init() {
        this.loadComponents();
        this.setupEventListeners();
        this.updateStepIndicator();
        this.updateNavigationButtons(); // Initialize navigation buttons state
    }
    
    loadComponents() {
        // Components are already loaded from the server-side template
        // This method would be used if we were fetching via AJAX
        console.log('Components loaded from server');
    }
    
    setupEventListeners() {
        // Component selection listeners
        document.addEventListener('click', (e) => {
            if (e.target.closest('.component-card')) {
                this.selectComponent(e.target.closest('.component-card'));
            }
        });
        
        // Navigation buttons
        const nextBtn = document.getElementById('next-step');
        const prevBtn = document.getElementById('prev-step');
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextStep());
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prevStep());
        }
        
        // Save configuration button
        const saveBtn = document.getElementById('save-config');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveConfiguration());
        }
    }
    
    selectComponent(card) {
        const category = card.dataset.category;
        const componentId = parseInt(card.dataset.id);
        
        // Remove previous selection
        const previousSelected = document.querySelector(`.component-card[data-category="${category}"].selected`);
        if (previousSelected) {
            previousSelected.classList.remove('selected');
        }
        
        // Add new selection
        card.classList.add('selected');
        this.selectedComponents[category] = componentId;
        
        // Validate compatibility
        this.validateCompatibility();
        
        // Update step indicator and navigation
        this.updateStepIndicator();
        this.updateNavigationButtons();
    }
    
    async validateCompatibility() {
        const statusDiv = document.getElementById('compatibility-status');
        if (!statusDiv) return;
        
        // Show loading
        statusDiv.innerHTML = '<div class="text-center"><div class="loading"></div> Überprüfe Kompatibilität...</div>';
        
        try {
            const response = await fetch('/api/validate-compatibility', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.selectedComponents)
            });
            
            const result = await response.json();
            this.displayCompatibilityResults(result);
        } catch (error) {
            console.error('Compatibility validation error:', error);
            statusDiv.innerHTML = '<div class="alert alert-danger">Fehler bei der Kompatibilitätsprüfung</div>';
        }
    }
    
    displayCompatibilityResults(result) {
        const statusDiv = document.getElementById('compatibility-status');
        let html = '<h4>Kompatibilitätsstatus</h4>';
        
        if (result.compatible) {
            html += '<div class="alert alert-success"><i class="fas fa-check-circle"></i> Konfiguration ist kompatibel!</div>';
        } else {
            html += '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> Kompatibilitätsprobleme gefunden!</div>';
        }
        
        // Display errors
        if (result.errors && result.errors.length > 0) {
            html += '<div class="mt-3"><strong>Fehler:</strong>';
            result.errors.forEach(error => {
                html += `<div class="status-item"><span class="status-icon status-error"><i class="fas fa-times-circle"></i></span>${error}</div>`;
            });
            html += '</div>';
        }
        
        // Display warnings
        if (result.warnings && result.warnings.length > 0) {
            html += '<div class="mt-3"><strong>Warnungen:</strong>';
            result.warnings.forEach(warning => {
                html += `<div class="status-item"><span class="status-icon status-warning"><i class="fas fa-exclamation-circle"></i></span>${warning}</div>`;
            });
            html += '</div>';
        }
        
        // Display price and power consumption
        if (result.total_price > 0) {
            html += `
                <div class="price-summary">
                    <div class="total-price">Gesamtpreis: €${result.total_price.toFixed(2)}</div>
                    <div class="text-center mt-2">
                        <small>Geschätzter Stromverbrauch: ${result.total_wattage}W</small>
                    </div>
                </div>
            `;
        }
        
        statusDiv.innerHTML = html;
    }
    
    updateStepIndicator() {
        const steps = document.querySelectorAll('.step');
        const componentCategories = ['cpu', 'motherboard', 'ram', 'gpu', 'ssd', 'case', 'psu', 'cooler'];
        
        steps.forEach((step, index) => {
            const category = componentCategories[index];
            step.classList.remove('active', 'completed');
            
            if (this.selectedComponents[category]) {
                step.classList.add('completed');
            } else if (index === this.currentStep - 1) {
                step.classList.add('active');
            }
        });
    }
    
    nextStep() {
        // Check if current step has a selection before proceeding
        const componentCategories = ['cpu', 'motherboard', 'ram', 'gpu', 'ssd', 'case', 'psu', 'cooler'];
        const currentCategory = componentCategories[this.currentStep - 1];
        
        if (!this.selectedComponents[currentCategory]) {
            alert(`Bitte wählen Sie eine ${this.getCategoryDisplayName(currentCategory)} aus, bevor Sie fortfahren.`);
            return;
        }
        
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.showStep(this.currentStep);
        }
    }
    
    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.showStep(this.currentStep);
        }
    }
    
    showStep(step) {
        // Hide all component sections
        document.querySelectorAll('.component-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show current step section
        const currentSection = document.getElementById(`step-${step}`);
        if (currentSection) {
            currentSection.style.display = 'block';
        }
        
        this.updateStepIndicator();
        
        // Update navigation buttons
        this.updateNavigationButtons();
    }
    
    updateNavigationButtons() {
        const nextBtn = document.getElementById('next-step');
        const prevBtn = document.getElementById('prev-step');
        
        if (prevBtn) {
            prevBtn.style.display = this.currentStep > 1 ? 'inline-block' : 'none';
        }
        
        if (nextBtn) {
            const componentCategories = ['cpu', 'motherboard', 'ram', 'gpu', 'ssd', 'case', 'psu', 'cooler'];
            const currentCategory = componentCategories[this.currentStep - 1];
            const hasSelection = this.selectedComponents[currentCategory] !== null;
            
            // Enable/disable next button based on selection
            nextBtn.disabled = !hasSelection;
            
            if (this.currentStep === this.totalSteps) {
                nextBtn.textContent = 'Konfiguration abschließen';
                nextBtn.classList.remove('btn-primary');
                nextBtn.classList.add('btn-success');
            } else {
                nextBtn.textContent = 'Weiter';
                nextBtn.classList.remove('btn-success');
                nextBtn.classList.add('btn-primary');
            }
            
            // Visual feedback for disabled state
            if (!hasSelection) {
                nextBtn.style.opacity = '0.5';
                nextBtn.style.cursor = 'not-allowed';
            } else {
                nextBtn.style.opacity = '1';
                nextBtn.style.cursor = 'pointer';
            }
        }
    }
    
    getCategoryDisplayName(category) {
        const displayNames = {
            'cpu': 'CPU',
            'motherboard': 'Motherboard',
            'ram': 'RAM',
            'gpu': 'Grafikkarte',
            'ssd': 'SSD',
            'case': 'Gehäuse',
            'psu': 'Netzteil',
            'cooler': 'Kühler'
        };
        return displayNames[category] || category;
    }

    saveConfiguration() {
        const selectedCount = Object.values(this.selectedComponents).filter(c => c !== null).length;
        
        if (selectedCount === 0) {
            alert('Bitte wählen Sie mindestens eine Komponente aus.');
            return;
        }
        
        // Create configuration summary
        const configName = prompt('Geben Sie einen Namen für Ihre Konfiguration ein:');
        if (!configName) return;
        
        const configData = {
            name: configName,
            components: this.selectedComponents,
            timestamp: new Date().toISOString()
        };
        
        // Save to localStorage for now (in production, this would be sent to server)
        const savedConfigs = JSON.parse(localStorage.getItem('savedConfigurations') || '[]');
        savedConfigs.push(configData);
        localStorage.setItem('savedConfigurations', JSON.stringify(savedConfigs));
        
        alert('Konfiguration erfolgreich gespeichert!');
    }
    
    loadConfiguration(config) {
        this.selectedComponents = config.components;
        
        // Update UI to reflect loaded configuration
        Object.keys(this.selectedComponents).forEach(category => {
            const componentId = this.selectedComponents[category];
            if (componentId) {
                const card = document.querySelector(`.component-card[data-category="${category}"][data-id="${componentId}"]`);
                if (card) {
                    card.classList.add('selected');
                }
            }
        });
        
        this.validateCompatibility();
        this.updateStepIndicator();
    }
    
    resetConfiguration() {
        // Clear all selections
        Object.keys(this.selectedComponents).forEach(key => {
            this.selectedComponents[key] = null;
        });
        
        // Remove visual selections
        document.querySelectorAll('.component-card.selected').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Reset step indicator
        this.currentStep = 1;
        this.updateStepIndicator();
        
        // Clear compatibility status
        const statusDiv = document.getElementById('compatibility-status');
        if (statusDiv) {
            statusDiv.innerHTML = '<p>Wählen Sie Komponenten aus, um die Kompatibilität zu überprüfen.</p>';
        }
    }
}

// Initialize configurator when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('pc-configurator')) {
        window.configurator = new PCConfigurator();
    }
});

// Utility functions
function formatPrice(price) {
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
    }).format(price);
}

function formatSpecs(specs) {
    // Format component specifications for display
    return Object.entries(specs)
        .map(([key, value]) => `${key}: ${value}`)
        .join(' • ');
}

// Export configuration as JSON
function exportConfiguration() {
    if (window.configurator) {
        const config = {
            components: window.configurator.selectedComponents,
            timestamp: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(config, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = 'pc-configuration.json';
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }
}

// Import configuration from JSON
function importConfiguration() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const config = JSON.parse(e.target.result);
                    if (window.configurator && config.components) {
                        window.configurator.loadConfiguration(config);
                    }
                } catch (error) {
                    alert('Fehler beim Laden der Konfiguration: ' + error.message);
                }
            };
            reader.readAsText(file);
        }
    };
    
    input.click();
}
