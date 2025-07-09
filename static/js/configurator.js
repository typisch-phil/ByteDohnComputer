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
        this.updateNavigationButtons();
    }
    
    loadComponents() {
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
        
        // Filter and search listeners
        this.setupFilterListeners();
    }
    
    setupFilterListeners() {
        // CPU filters
        this.setupCategoryFilters('cpu', [
            'search-cpu',
            'filter-cpu-socket', 
            'filter-cpu-cores',
            'sort-cpu'
        ]);
        
        // Motherboard filters
        this.setupCategoryFilters('motherboard', [
            'search-motherboard',
            'filter-mb-socket',
            'filter-mb-form-factor',
            'sort-motherboard'
        ]);
        
        // RAM filters
        this.setupCategoryFilters('ram', [
            'search-ram',
            'filter-ram-type',
            'filter-ram-capacity',
            'sort-ram'
        ]);
        
        // GPU filters
        this.setupCategoryFilters('gpu', [
            'search-gpu',
            'filter-gpu-memory',
            'filter-gpu-brand',
            'sort-gpu'
        ]);
        
        // SSD filters
        this.setupCategoryFilters('ssd', [
            'search-ssd',
            'filter-ssd-capacity',
            'filter-ssd-interface',
            'sort-ssd'
        ]);
        
        // Case filters
        this.setupCategoryFilters('case', [
            'search-case',
            'filter-case-form-factor',
            'filter-case-size',
            'sort-case'
        ]);
        
        // PSU filters
        this.setupCategoryFilters('psu', [
            'search-psu',
            'filter-psu-wattage',
            'filter-psu-efficiency',
            'sort-psu'
        ]);
        
        // Cooler filters
        this.setupCategoryFilters('cooler', [
            'search-cooler',
            'filter-cooler-type',
            'filter-cooler-socket',
            'sort-cooler'
        ]);
    }
    
    setupCategoryFilters(category, filterIds) {
        filterIds.forEach(filterId => {
            const element = document.getElementById(filterId);
            if (element) {
                const eventType = filterId.startsWith('search-') ? 'input' : 'change';
                element.addEventListener(eventType, () => {
                    console.log(`Filter changed: ${filterId} for category ${category}`);
                    this.applyFilters(category);
                });
                console.log(`Added event listener for ${filterId}`);
            } else {
                console.warn(`Filter element not found: ${filterId}`);
            }
        });
    }
    
    applyFilters(category) {
        console.log(`Applying filters for category: ${category}`);
        
        // Find the correct container for the category
        const container = document.querySelector(`#${category}-list`) || 
                         document.querySelector(`#step-${this.getCategoryStep(category)} .component-selection`);
        
        if (!container) {
            console.error(`Container not found for category: ${category}`);
            return;
        }
        
        const cards = container.querySelectorAll(`.component-card[data-category="${category}"]`);
        console.log(`Found ${cards.length} cards for category ${category}`);
        
        if (cards.length === 0) {
            console.warn(`No cards found for category ${category}`);
            return;
        }
        
        const searchTerm = this.getFilterValue(`search-${category}`);
        console.log(`Search term: "${searchTerm}"`);
        
        let filteredCards = Array.from(cards);
        
        // Apply search filter
        if (searchTerm && searchTerm.trim() !== '') {
            filteredCards = filteredCards.filter(card => {
                const nameEl = card.querySelector('.component-name');
                const specsEl = card.querySelector('.component-specs');
                const name = nameEl ? nameEl.textContent.toLowerCase() : '';
                const specs = specsEl ? specsEl.textContent.toLowerCase() : '';
                const searchLower = searchTerm.toLowerCase().trim();
                const matches = name.includes(searchLower) || specs.includes(searchLower);
                console.log(`Card "${name}" matches "${searchTerm}": ${matches}`);
                return matches;
            });
        }
        
        // Apply category-specific filters
        filteredCards = this.applyCategoryFilters(category, filteredCards);
        
        // Apply sorting
        filteredCards = this.applySorting(category, filteredCards);
        
        // Show/hide cards
        cards.forEach(card => {
            if (filteredCards.includes(card)) {
                card.classList.remove('hidden');
                card.style.display = '';
            } else {
                card.classList.add('hidden');
                card.style.display = 'none';
            }
        });
        
        console.log(`Filtered to ${filteredCards.length} cards`);
        
        // Show no results message if needed
        this.showNoResultsMessage(category, filteredCards.length === 0);
    }
    
    getCategoryStep(category) {
        const categorySteps = {
            'cpu': 1,
            'motherboard': 2,
            'ram': 3,
            'gpu': 4,
            'ssd': 5,
            'case': 6,
            'psu': 7,
            'cooler': 8
        };
        return categorySteps[category] || 1;
    }
    
    applyCategoryFilters(category, cards) {
        if (category === 'cpu') {
            const socket = this.getFilterValue('filter-cpu-socket');
            const cores = this.getFilterValue('filter-cpu-cores');
            
            return cards.filter(card => {
                const specsEl = card.querySelector('.component-specs');
                const specs = specsEl ? specsEl.textContent : '';
                
                if (socket && !specs.includes(`Socket ${socket}`)) return false;
                
                if (cores) {
                    const coresMatch = specs.match(/(\d+) Kerne/);
                    if (coresMatch) {
                        const cardCores = parseInt(coresMatch[1]);
                        if (cores === '12' && cardCores < 12) return false;
                        if (cores !== '12' && cardCores !== parseInt(cores)) return false;
                    }
                }
                
                return true;
            });
        }
        
        if (category === 'motherboard') {
            const socket = this.getFilterValue('filter-mb-socket');
            const formFactor = this.getFilterValue('filter-mb-form-factor');
            
            return cards.filter(card => {
                const specsEl = card.querySelector('.component-specs');
                const specs = specsEl ? specsEl.textContent : '';
                
                if (socket && !specs.includes(`Socket ${socket}`)) return false;
                if (formFactor && !specs.includes(formFactor)) return false;
                
                return true;
            });
        }
        
        if (category === 'ram') {
            const type = this.getFilterValue('filter-ram-type');
            const capacity = this.getFilterValue('filter-ram-capacity');
            
            return cards.filter(card => {
                const specsEl = card.querySelector('.component-specs');
                const specs = specsEl ? specsEl.textContent : '';
                
                if (type && !specs.includes(type)) return false;
                
                if (capacity) {
                    const capacityMatch = specs.match(/(\d+)GB/);
                    if (capacityMatch && parseInt(capacityMatch[1]) !== parseInt(capacity)) return false;
                }
                
                return true;
            });
        }
        
        if (category === 'gpu') {
            const memory = this.getFilterValue('filter-gpu-memory');
            const brand = this.getFilterValue('filter-gpu-brand');
            
            return cards.filter(card => {
                const nameEl = card.querySelector('.component-name');
                const specsEl = card.querySelector('.component-specs');
                const name = nameEl ? nameEl.textContent : '';
                const specs = specsEl ? specsEl.textContent : '';
                
                if (memory) {
                    const memoryMatch = specs.match(/(\d+)GB/);
                    if (memoryMatch && parseInt(memoryMatch[1]) < parseInt(memory)) return false;
                }
                
                if (brand && !name.includes(brand)) return false;
                
                return true;
            });
        }
        
        if (category === 'ssd') {
            const capacity = this.getFilterValue('filter-ssd-capacity');
            const interfaceType = this.getFilterValue('filter-ssd-interface');
            
            return cards.filter(card => {
                const specsEl = card.querySelector('.component-specs');
                const specs = specsEl ? specsEl.textContent : '';
                
                if (capacity) {
                    const capacityMatch = specs.match(/(\d+)GB/);
                    if (capacityMatch && parseInt(capacityMatch[1]) < parseInt(capacity)) return false;
                }
                
                if (interfaceType && !specs.includes(interfaceType)) return false;
                
                return true;
            });
        }
        
        if (category === 'case') {
            const formFactor = this.getFilterValue('filter-case-form-factor');
            const size = this.getFilterValue('filter-case-size');
            
            return cards.filter(card => {
                const specsEl = card.querySelector('.component-specs');
                const specs = specsEl ? specsEl.textContent : '';
                
                if (formFactor && !specs.includes(formFactor)) return false;
                if (size && !specs.includes(size)) return false;
                
                return true;
            });
        }
        
        if (category === 'psu') {
            const wattage = this.getFilterValue('filter-psu-wattage');
            const efficiency = this.getFilterValue('filter-psu-efficiency');
            
            return cards.filter(card => {
                const specsEl = card.querySelector('.component-specs');
                const specs = specsEl ? specsEl.textContent : '';
                
                if (wattage) {
                    const wattageMatch = specs.match(/(\d+)W/);
                    if (wattageMatch && parseInt(wattageMatch[1]) < parseInt(wattage)) return false;
                }
                
                if (efficiency && !specs.includes(efficiency)) return false;
                
                return true;
            });
        }
        
        if (category === 'cooler') {
            const type = this.getFilterValue('filter-cooler-type');
            const socket = this.getFilterValue('filter-cooler-socket');
            
            return cards.filter(card => {
                const specsEl = card.querySelector('.component-specs');
                const specs = specsEl ? specsEl.textContent : '';
                
                if (type && !specs.includes(type)) return false;
                if (socket && !specs.includes(socket)) return false;
                
                return true;
            });
        }
        
        return cards;
    }
    
    applySorting(category, cards) {
        const sortValue = this.getFilterValue(`sort-${category}`);
        
        return cards.sort((a, b) => {
            if (sortValue === 'name') {
                const nameA = a.querySelector('.component-name').textContent;
                const nameB = b.querySelector('.component-name').textContent;
                return nameA.localeCompare(nameB);
            }
            
            if (sortValue === 'price-asc' || sortValue === 'price-desc') {
                const priceA = this.extractPrice(a.querySelector('.component-price').textContent);
                const priceB = this.extractPrice(b.querySelector('.component-price').textContent);
                return sortValue === 'price-asc' ? priceA - priceB : priceB - priceA;
            }
            
            return 0;
        });
    }
    
    getFilterValue(filterId) {
        const element = document.getElementById(filterId);
        return element ? element.value.trim() : '';
    }
    
    extractPrice(priceText) {
        const match = priceText.match(/€([\d,\.]+)/);
        return match ? parseFloat(match[1].replace(',', '.')) : 0;
    }
    
    showNoResultsMessage(category, show) {
        const container = document.querySelector(`#${category}-list`) || 
                        document.querySelector(`#step-${this.getCategoryStep(category)} .component-selection`);
        
        let noResultsDiv = container ? container.querySelector('.no-results') : null;
        
        if (show && !noResultsDiv && container) {
            noResultsDiv = document.createElement('div');
            noResultsDiv.className = 'no-results text-center py-4';
            noResultsDiv.innerHTML = `
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5>Keine Komponenten gefunden</h5>
                <p class="text-muted">Versuchen Sie andere Suchbegriffe oder setzen Sie die Filter zurück.</p>
            `;
            container.appendChild(noResultsDiv);
        } else if (!show && noResultsDiv) {
            noResultsDiv.remove();
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
        
        statusDiv.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Überprüfe Kompatibilität...</div>';
        
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
            console.error('Compatibility check failed:', error);
            statusDiv.innerHTML = '<div class="alert alert-warning">Kompatibilitätsprüfung nicht verfügbar</div>';
        }
    }
    
    displayCompatibilityResults(result) {
        const statusDiv = document.getElementById('compatibility-status');
        if (!statusDiv) return;
        
        let html = '<h4>Kompatibilitätsstatus</h4>';
        
        if (result.compatible) {
            html += '<div class="alert alert-success"><i class="fas fa-check"></i> Alle Komponenten sind kompatibel!</div>';
        } else {
            html += '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> Kompatibilitätsprobleme gefunden:</div>';
            result.issues.forEach(issue => {
                html += `<div class="alert alert-warning">${issue}</div>`;
            });
        }
        
        statusDiv.innerHTML = html;
    }
    
    updateStepIndicator() {
        for (let i = 1; i <= this.totalSteps; i++) {
            const indicator = document.querySelector(`.step-indicator .step:nth-child(${i})`);
            if (indicator) {
                indicator.classList.toggle('active', i === this.currentStep);
                indicator.classList.toggle('completed', i < this.currentStep);
            }
        }
    }
    
    nextStep() {
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.showStep(this.currentStep);
            this.updateStepIndicator();
            this.updateNavigationButtons();
        }
    }
    
    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.showStep(this.currentStep);
            this.updateStepIndicator();
            this.updateNavigationButtons();
        }
    }
    
    showStep(step) {
        for (let i = 1; i <= this.totalSteps; i++) {
            const stepDiv = document.getElementById(`step-${i}`);
            if (stepDiv) {
                stepDiv.style.display = i === step ? 'block' : 'none';
            }
        }
    }
    
    updateNavigationButtons() {
        const nextBtn = document.getElementById('next-step');
        const prevBtn = document.getElementById('prev-step');
        
        if (prevBtn) {
            prevBtn.style.display = this.currentStep > 1 ? 'inline-block' : 'none';
        }
        
        if (nextBtn) {
            if (this.currentStep === this.totalSteps) {
                nextBtn.textContent = 'Konfiguration abschließen';
                nextBtn.innerHTML = '<i class="fas fa-check"></i> Abschließen';
            } else {
                nextBtn.innerHTML = 'Weiter <i class="fas fa-arrow-right"></i>';
            }
        }
    }
    
    getCategoryDisplayName(category) {
        const names = {
            cpu: 'CPU',
            motherboard: 'Motherboard',
            ram: 'RAM',
            gpu: 'GPU',
            ssd: 'SSD',
            case: 'Gehäuse',
            psu: 'Netzteil',
            cooler: 'Kühler'
        };
        return names[category] || category;
    }
    
    saveConfiguration() {
        const configData = {
            name: prompt('Name für die Konfiguration:') || 'Meine PC-Konfiguration',
            components: this.selectedComponents,
            totalPrice: this.calculateTotalPrice()
        };
        
        fetch('/api/save-configuration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(configData)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Konfiguration erfolgreich gespeichert!');
            } else {
                alert('Fehler beim Speichern der Konfiguration.');
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            alert('Fehler beim Speichern der Konfiguration.');
        });
    }
    
    calculateTotalPrice() {
        let total = 0;
        // This would calculate based on selected components
        // Implementation depends on how component data is structured
        return total;
    }
    
    loadConfiguration(config) {
        this.selectedComponents = config.components;
        this.updateStepIndicator();
        this.updateNavigationButtons();
        this.validateCompatibility();
    }
    
    resetConfiguration() {
        if (confirm('Sind Sie sicher, dass Sie die Konfiguration zurücksetzen möchten?')) {
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
            
            // Remove all selected states
            document.querySelectorAll('.component-card.selected').forEach(card => {
                card.classList.remove('selected');
            });
            
            this.currentStep = 1;
            this.showStep(1);
            this.updateStepIndicator();
            this.updateNavigationButtons();
            
            const statusDiv = document.getElementById('compatibility-status');
            if (statusDiv) {
                statusDiv.innerHTML = '<h4>Kompatibilitätsstatus</h4><p>Wählen Sie Komponenten aus, um die Kompatibilität zu überprüfen.</p>';
            }
        }
    }
}

