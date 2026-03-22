// Modern JavaScript Interactions & Animations
document.addEventListener('DOMContentLoaded', () => {
    
    // --- Theme Toggler ---
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        // Load saved preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            themeToggleBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
        }
        
        themeToggleBtn.addEventListener('click', () => {
            let currentTheme = document.documentElement.getAttribute('data-theme');
            if (currentTheme === 'dark') {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                themeToggleBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                themeToggleBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
            }
        });
    }

    // --- Animated Number Counters ---
    const counterElements = document.querySelectorAll('.animate-number');
    counterElements.forEach(el => {
        const targetStr = el.getAttribute('data-target');
        if (!targetStr) return;
        const target = parseFloat(targetStr);
        let current = 0;
        const duration = 1500; // ms
        const increment = target / (duration / 16); // 60fps
        
        const counterInterval = setInterval(() => {
            current += increment;
            if (current >= target) {
                el.innerText = target.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                clearInterval(counterInterval);
            } else {
                el.innerText = current.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }
        }, 16);
    });

    // --- Flash Message Auto-Hide ---
    const flashes = document.querySelectorAll('.alert');
    if (flashes.length > 0) {
        setTimeout(() => {
            flashes.forEach(flash => {
                flash.style.transition = "opacity 0.4s ease, transform 0.4s ease";
                flash.style.opacity = '0';
                flash.style.transform = 'translateX(50px)';
                setTimeout(() => flash.remove(), 400);
            });
        }, 5000);
    }
    
    // --- Error Shake Animation ---
    if (document.querySelector('.alert-danger')) {
        const authCard = document.querySelector('.auth-card');
        if (authCard) {
            authCard.classList.add('shake');
            setTimeout(() => authCard.classList.remove('shake'), 500);
        }
    }

    // --- Input Validation & Max Date ---
    const dateInputs = document.querySelectorAll('input[type="date"]');
    if (dateInputs.length > 0) {
        const today = new Date().toISOString().split('T')[0];
        dateInputs.forEach(input => {
            input.setAttribute('max', today);
        });
    }

    // Interactive button clicks (Micro-interaction)
    const buttons = document.querySelectorAll('.btn-primary');
    buttons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            let ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            let x = e.clientX - e.target.offsetLeft;
            let y = e.clientY - e.target.offsetTop;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            setTimeout(() => { ripple.remove(); }, 600);
        });
    });

    // Make body fade in
    document.body.classList.add('loaded');

    // --- Profile Dropdown Logic ---
    const profileBtn = document.getElementById('profile-dropdown-btn');
    const profileMenu = document.getElementById('profile-dropdown-menu');
    
    if (profileBtn && profileMenu) {
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if(profileMenu.classList.contains('show')) {
                profileMenu.classList.remove('show');
                setTimeout(() => { profileMenu.style.display = 'none'; }, 200);
            } else {
                profileMenu.style.display = 'block';
                // Small delay to allow display:block to apply before animating opacity
                setTimeout(() => profileMenu.classList.add('show'), 10);
            }
        });
        
        document.addEventListener('click', function(e) {
            if (!profileMenu.contains(e.target) && !profileBtn.contains(e.target)) {
                profileMenu.classList.remove('show');
                setTimeout(() => {
                    if(!profileMenu.classList.contains('show')) {
                        profileMenu.style.display = 'none';
                    }
                }, 200);
            }
        });
    }
});
