// Page-specific JavaScript functionality

// Debug: Check if functions are available globally
console.log('Global functions check:', {
    bookService: typeof window.bookService,
    quickView: typeof window.quickView,
    shareService: typeof window.shareService,
    addToFavorites: typeof window.addToFavorites
});

// Homepage functionality
function initializeHomepage() {
    // Search functionality
    const searchForm = document.querySelector('.homepage-search form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = this.querySelector('input[type="text"]').value.trim();
            if (query) {
                window.location.href = `/services/?q=${encodeURIComponent(query)}`;
            }
        });
    }

    // Category buttons
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const category = this.dataset.category;
            window.location.href = `/services/?category=${category}`;
        });
    });
}

// Dashboard functionality
function initializeDashboard() {
    // Order status update functionality
    window.updateOrderStatus = function(orderId, newStatus) {
        if (confirm(`Are you sure you want to mark this order as ${newStatus}?`)) {
            // Show loading state
            const btn = event.target;
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            btn.disabled = true;

            // In a real app, this would make an API call
            // For now, just simulate the update
            setTimeout(() => {
                btn.innerHTML = '<i class="fas fa-check"></i> Updated';
                btn.style.background = 'var(--success-color)';

                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    btn.style.background = '';
                }, 1500);
            }, 1000);
        }
    };

    // Notification functionality
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            this.classList.remove('unread');
        });
    });
}

