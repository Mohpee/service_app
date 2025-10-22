// Enhanced Mobile menu toggle functionality
function toggleMobileMenu() {
    const navbarNav = document.getElementById('navbar-nav');
    const toggleBtn = document.querySelector('.mobile-menu-toggle');

    navbarNav.classList.toggle('active');
    toggleBtn.classList.toggle('active');
}

// Theme toggle functionality
function toggleTheme() {
    const html = document.documentElement;
    const themeIcon = document.getElementById('theme-icon');
    const currentTheme = html.getAttribute('data-theme');

    if (currentTheme === 'dark') {
        html.removeAttribute('data-theme');
        themeIcon.className = 'fas fa-moon';
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
        localStorage.setItem('theme', 'dark');
    }
}

// Initialize theme on page load
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');

    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeIcon) themeIcon.className = 'fas fa-sun';
    } else {
        if (themeIcon) themeIcon.className = 'fas fa-moon';
    }
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const navbarNav = document.getElementById('navbar-nav');
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');

    if (navbarNav && mobileMenuToggle &&
        !navbarNav.contains(event.target) &&
        !mobileMenuToggle.contains(event.target)) {
        navbarNav.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
    }
});

// Enhanced initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initializeTheme();

    // Enhanced smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start',
                    inline: 'nearest'
                });
            }
            // Close mobile menu after clicking a link
            const navbarNav = document.getElementById('navbar-nav');
            const toggleBtn = document.querySelector('.mobile-menu-toggle');
            if (navbarNav) navbarNav.classList.remove('active');
            if (toggleBtn) toggleBtn.classList.remove('active');
        });
    });

    // Enhanced loading states for forms with better UX
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains('btn-loading')) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                submitBtn.classList.add('btn-loading');
                submitBtn.disabled = true;

                // Re-enable button after 10 seconds as fallback
                setTimeout(() => {
                    if (submitBtn.classList.contains('btn-loading')) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.classList.remove('btn-loading');
                        submitBtn.disabled = false;
                    }
                }, 10000);
            }
        });
    });

    // Enhanced navigation link handlers
    document.querySelectorAll('.navbar-nav a').forEach(link => {
        link.addEventListener('click', function() {
            const navbarNav = document.getElementById('navbar-nav');
            const toggleBtn = document.querySelector('.mobile-menu-toggle');
            if (navbarNav) navbarNav.classList.remove('active');
            if (toggleBtn) toggleBtn.classList.remove('active');
        });
    });

    // Add intersection observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.card, .btn, h1, h2, h3').forEach(el => {
        observer.observe(el);
    });

    // Add scroll-based navbar effects
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            navbar.style.transform = 'translateY(0)';
        }

        lastScrollTop = scrollTop;
    });

    // Add keyboard navigation support
    document.addEventListener('keydown', (e) => {
        // Close mobile menu with Escape key
        if (e.key === 'Escape') {
            const navbarNav = document.getElementById('navbar-nav');
            const toggleBtn = document.querySelector('.mobile-menu-toggle');
            if (navbarNav) navbarNav.classList.remove('active');
            if (toggleBtn) toggleBtn.classList.remove('active');
        }
    });
});