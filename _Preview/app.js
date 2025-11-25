// Design Tokens Preview - Brand & Theme Switcher
class TokenPreview {
    constructor() {
        this.currentBrand = 'default';
        this.currentTheme = 'day';
        this.tokensViewerOpen = false;
        
        this.init();
    }
    
    init() {
        // Set up event listeners
        document.getElementById('brand-select').addEventListener('change', (e) => {
            this.switchBrand(e.target.value);
        });
        
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.switchTheme(e.target.value);
        });
        
        document.getElementById('toggle-tokens').addEventListener('click', () => {
            this.toggleTokensViewer();
        });
        
        document.getElementById('close-tokens').addEventListener('click', () => {
            this.toggleTokensViewer();
        });
        
        // Load initial tokens
        this.loadTokens();
        this.updateColorValues();
    }
    
    switchBrand(brand) {
        console.log(`Switching brand to: ${brand}`);
        this.currentBrand = brand;
        this.loadTokens();
    }
    
    switchTheme(theme) {
        console.log(`Switching theme to: ${theme}`);
        this.currentTheme = theme;
        this.loadTokens();
    }
    
    loadTokens() {
        // Try multiple path options to handle different server setups
        // If server is run from project root: _TransformedTokens/css/...
        // If server is run from _Preview: ../_TransformedTokens/css/...
        const pathOptions = [
            `_TransformedTokens/css/${this.currentBrand}_${this.currentTheme}/tokens.css`,
            `../_TransformedTokens/css/${this.currentBrand}_${this.currentTheme}/tokens.css`
        ];
        
        const tokenPath = pathOptions[0]; // Use first option by default (server from root)
        
        console.log(`Loading tokens from: ${tokenPath}`);
        
        // Remove old link
        const oldLink = document.getElementById('token-theme');
        if (oldLink) {
            oldLink.remove();
        }
        
        // Create new link element with cache busting
        const newLink = document.createElement('link');
        newLink.id = 'token-theme';
        newLink.rel = 'stylesheet';
        newLink.href = `${tokenPath}?v=${Date.now()}`; // Cache busting
        
        // Wait for CSS to load before updating
        newLink.onload = () => {
            console.log(`✅ Loaded tokens: ${this.currentBrand}_${this.currentTheme}`);
            this.updateColorValues();
            // Force a repaint to ensure styles are applied
            document.body.offsetHeight;
        };
        
        newLink.onerror = () => {
            console.error(`❌ Failed to load tokens from: ${tokenPath}`);
            console.log('Trying alternative paths...');
            // Try alternative path
            this.tryAlternativePath(pathOptions.slice(1), 0);
        };
        
        document.head.appendChild(newLink);
        
        // Reload tokens in viewer if open
        if (this.tokensViewerOpen) {
            setTimeout(() => this.loadTokensIntoViewer(), 200);
        }
    }
    
    tryAlternativePath(pathOptions, index) {
        if (index >= pathOptions.length) {
            alert(`Failed to load tokens for ${this.currentBrand} ${this.currentTheme}. Please check that token files exist.`);
            return;
        }
        
        const tokenPath = pathOptions[index];
        console.log(`Trying alternative path: ${tokenPath}`);
        
        const newLink = document.createElement('link');
        newLink.id = 'token-theme';
        newLink.rel = 'stylesheet';
        newLink.href = `${tokenPath}?v=${Date.now()}`;
        
        newLink.onload = () => {
            console.log(`✅ Loaded tokens from alternative path: ${tokenPath}`);
            this.updateColorValues();
        };
        
        newLink.onerror = () => {
            this.tryAlternativePath(pathOptions, index + 1);
        };
        
        const oldLink = document.getElementById('token-theme');
        if (oldLink) oldLink.remove();
        document.head.appendChild(newLink);
    }
    
    toggleTokensViewer() {
        const viewer = document.getElementById('tokens-viewer');
        this.tokensViewerOpen = !this.tokensViewerOpen;
        
        if (this.tokensViewerOpen) {
            viewer.classList.add('open');
            this.loadTokensIntoViewer();
        } else {
            viewer.classList.remove('open');
        }
    }
    
    async loadTokensIntoViewer() {
        const pathOptions = [
            `_TransformedTokens/css/${this.currentBrand}_${this.currentTheme}/tokens.css`,
            `../_TransformedTokens/css/${this.currentBrand}_${this.currentTheme}/tokens.css`
        ];
        
        const content = document.getElementById('tokens-content');
        let cssText = null;
        let lastError = null;
        
        // Try each path option
        for (const tokenPath of pathOptions) {
            try {
                console.log(`Fetching tokens from: ${tokenPath}`);
                const response = await fetch(tokenPath);
                if (response.ok) {
                    cssText = await response.text();
                    break;
                }
            } catch (error) {
                lastError = error;
                console.log(`Failed to load from ${tokenPath}, trying next...`);
            }
        }
        
        if (cssText) {
            // Parse CSS to extract tokens
            const tokens = this.parseCSSTokens(cssText);
            this.renderTokens(tokens, content);
        } else {
            console.error('Error loading tokens:', lastError);
            content.innerHTML = `<p>Error loading tokens. Tried paths: ${pathOptions.join(', ')}</p><p>Check browser console for details.</p>`;
        }
    }
    
    parseCSSTokens(cssText) {
        const tokens = {
            colors: [],
            spacing: [],
            typography: [],
            borderRadius: [],
            motion: [],
            accessibility: [],
            interactions: []
        };
        
        // Extract :root rules
        const rootMatch = cssText.match(/:root\s*\{([^}]+)\}/);
        if (!rootMatch) return tokens;
        
        const rootContent = rootMatch[1];
        
        // Parse each CSS variable
        const variableRegex = /--([^:]+):\s*([^;]+);/g;
        let match;
        
        while ((match = variableRegex.exec(rootContent)) !== null) {
            const name = match[1].trim();
            const value = match[2].trim();
            
            const token = { name, value };
            
            // Categorize tokens
            if (name.includes('color-')) {
                tokens.colors.push(token);
            } else if (name.includes('spacing-')) {
                tokens.spacing.push(token);
            } else if (name.includes('font-') || name.includes('line-height-')) {
                tokens.typography.push(token);
            } else if (name.includes('border-radius-')) {
                tokens.borderRadius.push(token);
            } else if (name.includes('motion-')) {
                tokens.motion.push(token);
            } else if (name.includes('accessibility-')) {
                tokens.accessibility.push(token);
            } else if (name.includes('interaction-')) {
                tokens.interactions.push(token);
            }
        }
        
        return tokens;
    }
    
    renderTokens(tokens, container) {
        container.innerHTML = '';
        
        const categories = [
            { name: 'Colors', tokens: tokens.colors, icon: '🎨' },
            { name: 'Spacing', tokens: tokens.spacing, icon: '📏' },
            { name: 'Typography', tokens: tokens.typography, icon: '✍️' },
            { name: 'Border Radius', tokens: tokens.borderRadius, icon: '⬜' },
            { name: 'Motion', tokens: tokens.motion, icon: '⚡' },
            { name: 'Accessibility', tokens: tokens.accessibility, icon: '♿' },
            { name: 'Interactions', tokens: tokens.interactions, icon: '👆' }
        ];
        
        categories.forEach(category => {
            if (category.tokens.length === 0) return;
            
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'token-category';
            
            const title = document.createElement('h3');
            title.textContent = `${category.icon} ${category.name}`;
            categoryDiv.appendChild(title);
            
            category.tokens.forEach(token => {
                const tokenDiv = document.createElement('div');
                tokenDiv.className = 'token-item';
                
                const nameSpan = document.createElement('span');
                nameSpan.className = 'token-name';
                nameSpan.textContent = `--${token.name}`;
                
                const valueSpan = document.createElement('span');
                valueSpan.className = 'token-value';
                valueSpan.textContent = token.value;
                
                tokenDiv.appendChild(nameSpan);
                tokenDiv.appendChild(valueSpan);
                categoryDiv.appendChild(tokenDiv);
            });
            
            container.appendChild(categoryDiv);
        });
    }
    
    updateColorValues() {
        // Update color value displays after a delay to allow CSS to load
        setTimeout(() => {
            const colorValueElements = document.querySelectorAll('.color-value[data-color]');
            colorValueElements.forEach(el => {
                const cssVar = el.getAttribute('data-color');
                const computedValue = getComputedStyle(document.documentElement)
                    .getPropertyValue(cssVar)
                    .trim();
                el.textContent = computedValue || 'N/A';
            });
            
            // Log current brand/theme for debugging
            console.log(`Current: ${this.currentBrand}_${this.currentTheme}`);
        }, 300);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new TokenPreview();
    });
} else {
    new TokenPreview();
}

