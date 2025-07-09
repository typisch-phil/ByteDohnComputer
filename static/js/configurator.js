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
        
        // Test all search inputs after page load
        setTimeout(() => {
            this.testInputs();
        }, 1000);
    }
    
    testInputs() {
        console.log('=== TESTING ALL INPUTS ===');
        const testInputs = [
            'search-cpu', 'filter-cpu-socket', 'filter-cpu-cores',
            'search-motherboard', 'filter-mb-socket'
        ];
        
        testInputs.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                console.log(`✓ Found element: ${id}, type: ${element.tagName}, value: "${element.value}"`);
                console.log(`  - Events: ${element.onclick ? 'onclick' : 'no onclick'}`);
                console.log(`  - Style: display=${getComputedStyle(element).display}, pointer-events=${getComputedStyle(element).pointerEvents}`);
                
                // Test manual event trigger
                element.addEventListener('click', () => {
                    console.log(`MANUAL CLICK TEST: ${id} clicked!`);
                });
                
                element.addEventListener('focus', () => {
                    console.log(`MANUAL FOCUS TEST: ${id} focused!`);
                });
                
                // For search fields, also test input event
                if (id.startsWith('search-')) {
                    element.addEventListener('input', () => {
                        console.log(`MANUAL INPUT TEST: ${id} input changed to "${element.value}"`);
                    });
                    element.addEventListener('keyup', () => {
                        console.log(`MANUAL KEYUP TEST: ${id} keyup with value "${element.value}"`);
                    });
                }
                
                // For select fields, test change event
                if (element.tagName === 'SELECT') {
                    element.addEventListener('change', () => {
                        console.log(`MANUAL CHANGE TEST: ${id} changed to "${element.value}"`);
                    });
                }
            } else {
                console.log(`✗ Missing element: ${id}`);
            }
        });
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
                element.addEventListener(eventType, (event) => {
                    console.log(`Filter triggered: ${filterId} = "${element.value}" for category ${category}`, event);
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
        
        // First hide all cards
        cards.forEach(card => {
            card.classList.add('hidden');
            card.style.display = 'none';
        });
        
        // Show and reorder filtered cards
        const sortContainer = document.querySelector(`#step-${this.getCategoryStep(category)} .component-selection`);
        if (sortContainer) {
            // Remove all cards from container first
            filteredCards.forEach(card => {
                if (card.parentNode) {
                    card.parentNode.removeChild(card);
                }
            });
            
            // Re-add cards in sorted order
            filteredCards.forEach(card => {
                card.classList.remove('hidden');
                card.style.display = '';
                sortContainer.appendChild(card);
            });
        }
        
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
            
            console.log(`CPU filters - socket: "${socket}", cores: "${cores}"`);
            
            return cards.filter(card => {
                const specsEl = card.querySelector('.component-specs');
                const specs = specsEl ? specsEl.textContent : '';
                
                console.log(`Checking CPU card specs: "${specs}"`);
                
                if (socket && socket !== '') {
                    const socketMatch = specs.includes(`Socket ${socket}`);
                    console.log(`Socket filter "${socket}" matches: ${socketMatch}`);
                    if (!socketMatch) return false;
                }
                
                if (cores && cores !== '') {
                    const coresMatch = specs.match(/(\d+) Kerne/);
                    if (coresMatch) {
                        const cardCores = parseInt(coresMatch[1]);
                        console.log(`Cores filter "${cores}" vs card cores: ${cardCores}`);
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
        console.log(`Applying sort: ${sortValue} to ${cards.length} cards`);
        
        if (!sortValue || sortValue === 'name') {
            // Default alphabetical sort by name
            return Array.from(cards).sort((a, b) => {
                const nameA = a.querySelector('.component-name')?.textContent || '';
                const nameB = b.querySelector('.component-name')?.textContent || '';
                return nameA.localeCompare(nameB);
            });
        }
        
        if (sortValue === 'price-asc' || sortValue === 'price-desc') {
            return Array.from(cards).sort((a, b) => {
                const priceAEl = a.querySelector('.component-price');
                const priceBEl = b.querySelector('.component-price');
                
                if (!priceAEl || !priceBEl) {
                    console.warn('Price element not found for sorting');
                    return 0;
                }
                
                const priceA = this.extractPrice(priceAEl.textContent);
                const priceB = this.extractPrice(priceBEl.textContent);
                
                console.log(`Sorting: ${priceA} vs ${priceB}`);
                
                const result = sortValue === 'price-asc' ? priceA - priceB : priceB - priceA;
                return result;
            });
        }
        
        return Array.from(cards);
    }
    
    getFilterValue(filterId) {
        const element = document.getElementById(filterId);
        if (!element) {
            console.warn(`Filter element not found: ${filterId}`);
            return '';
        }
        const value = element.value.trim();
        console.log(`Filter ${filterId} value: "${value}"`);
        return value;
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
            console.log('Sending compatibility check with:', this.selectedComponents);
            
            const response = await fetch('/api/validate-compatibility', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.selectedComponents)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('Compatibility result:', result);
            this.displayCompatibilityResults(result);
        } catch (error) {
            console.error('Compatibility check failed:', error);
            statusDiv.innerHTML = `
                <h4>Kompatibilitätsstatus</h4>
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i> 
                    Kompatibilitätsprüfung temporär nicht verfügbar
                </div>
            `;
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
            if (result.errors && result.errors.length > 0) {
                result.errors.forEach(error => {
                    html += `<div class="alert alert-warning mb-2">${error}</div>`;
                });
            }
        }
        
        // Show warnings if any
        if (result.warnings && result.warnings.length > 0) {
            result.warnings.forEach(warning => {
                html += `<div class="alert alert-info mb-2"><i class="fas fa-info-circle"></i> ${warning}</div>`;
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
        // Check if current step has a selection
        const currentCategory = this.getCurrentStepCategory();
        if (currentCategory && !this.selectedComponents[currentCategory]) {
            alert(`Bitte wählen Sie eine ${this.getCategoryDisplayName(currentCategory)} aus, bevor Sie fortfahren.`);
            return;
        }
        
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
            const currentCategory = this.getCurrentStepCategory();
            const hasSelection = currentCategory && this.selectedComponents[currentCategory];
            
            // Enable/disable next button based on selection
            nextBtn.disabled = !hasSelection;
            
            if (this.currentStep === this.totalSteps) {
                nextBtn.innerHTML = '<i class="fas fa-check"></i> Abschließen';
            } else {
                nextBtn.innerHTML = 'Weiter <i class="fas fa-arrow-right"></i>';
            }
        }
    }
    
    getCurrentStepCategory() {
        const stepCategories = {
            1: 'cpu',
            2: 'motherboard',
            3: 'ram',
            4: 'gpu',
            5: 'ssd',
            6: 'case',
            7: 'psu',
            8: 'cooler'
        };
        return stepCategories[this.currentStep];
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