// Global functions for template usage
function clearFilters(category) {
    console.log(`Clearing filters for category: ${category}`);
    
    // Clear search input
    const searchInput = document.getElementById(`search-${category}`);
    if (searchInput) {
        searchInput.value = '';
        console.log(`Cleared search input for ${category}`);
    }
    
    // Clear all filter selects
    const filterSelects = document.querySelectorAll(`[id*="filter-${category}"], [id*="sort-${category}"]`);
    filterSelects.forEach(select => {
        select.value = '';
        console.log(`Cleared filter: ${select.id}`);
    });
    
    // For motherboard, handle special case
    if (category === 'motherboard') {
        const mbSocket = document.getElementById('filter-mb-socket');
        const mbFormFactor = document.getElementById('filter-mb-form-factor');
        if (mbSocket) mbSocket.value = '';
        if (mbFormFactor) mbFormFactor.value = '';
    }
    
    // Reapply filters to show all components
    if (window.configurator) {
        window.configurator.applyFilters(category);
        console.log(`Filters cleared and reapplied for ${category}`);
    }
}

function formatPrice(price) {
    return new Intl.NumberFormat('de-DE', { 
        style: 'currency', 
        currency: 'EUR' 
    }).format(price);
}

function formatSpecs(specs) {
    if (typeof specs === 'object') {
        return Object.entries(specs)
            .map(([key, value]) => `${key}: ${value}`)
            .join(' • ');
    }
    return specs;
}

function exportConfiguration() {
    if (window.configurator) {
        const configData = {
            components: window.configurator.selectedComponents,
            timestamp: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(configData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'pc-konfiguration.json';
        link.click();
    }
}

function importConfiguration() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                try {
                    const config = JSON.parse(event.target.result);
                    if (window.configurator) {
                        window.configurator.loadConfiguration(config);
                    }
                } catch (error) {
                    alert('Fehler beim Laden der Konfiguration: Ungültige Datei');
                }
            };
            reader.readAsText(file);
        }
    };
    
    input.click();
}