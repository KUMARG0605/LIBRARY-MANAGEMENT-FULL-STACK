/**
 * Real-time Search with Autocomplete
 * Provides instant search results as user types
 */

class RealtimeSearch {
    constructor(options) {
        this.searchInput = document.querySelector(options.inputSelector);
        this.resultsContainer = document.querySelector(options.resultsSelector);
        this.minChars = options.minChars || 2;
        this.debounceTime = options.debounceTime || 300;
        this.apiEndpoint = options.apiEndpoint || '/api/search';
        this.onSelect = options.onSelect || this.defaultSelect;
        
        this.debounceTimer = null;
        this.currentRequest = null;
        this.cache = new Map();
        
        this.init();
    }
    
    init() {
        if (!this.searchInput) return;
        
        // Bind events
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('focus', (e) => this.handleFocus(e));
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideResults();
            }
        });
        
        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        // Clear previous timer
        clearTimeout(this.debounceTimer);
        
        // Hide if less than min chars
        if (query.length < this.minChars) {
            this.hideResults();
            return;
        }
        
        // Debounce search
        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, this.debounceTime);
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= this.minChars) {
            this.performSearch(query);
        }
    }
    
    async performSearch(query) {
        // Check cache first
        if (this.cache.has(query)) {
            this.displayResults(this.cache.get(query), query);
            return;
        }
        
        // Cancel previous request
        if (this.currentRequest) {
            this.currentRequest.abort();
        }
        
        // Show loading
        this.showLoading();
        
        try {
            // Create new request
            this.currentRequest = new AbortController();
            
            const response = await fetch(`${this.apiEndpoint}?q=${encodeURIComponent(query)}`, {
                signal: this.currentRequest.signal
            });
            
            if (!response.ok) throw new Error('Search failed');
            
            const data = await response.json();
            
            // Cache results
            this.cache.set(query, data);
            
            // Display results
            this.displayResults(data, query);
            
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Search error:', error);
                this.showError('Search failed. Please try again.');
            }
        } finally {
            this.currentRequest = null;
        }
    }
    
    displayResults(data, query) {
        this.hideLoading();
        
        if (!data || (!data.books && !data.authors && !data.categories)) {
            this.showNoResults();
            return;
        }
        
        let html = '<div class="search-results">';
        
        // Books
        if (data.books && data.books.length > 0) {
            html += '<div class="result-section">';
            html += '<h6 class="result-header"><i class="fas fa-book me-2"></i>Books</h6>';
            html += '<div class="result-list">';
            
            data.books.slice(0, 5).forEach(book => {
                html += this.renderBookResult(book, query);
            });
            
            if (data.books.length > 5) {
                html += `<a href="/search?q=${encodeURIComponent(query)}" class="result-item see-all">
                    <i class="fas fa-arrow-right me-2"></i>See all ${data.books.length} books
                </a>`;
            }
            
            html += '</div></div>';
        }
        
        // Authors
        if (data.authors && data.authors.length > 0) {
            html += '<div class="result-section">';
            html += '<h6 class="result-header"><i class="fas fa-user me-2"></i>Authors</h6>';
            html += '<div class="result-list">';
            
            data.authors.slice(0, 3).forEach(author => {
                html += this.renderAuthorResult(author, query);
            });
            
            html += '</div></div>';
        }
        
        // Categories
        if (data.categories && data.categories.length > 0) {
            html += '<div class="result-section">';
            html += '<h6 class="result-header"><i class="fas fa-tags me-2"></i>Categories</h6>';
            html += '<div class="result-list">';
            
            data.categories.forEach(category => {
                html += this.renderCategoryResult(category);
            });
            
            html += '</div></div>';
        }
        
        html += '</div>';
        
        this.resultsContainer.innerHTML = html;
        this.resultsContainer.classList.add('show');
        
        // Bind click events
        this.bindResultClicks();
    }
    
    renderBookResult(book, query) {
        const highlightedTitle = this.highlightMatch(book.title, query);
        const availability = book.available_copies > 0 ? 
            '<span class="badge bg-success ms-2">Available</span>' : 
            '<span class="badge bg-danger ms-2">Not Available</span>';
        
        return `
            <a href="/books/${book.id}" class="result-item book-result" data-id="${book.id}">
                <div class="result-content">
                    <div class="result-icon">
                        <img src="${book.cover_image || '/static/images/default-book.jpg'}" 
                             alt="${book.title}" class="book-thumbnail">
                    </div>
                    <div class="result-details">
                        <div class="result-title">${highlightedTitle}${availability}</div>
                        <div class="result-meta">
                            <small class="text-muted">
                                <i class="fas fa-user me-1"></i>${book.author}
                                <span class="mx-2">•</span>
                                <i class="fas fa-tag me-1"></i>${book.category}
                            </small>
                        </div>
                    </div>
                </div>
            </a>
        `;
    }
    
    renderAuthorResult(author, query) {
        const highlightedName = this.highlightMatch(author.name, query);
        
        return `
            <a href="/search?author=${encodeURIComponent(author.name)}" class="result-item">
                <div class="result-content">
                    <div class="result-icon">
                        <i class="fas fa-user-circle fa-2x text-primary"></i>
                    </div>
                    <div class="result-details">
                        <div class="result-title">${highlightedName}</div>
                        <small class="text-muted">${author.book_count} books</small>
                    </div>
                </div>
            </a>
        `;
    }
    
    renderCategoryResult(category) {
        return `
            <a href="/books?category=${category.id}" class="result-item">
                <div class="result-content">
                    <div class="result-icon">
                        <i class="fas fa-tag fa-lg text-info"></i>
                    </div>
                    <div class="result-details">
                        <div class="result-title">${category.name}</div>
                        <small class="text-muted">${category.book_count} books</small>
                    </div>
                </div>
            </a>
        `;
    }
    
    highlightMatch(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    showLoading() {
        this.resultsContainer.innerHTML = `
            <div class="search-loading">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                Searching...
            </div>
        `;
        this.resultsContainer.classList.add('show');
    }
    
    hideLoading() {
        // Loading will be replaced by results
    }
    
    showError(message) {
        this.resultsContainer.innerHTML = `
            <div class="search-error">
                <i class="fas fa-exclamation-circle me-2"></i>${message}
            </div>
        `;
        this.resultsContainer.classList.add('show');
    }
    
    showNoResults() {
        this.resultsContainer.innerHTML = `
            <div class="search-no-results">
                <i class="fas fa-search me-2"></i>No results found
            </div>
        `;
        this.resultsContainer.classList.add('show');
    }
    
    hideResults() {
        this.resultsContainer.classList.remove('show');
    }
    
    bindResultClicks() {
        this.resultsContainer.querySelectorAll('.result-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.onSelect(e, item);
            });
        });
    }
    
    defaultSelect(e, item) {
        // Default behavior is to follow the link
        // Can be overridden
    }
    
    handleKeyboard(e) {
        const items = this.resultsContainer.querySelectorAll('.result-item');
        const activeItem = this.resultsContainer.querySelector('.result-item.active');
        let currentIndex = Array.from(items).indexOf(activeItem);
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentIndex = (currentIndex + 1) % items.length;
                this.highlightItem(items[currentIndex]);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                currentIndex = currentIndex <= 0 ? items.length - 1 : currentIndex - 1;
                this.highlightItem(items[currentIndex]);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (activeItem) {
                    activeItem.click();
                }
                break;
                
            case 'Escape':
                this.hideResults();
                break;
        }
    }
    
    highlightItem(item) {
        // Remove previous highlight
        this.resultsContainer.querySelectorAll('.result-item.active').forEach(el => {
            el.classList.remove('active');
        });
        
        // Add highlight
        if (item) {
            item.classList.add('active');
            item.scrollIntoView({ block: 'nearest' });
        }
    }
    
    clearCache() {
        this.cache.clear();
    }
}

