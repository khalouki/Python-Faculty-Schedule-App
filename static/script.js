

// Initialize Lucide icons
lucide.createIcons()
// Toggle mobile menu with animation
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');

// Initially hide the mobile menu
mobileMenu.style.display = 'none';

mobileMenuButton.addEventListener('click', () => {
    if (mobileMenu.style.display === 'none') {
        mobileMenu.style.display = 'block';
        setTimeout(() => {
            mobileMenu.classList.add('show');
        }, 10);
    } else {
        mobileMenu.classList.remove('show');
        setTimeout(() => {
            mobileMenu.style.display = 'none';
        }, 300);
    }
});

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const isClickInsideMenu = mobileMenu.contains(event.target);
    const isClickOnButton = mobileMenuButton.contains(event.target);
    
    if (!isClickInsideMenu && !isClickOnButton && mobileMenu.style.display === 'block') {
        mobileMenu.classList.remove('show');
        setTimeout(() => {
            mobileMenu.style.display = 'none';
        }, 300);
    }
})
// Add active class to current page link
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});