// Profile functionality
function initializeProfile() {
    // Profile picture preview
    const profilePicInput = document.querySelector('input[name="profile_picture"]');
    if (profilePicInput) {
        profilePicInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('.profile-avatar');
                    if (preview) {
                        preview.src = e.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = 'var(--danger-color)';
                    isValid = false;
                } else {
                    field.style.borderColor = 'var(--light-secondary)';
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
}

// Service list functionality
function initializeServiceList() {
    // Enhanced search and filter functionality
    let searchTimeout;
    let currentView = 'grid';

    // Quick filter functionality
    window.quickFilter = function(category) {
        document.getElementById('category-select').value = category;
        document.getElementById('search-form').submit();
    };

    // Apply filters functionality
    window.applyFilters = function() {
        const formData = new FormData();
        const filters = {};

        // Collect filter values
        document.querySelectorAll('input[name], select[name]').forEach(element => {
            if (element.type === 'checkbox') {
                if (element.checked) {
                    if (!filters[element.name]) filters[element.name] = [];
                    filters[element.name].push(element.value);
                }
            } else if (element.value) {
                filters[element.name] = element.value;
            }
        });

        // Build URL with filters
        const url = new URL(window.location);
        Object.keys(filters).forEach(key => {
            if (Array.isArray(filters[key])) {
                filters[key].forEach(value => {
                    url.searchParams.append(key, value);
                });
            } else {
                url.searchParams.set(key, filters[key]);
            }
        });

        window.location.href = url.toString();
    };

    // Clear filters functionality
    window.clearFilters = function() {
        // Clear all form inputs
        document.querySelectorAll('input[type="text"], input[type="number"], select').forEach(input => {
            input.value = '';
        });
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });

        // Reset to homepage
        window.location.href = window.location.pathname;
    };

    // Change sort functionality
    window.changeSort = function(sortValue) {
        const url = new URL(window.location);
        url.searchParams.set('sort_by', sortValue);
        window.location.href = url.toString();
    };

    // Change per page functionality
    window.changePerPage = function(perPage) {
        const url = new URL(window.location);
        url.searchParams.set('per_page', perPage);
        window.location.href = url.toString();
    };

    // Toggle view functionality
    window.toggleView = function(viewType) {
        currentView = viewType;
        const gridView = document.getElementById('services-grid');

        // Update button states
        document.getElementById('grid-view').classList.toggle('active', viewType === 'grid');
        document.getElementById('list-view').classList.toggle('active', viewType === 'list');

        if (viewType === 'list') {
            gridView.style.gridTemplateColumns = '1fr';
            gridView.querySelectorAll('.service-list-card').forEach(card => {
                card.style.display = 'flex';
                card.style.flexDirection = 'row';
                const imageDiv = card.querySelector('.service-list-card-image');
                const contentDiv = card.querySelector('.service-list-card-content');
                if (imageDiv && contentDiv) {
                    imageDiv.style.flex = '0 0 300px';
                    contentDiv.style.flex = '1';
                }
            });
        } else {
            gridView.style.gridTemplateColumns = 'repeat(auto-fill, minmax(340px, 1fr))';
            gridView.querySelectorAll('.service-list-card').forEach(card => {
                card.style.display = 'block';
                card.style.flexDirection = 'column';
                const imageDiv = card.querySelector('.service-list-card-image');
                const contentDiv = card.querySelector('.service-list-card-content');
                if (imageDiv && contentDiv) {
                    imageDiv.style.flex = 'none';
                    contentDiv.style.flex = 'none';
                }
            });
        }
    };

    // Book service functionality
    window.bookService = function(serviceId) {
        console.log('bookService called with serviceId:', serviceId);
        // Check if user is authenticated using Django session
        fetch('/users/profile/', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log('Authentication check response:', response.status);
            if (response.ok) {
                window.location.href = `/orders/book/${serviceId}/`;
            } else {
                // Redirect to login with next parameter
                window.location.href = `/users/login/?next=/orders/book/${serviceId}/`;
            }
        })
        .catch((error) => {
            console.error('Authentication check failed:', error);
            window.location.href = `/users/login/?next=/orders/book/${serviceId}/`;
        });
    };

    // Quick view functionality
    window.quickView = function(serviceId) {
        console.log('quickView called with serviceId:', serviceId);
        // Open modal with service details
        fetch(`/services/${serviceId}/`, {
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log('Quick view fetch response:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Quick view data:', data);
            // Create and show modal with service data
            showServiceModal(data);
        })
        .catch(error => {
            console.error('Error fetching service details:', error);
        });
    };

    // Add to favorites functionality
    window.addToFavorites = function(serviceId) {
        console.log('addToFavorites called with serviceId:', serviceId);
        fetch(`/services/favorites/${serviceId}/`, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log('Add to favorites response:', response.status);
            if (response.ok) {
                // Show success message
                showToast('Service added to favorites!', 'success');
            } else if (response.status === 401) {
                window.location.href = '/users/login/';
            } else {
                showToast('Error adding to favorites', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error adding to favorites', 'error');
        });
    };

    // Share service functionality
    window.shareService = function(serviceId) {
        console.log('shareService called with serviceId:', serviceId);
        const url = window.location.origin + `/services/${serviceId}/`;

        if (navigator.share) {
            navigator.share({
                title: 'Check out this service',
                url: url
            }).catch(() => {
                // Fallback to clipboard if share fails
                navigator.clipboard.writeText(url).then(() => {
                    showToast('Service link copied to clipboard!', 'success');
                });
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(url).then(() => {
                showToast('Service link copied to clipboard!', 'success');
            }).catch(() => {
                showToast('Unable to share service link', 'error');
            });
        }
    };

    // Show service modal
    function showServiceModal(serviceData) {
        // Create modal HTML
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); display: flex; align-items: center;
            justify-content: center; z-index: 1000;
        `;

        modal.innerHTML = `
            <div style="background: white; border-radius: var(--radius-lg); max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto;">
                <div style="padding: var(--spacing-lg); border-bottom: 1px solid var(--light-secondary);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>${serviceData.name}</h3>
                        <button onclick="this.closest('div').parentElement.remove()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
                    </div>
                </div>
                <div style="padding: var(--spacing-lg);">
                    <p>${serviceData.description}</p>
                    <div style="display: flex; gap: var(--spacing-md); margin-top: var(--spacing-lg);">
                        <button class="btn btn-primary" onclick="bookService('${serviceData.id}'); this.closest('div').parentElement.remove();">Book Now</button>
                        <a href="/services/${serviceData.id}/" class="btn btn-outline">View Full Details</a>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    // Enhanced search with suggestions
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value;

            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    fetchSuggestions(query);
                }, 300);
            }
        });
    }

    function fetchSuggestions(query) {
        fetch(`/services/search/suggestions/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                showSuggestions(data);
            })
            .catch(error => console.error('Error fetching suggestions:', error));
    }

    function showSuggestions(suggestions) {
        // Remove existing suggestions
        const existing = document.querySelector('.search-suggestions');
        if (existing) existing.remove();

        if (!suggestions.services.length && !suggestions.locations.length) return;

        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'search-suggestions';
        suggestionsDiv.style.cssText = `
            position: absolute; top: 100%; left: 0; right: 0; background: white;
            border: 1px solid var(--light-secondary); border-radius: var(--radius-md);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 1000; max-height: 300px; overflow-y: auto;
        `;

        // Add services
        if (suggestions.services.length) {
            suggestionsDiv.innerHTML += '<div style="padding: 0.5rem 1rem; background: var(--light-bg); font-weight: 600; font-size: 0.875rem;">Services</div>';
            suggestions.services.forEach(service => {
                suggestionsDiv.innerHTML += `<div style="padding: 0.5rem 1rem; cursor: pointer;" onclick="selectSuggestion('${service}')">${service}</div>`;
            });
        }

        // Add locations
        if (suggestions.locations.length) {
            suggestionsDiv.innerHTML += '<div style="padding: 0.5rem 1rem; background: var(--light-bg); font-weight: 600; font-size: 0.875rem;">Locations</div>';
            suggestions.locations.forEach(location => {
                suggestionsDiv.innerHTML += `<div style="padding: 0.5rem 1rem; cursor: pointer;" onclick="selectLocation('${location}')">📍 ${location}</div>`;
            });
        }

        const formGroup = document.querySelector('.service-list-search-form .form-group');
        if (formGroup) {
            formGroup.style.position = 'relative';
            formGroup.appendChild(suggestionsDiv);
        }
    }

    window.selectSuggestion = function(value) {
        document.getElementById('search-input').value = value;
        document.querySelector('.search-suggestions').remove();
        document.getElementById('search-form').submit();
    };

    window.selectLocation = function(value) {
        document.getElementById('location-input').value = value;
        document.querySelector('.search-suggestions').remove();
    };

    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.service-list-search-form .form-group')) {
            const suggestions = document.querySelector('.search-suggestions');
            if (suggestions) suggestions.remove();
        }
    });

    // Initialize price range slider
    function initPriceSlider() {
        // This would initialize a proper price range slider
        // For now, just ensure the inputs work together
        const minPrice = document.getElementById('min-price');
        const maxPrice = document.getElementById('max-price');

        if (minPrice && maxPrice) {
            minPrice.addEventListener('input', function() {
                if (maxPrice.value && parseInt(this.value) > parseInt(maxPrice.value)) {
                    this.value = maxPrice.value;
                }
            });

            maxPrice.addEventListener('input', function() {
                if (minPrice.value && parseInt(this.value) < parseInt(minPrice.value)) {
                    this.value = minPrice.value;
                }
            });
        }
    }

    // Service card interactions
    document.querySelectorAll('.service-list-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't navigate if clicking on a button or link
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' ||
                e.target.closest('button') || e.target.closest('a')) {
                return;
            }

            // Find the service ID from the View Details link within this card
            const viewDetailsLink = this.querySelector('a[href*="service-detail"]');
            if (viewDetailsLink) {
                const href = viewDetailsLink.getAttribute('href');
                const serviceIdMatch = href.match(/\/services\/(\d+)\//);
                if (serviceIdMatch) {
                    window.location.href = `/services/${serviceIdMatch[1]}/`;
                }
            }
        });
    });

    // Debug: Log that service list is initialized
    console.log('Service list initialized with', document.querySelectorAll('.service-list-card').length, 'cards');

    // Service detail page functions
    window.bookService = function() {
        // Scroll to booking form
        const bookingForm = document.getElementById('booking-form');
        if (bookingForm) {
            bookingForm.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });

            // Focus on date input
            const dateInput = document.getElementById('booking-date');
            if (dateInput) {
                dateInput.focus();
            }
        }
    };

    window.contactProvider = function() {
        // In a real app, this would open a chat or contact form
        alert('Contact feature coming soon!');
    };

    window.toggleFavorite = function() {
        // In a real app, this would add/remove from favorites
        const btn = event.target.closest('button');
        const icon = btn.querySelector('i');

        if (icon.classList.contains('far')) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            btn.style.color = '#ff3b30';
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            btn.style.color = '';
        }
    };

    window.changeMainImage = function(imageSrc) {
        const mainImage = document.querySelector('.service-image');
        if (mainImage) {
            mainImage.src = imageSrc;
        }
    };

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        initPriceSlider();

        // Auto-submit form on filter change (with debounce)
        document.querySelectorAll('input, select').forEach(element => {
            element.addEventListener('change', function() {
                if (this.type === 'text' || this.type === 'number') return; // Don't auto-submit for text inputs

                clearTimeout(window.filterTimeout);
                window.filterTimeout = setTimeout(() => {
                    applyFilters();
                }, 800);
            });
        });

        // Show loading state during search
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', function() {
                const loading = document.getElementById('loading');
                const grid = document.getElementById('services-grid');
                if (loading) loading.style.display = 'block';
                if (grid) grid.style.opacity = '0.5';
            });
        }
    });
}

// Order functionality
function initializeOrders() {
    // Order status updates
    document.querySelectorAll('.order-status-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const orderId = this.dataset.orderId;
            const newStatus = this.dataset.status;

            if (confirm(`Change order status to ${newStatus}?`)) {
                // In a real app, make API call here
                console.log(`Updating order ${orderId} to ${newStatus}`);
            }
        });
    });

    // Order cancellation
    document.querySelectorAll('.cancel-order-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const orderId = this.dataset.orderId;

            if (confirm('Are you sure you want to cancel this order?')) {
                // In a real app, make API call here
                console.log(`Cancelling order ${orderId}`);
            }
        });
    });
}

// Notification functionality
function initializeNotifications() {
    // Mark as read
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            this.classList.remove('unread');
        });
    });

    // Clear all notifications
    const clearAllBtn = document.querySelector('.clear-notifications-btn');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function() {
            if (confirm('Clear all notifications?')) {
                document.querySelectorAll('.notification-item').forEach(item => {
                    item.style.display = 'none';
                });
                this.style.display = 'none';
            }
        });
    }
}

// Authentication functionality
function initializeAuth() {
    // Password confirmation validation
    const passwordFields = document.querySelectorAll('input[type="password"]');
    if (passwordFields.length >= 2) {
        const password = passwordFields[0];
        const confirmPassword = passwordFields[1];

        confirmPassword.addEventListener('input', function() {
            if (password.value !== this.value) {
                this.style.borderColor = 'var(--danger-color)';
                this.setCustomValidity('Passwords do not match');
            } else {
                this.style.borderColor = 'var(--success-color)';
                this.setCustomValidity('');
            }
        });
    }

    // Show/hide password toggle
    document.querySelectorAll('.login-password-toggle, .password-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
}

function initializeRegister() {
    // Account type selection
    window.selectAccountType = function(type) {
        // Remove active state from all cards
        document.querySelectorAll('.register-account-type-card').forEach(card => {
            card.classList.remove('active');
        });

        // Add active state to selected card
        const clickedCard = event.target.closest('.register-account-type-card');
        if (clickedCard) {
            clickedCard.classList.add('active');
        }

        // Set the radio button value
        const radioBtn = document.getElementById(`${type}-radio`);
        if (radioBtn) {
            radioBtn.checked = true;
        }

        // Set the hidden input value
        const hiddenInput = document.getElementById('account_type_hidden');
        if (hiddenInput) {
            hiddenInput.value = type;
        }

        // Show/hide phone number field for providers
        const phoneGroup = document.getElementById('phone-group');
        if (phoneGroup) {
            if (type === 'provider') {
                phoneGroup.style.display = 'block';
            } else {
                phoneGroup.style.display = 'none';
            }
        }
    };

    // Form validation and submission
    const registrationForm = document.getElementById('registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission

            const password = document.querySelector('input[name="password"]').value;
            const password2 = document.querySelector('input[name="password2"]').value;

            if (password !== password2) {
                alert('Passwords do not match!');
                return;
            }

            if (password.length < 8) {
                alert('Password must be at least 8 characters long!');
                return;
            }

            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';
            submitBtn.disabled = true;

            // Prepare form data
            const formData = new FormData(this);

            // Debug: Log form data
            console.log('Form data being sent:');
            for (let [key, value] of formData.entries()) {
                console.log(key, value);
            }

            // Send AJAX request
            fetch('/users/register/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    return response.json().then(data => {
                        throw new Error(JSON.stringify(data));
                    });
                }
            })
            .then(data => {
                if (data.message) {
                    // Success - redirect to homepage
                    window.location.href = data.redirect_url || '/';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                try {
                    const errorData = JSON.parse(error.message);
                    let errorMessage = 'Registration failed:\n';
                    for (let field in errorData) {
                        if (Array.isArray(errorData[field])) {
                            errorMessage += `${field}: ${errorData[field].join(', ')}\n`;
                        } else {
                            errorMessage += `${field}: ${errorData[field]}\n`;
                        }
                    }
                    alert(errorMessage);
                } catch (e) {
                    alert('An error occurred. Please try again.');
                }
            })
            .finally(() => {
                // Reset button state
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    }

    // Password strength indicator
    const passwordInput = document.querySelector('input[name="password"]');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            // Add password strength logic here if needed
        });
    }
}

function initializeLogin() {
    // Add form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const username = document.querySelector('input[name="username"]').value;
            const password = document.querySelector('input[name="password"]').value;

            if (!username || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
                return;
            }

            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
            submitBtn.disabled = true;

            // Let the form submit normally - Django will handle authentication
        });
    }
}

// Utility functions
function showToast(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    // Add to page
    document.body.appendChild(toast);

    // Show and hide
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-KE', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Initialize page-specific functionality based on body classes or data attributes
document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;

    // Check for page-specific classes or initialize based on URL/content
    if (body.classList.contains('homepage') || document.querySelector('.homepage-hero')) {
        initializeHomepage();
    }

    if (body.classList.contains('dashboard') || document.querySelector('.dashboard-stats')) {
        initializeDashboard();
    }

    if (body.classList.contains('profile') || document.querySelector('.profile-avatar')) {
        initializeProfile();
    }

    if (body.classList.contains('service-list') || document.querySelector('#services-grid') || document.querySelector('.service-list-grid')) {
        initializeServiceList();
    }

    if (body.classList.contains('service-detail') || document.querySelector('.service-detail') || document.querySelector('#booking-form')) {
        // Initialize service detail page functions
        const dateInput = document.getElementById('booking-date');
        if (dateInput) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.min = today;
        }

        // Set rating bar widths
        document.querySelectorAll('.rating-bar').forEach(bar => {
            const width = bar.getAttribute('data-width') + '%';
            bar.style.width = width;
        });

        // Handle booking form submission
        const bookingForm = document.getElementById('booking-form');
        if (bookingForm) {
            bookingForm.addEventListener('submit', function(e) {
                e.preventDefault();

                // In a real app, this would submit the booking
                alert('Booking feature coming soon!');

                // Show success message
                const btn = this.querySelector('button[type="submit"]');
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i> Booked!';
                btn.style.background = 'var(--success-color)';

                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.background = '';
                }, 2000);
            });
        }
    }

    if (body.classList.contains('orders') || document.querySelector('.order-card')) {
        initializeOrders();
    }

    if (body.classList.contains('notifications') || document.querySelector('.notification-item')) {
        initializeNotifications();
    }

    if (body.classList.contains('auth') || document.querySelector('.auth-form') || document.querySelector('.login-section') || document.querySelector('.register-section')) {
        initializeAuth();
        initializeLogin();
        initializeRegister();
    }

    // Always initialize common functionality
    initializeCommon();
});

function initializeAbout() {
    // Add hover effects for feature cards
    const featureCards = document.querySelectorAll('.about-features .card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function initializeContact() {
    // Form submission handling
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            submitBtn.disabled = true;

            // Simulate form submission (replace with actual API call)
            setTimeout(() => {
                // Show success message
                const formContainer = this.parentElement;
                formContainer.innerHTML = `
                    <div class="text-center" style="padding: var(--spacing-xl);">
                        <div style="width: 80px; height: 80px; background: var(--success-color); border-radius: var(--radius-full); display: flex; align-items: center; justify-content: center; margin: 0 auto var(--spacing-lg);">
                            <i class="fas fa-check" style="font-size: 2rem; color: white;"></i>
                        </div>
                        <h3 style="color: var(--text-primary); margin-bottom: var(--spacing-md);">Message Sent Successfully!</h3>
                        <p style="color: var(--text-secondary);">Thank you for contacting us. We'll get back to you within 24 hours.</p>
                    </div>
                `;
            }, 2000);
        });
    }

    // Social media hover effects
    document.querySelectorAll('.contact-social-links a').forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
        });
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

function initializeCommon() {
    // Add any common page functionality here
    console.log('ServiceHub initialized');

    // Initialize about page if on about page
    if (document.querySelector('.about-hero')) {
        initializeAbout();
    }

    // Initialize contact page if on contact page
    if (document.querySelector('.contact-hero')) {
        initializeContact();
    }
}