// CSS Styles (add to style.css)
const searchStyles = `
.search-results {
    max-height: 500px;
    overflow-y: auto;
}

.result-section {
    padding: 10px 0;
    border-bottom: 1px solid #e9ecef;
}

.result-section:last-child {
    border-bottom: none;
}

.result-header {
    color: #6c757d;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
    padding: 0 15px;
}

.result-item {
    display: block;
    padding: 10px 15px;
    color: inherit;
    text-decoration: none;
    transition: background-color 0.2s;
}

.result-item:hover,
.result-item.active {
    background-color: #f8f9fa;
}

.result-content {
    display: flex;
    align-items: center;
    gap: 12px;
}

.result-icon {
    flex-shrink: 0;
}

.book-thumbnail {
    width: 40px;
    height: 55px;
    object-fit: cover;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.result-details {
    flex: 1;
    min-width: 0;
}

.result-title {
    font-weight: 500;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.result-title mark {
    background-color: #fff3cd;
    padding: 1px 3px;
    border-radius: 2px;
}

.result-meta {
    font-size: 0.85rem;
}

.see-all {
    color: var(--primary-blue);
    font-weight: 500;
}

.search-loading,
.search-error,
.search-no-results {
    padding: 20px;
    text-align: center;
    color: #6c757d;
}

.search-error {
    color: #dc3545;
}
`;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize for header search
    if (document.querySelector('#headerSearch')) {
        window.realtimeSearch = new RealtimeSearch({
            inputSelector: '#headerSearch',
            resultsSelector: '#searchResults',
            minChars: 2,
            debounceTime: 300,
            apiEndpoint: '/api/search'
        });
    }
});
