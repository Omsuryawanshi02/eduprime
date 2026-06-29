/* ========================================
   EduPrime — Interactive Scripts
   ======================================== */

document.addEventListener('DOMContentLoaded', () => {

    // ----------------------------------
    // Reset any stuck buttons on page load/back navigation
    // ----------------------------------
    function resetAllButtons() {
        // Reset student login button
        const studentBtn = document.getElementById('student-login-submit');
        if (studentBtn) {
            studentBtn.disabled = false;
            studentBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M7 3H4C3.45 3 3 3.45 3 4V14C3 14.55 3.45 15 4 15H7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M12 12L15 9L12 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 9H15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg> Sign In as Student`;
        }
        // Reset admin login button
        const adminBtn = document.getElementById('admin-login-submit');
        if (adminBtn) {
            adminBtn.disabled = false;
            adminBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M12 11C12 11 14 9.66 14 7.5C14 5.34 12 2 9 2C6 2 4 5.34 4 7.5C4 9.66 6 11 6 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M9 11V16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg> Sign In as Admin`;
        }
        // Reset enrollment button
        const enrollBtn = document.getElementById('submit-enrollment');
        if (enrollBtn) {
            enrollBtn.disabled = false;
        }
    }

    // Run on page load
    resetAllButtons();

    // Run when user navigates back (pageshow fires on back/forward cache)
    window.addEventListener('pageshow', (e) => {
        if (e.persisted) {
            resetAllButtons();
        }
    });

    // ----------------------------------
    // Navbar scroll effect
    // ----------------------------------
    const navbar = document.getElementById('navbar');
    const handleScroll = () => {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    // ----------------------------------
    // Mobile navigation toggle
    // ----------------------------------
    const mobileToggle = document.getElementById('mobile-toggle');
    const navLinks = document.getElementById('nav-links');

    mobileToggle.addEventListener('click', () => {
        mobileToggle.classList.toggle('active');
        navLinks.classList.toggle('open');
        document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
    });

    // Close mobile nav on link click
    navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            mobileToggle.classList.remove('active');
            navLinks.classList.remove('open');
            document.body.style.overflow = '';
        });
    });

    // ----------------------------------
    // Scroll-triggered animations
    // ----------------------------------
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15, rootMargin: '0px 0px -50px 0px' }
    );
    animateElements.forEach(el => observer.observe(el));

    // ----------------------------------
    // Animated counters
    // ----------------------------------
    const counters = document.querySelectorAll('.stat-number, .counter');
    const counterObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );
    counters.forEach(el => counterObserver.observe(el));

    function animateCounter(el) {
        const target = parseInt(el.getAttribute('data-target'), 10);
        const duration = 2000;
        const start = performance.now();

        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // Ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(target * eased);
            if (progress < 1) requestAnimationFrame(update);
        }

        requestAnimationFrame(update);
    }

    // ----------------------------------
    // Result bars animation
    // ----------------------------------
    const resultBars = document.querySelectorAll('.result-bar-fill');
    const barObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const width = entry.target.getAttribute('data-width');
                    entry.target.style.width = width + '%';
                    barObserver.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );
    resultBars.forEach(el => barObserver.observe(el));

    // ----------------------------------
    // Testimonials carousel
    // ----------------------------------
    const track = document.getElementById('testimonials-track');
    const prevBtn = document.getElementById('carousel-prev');
    const nextBtn = document.getElementById('carousel-next');
    const dotsContainer = document.getElementById('carousel-dots');
    const cards = track ? track.querySelectorAll('.testimonial-card') : [];

    let currentSlide = 0;
    let slidesVisible = window.innerWidth <= 768 ? 1 : 2;
    let totalSlides = Math.ceil(cards.length / slidesVisible);

    function createDots() {
        dotsContainer.innerHTML = '';
        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('div');
            dot.classList.add('carousel-dot');
            if (i === 0) dot.classList.add('active');
            dot.addEventListener('click', () => goToSlide(i));
            dotsContainer.appendChild(dot);
        }
    }

    function goToSlide(index) {
        currentSlide = index;
        const cardWidth = cards[0].offsetWidth + 24; // gap
        track.style.transform = `translateX(-${currentSlide * cardWidth * slidesVisible}px)`;
        updateDots();
    }

    function updateDots() {
        dotsContainer.querySelectorAll('.carousel-dot').forEach((dot, i) => {
            dot.classList.toggle('active', i === currentSlide);
        });
    }

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => {
            currentSlide = Math.max(0, currentSlide - 1);
            goToSlide(currentSlide);
        });

        nextBtn.addEventListener('click', () => {
            currentSlide = Math.min(totalSlides - 1, currentSlide + 1);
            goToSlide(currentSlide);
        });
    }

    function handleResize() {
        const newVisible = window.innerWidth <= 768 ? 1 : 2;
        if (newVisible !== slidesVisible) {
            slidesVisible = newVisible;
            totalSlides = Math.ceil(cards.length / slidesVisible);
            currentSlide = 0;
            goToSlide(0);
            createDots();
        }
    }

    if (cards.length) {
        createDots();
        window.addEventListener('resize', handleResize, { passive: true });
    }

    // Auto-advance testimonials
    let autoSlide = setInterval(() => {
        if (currentSlide < totalSlides - 1) {
            currentSlide++;
        } else {
            currentSlide = 0;
        }
        goToSlide(currentSlide);
    }, 5000);

    // Pause auto-advance on hover
    const carouselEl = document.getElementById('testimonials-carousel');
    if (carouselEl) {
        carouselEl.addEventListener('mouseenter', () => clearInterval(autoSlide));
        carouselEl.addEventListener('mouseleave', () => {
            autoSlide = setInterval(() => {
                if (currentSlide < totalSlides - 1) {
                    currentSlide++;
                } else {
                    currentSlide = 0;
                }
                goToSlide(currentSlide);
            }, 5000);
        });
    }

    // ----------------------------------
    // Form submission with toast
    // ----------------------------------
    const form = document.getElementById('enrollment-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Submitting...';

            const payload = {
                student_name: (form.querySelector('#student-name') || {}).value || '',
                parent_name:  (form.querySelector('#parent-name')  || {}).value || '',
                grade:        (form.querySelector('#grade')         || {}).value || '',
                phone:        (form.querySelector('#phone')         || {}).value || '',
                message:      (form.querySelector('#message')       || {}).value || '',
                program:      (form.querySelector('#program-select')|| {}).value || '',
                email:        (form.querySelector('#email')         || {}).value || ''
            };

            try {
                const res = await fetch('/api/inquiries', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.success) {
                    showToast(data.message || 'Enrollment inquiry submitted! We will contact you within 24 hours.');
                    form.reset();
                } else {
                    showToast('Error: ' + (data.error || 'Something went wrong. Please try again.'), 'error');
                }
            } catch (err) {
                showToast('Network error. Please check your connection and try again.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    function showToast(message, type) {
        // Remove existing toast
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'toast' + (type === 'error' ? ' toast-error' : '');
        toast.innerHTML = `
            <div class="toast-icon">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M3 7L6 10L11 4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                toast.classList.add('show');
            });
        });

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 600);
        }, 4000);
    }

    // ----------------------------------
    // Smooth scroll for anchor links
    // ----------------------------------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const href = anchor.getAttribute('href');
            if (href === '#') return;
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const offset = navbar.offsetHeight + 20;
                const top = target.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top, behavior: 'smooth' });
            }
        });
    });

    // ----------------------------------
    // Parallax effect on hero shapes
    // ----------------------------------
    const shapes = document.querySelectorAll('.shape');
    let ticking = false;

    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scrolled = window.scrollY;
                shapes.forEach((shape, i) => {
                    const speed = 0.03 + (i * 0.015);
                    shape.style.transform = `translateY(${scrolled * speed}px)`;
                });
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    // ----------------------------------
    // Login Modal
    // ----------------------------------
    const loginOverlay = document.getElementById('login-modal-overlay');
    const loginModal = document.getElementById('login-modal');
    const loginClose = document.getElementById('login-modal-close');
    const loginBtns = [
        document.getElementById('btn-login'),
        document.getElementById('btn-login-mobile')
    ];
    const adminBtns = [
        document.getElementById('btn-admin-login'),
        document.getElementById('btn-admin-login-mobile')
    ];
    const tabStudent = document.getElementById('tab-student');
    const tabAdmin = document.getElementById('tab-admin');
    const studentForm = document.getElementById('student-login-form');
    const adminForm = document.getElementById('admin-login-form');
    const tabIndicator = document.getElementById('login-tab-indicator');

    function openLoginModal(role) {
        if (!loginOverlay) return;
        loginOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        switchTab(role || 'student');

        // Close mobile nav if open
        const mobileNavLinks = document.getElementById('nav-links');
        const mobileToggleBtn = document.getElementById('mobile-toggle');
        if (mobileNavLinks && mobileNavLinks.classList.contains('open')) {
            mobileNavLinks.classList.remove('open');
            mobileToggleBtn.classList.remove('active');
        }
    }

    function closeLoginModal() {
        if (!loginOverlay) return;
        loginOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    function switchTab(role) {
        if (role === 'admin') {
            tabStudent.classList.remove('active');
            tabAdmin.classList.add('active');
            studentForm.style.display = 'none';
            adminForm.style.display = 'block';
            if (tabIndicator) {
                tabIndicator.style.transform = 'translateX(100%)';
            }
        } else {
            tabAdmin.classList.remove('active');
            tabStudent.classList.add('active');
            adminForm.style.display = 'none';
            studentForm.style.display = 'block';
            if (tabIndicator) {
                tabIndicator.style.transform = 'translateX(0)';
            }
        }
    }

    // Open modal — Student login
    loginBtns.forEach(btn => {
        if (btn) btn.addEventListener('click', () => openLoginModal('student'));
    });

    // Open modal — Admin login
    adminBtns.forEach(btn => {
        if (btn) btn.addEventListener('click', () => openLoginModal('admin'));
    });

    // Close modal
    if (loginClose) {
        loginClose.addEventListener('click', closeLoginModal);
    }

    // Close on overlay click
    if (loginOverlay) {
        loginOverlay.addEventListener('click', (e) => {
            if (e.target === loginOverlay) closeLoginModal();
        });
    }

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && loginOverlay && loginOverlay.classList.contains('active')) {
            closeLoginModal();
        }
    });

    // Tab switching inside modal
    if (tabStudent) {
        tabStudent.addEventListener('click', () => switchTab('student'));
    }
    if (tabAdmin) {
        tabAdmin.addEventListener('click', () => switchTab('admin'));
    }

    // Enroll link inside modal should close it
    const enrollLink = document.getElementById('login-enroll-link');
    if (enrollLink) {
        enrollLink.addEventListener('click', () => closeLoginModal());
    }

    // Password visibility toggle
    document.querySelectorAll('.login-password-toggle').forEach(toggle => {
        toggle.addEventListener('click', () => {
            const wrap = toggle.closest('.login-input-wrap');
            const input = wrap.querySelector('input');
            const eyeOpen = toggle.querySelector('.eye-open');
            const eyeClosed = toggle.querySelector('.eye-closed');

            if (input.type === 'password') {
                input.type = 'text';
                eyeOpen.style.display = 'none';
                eyeClosed.style.display = 'block';
            } else {
                input.type = 'password';
                eyeOpen.style.display = 'block';
                eyeClosed.style.display = 'none';
            }
        });
    });

    // Form submissions
    if (studentForm) {
        studentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('student-login-submit');
            const origText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = 'Signing in...';

            const emailVal    = document.getElementById('student-login-id').value.trim();
            const passwordVal = document.getElementById('student-login-password').value;

            if (!emailVal || !passwordVal) {
                showToast('Please enter your email and password.', 'error');
                btn.disabled = false;
                btn.innerHTML = origText;
                return;
            }

            try {
                const res = await fetch('/student/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: emailVal, password: passwordVal }),
                    credentials: 'same-origin'
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Login successful! Redirecting...');
                    setTimeout(() => { window.location.href = data.redirect || '/student/attendance'; }, 800);
                } else {
                    showToast(data.error || 'Invalid email or password.', 'error');
                    btn.disabled = false;
                    btn.innerHTML = origText;
                }
            } catch (err) {
                showToast('Network error. Please try again.', 'error');
                btn.disabled = false;
                btn.innerHTML = origText;
            }
        });
    }

    if (adminForm) {
        adminForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('admin-login-submit');
            const origText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = 'Authenticating...';

            const usernameVal = document.getElementById('admin-login-id').value.trim();
            const passwordVal2 = document.getElementById('admin-login-password').value;

            try {
                const res = await fetch('/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: usernameVal, password: passwordVal2 }),
                    credentials: 'same-origin'
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Login successful! Redirecting...');
                    setTimeout(() => { window.location.href = data.redirect || '/admin'; }, 800);
                } else {
                    showToast(data.error || 'Invalid credentials.', 'error');
                    btn.disabled = false;
                    btn.innerHTML = origText;
                }
            } catch (err) {
                showToast('Network error. Please try again.', 'error');
                btn.disabled = false;
                btn.innerHTML = origText;
            }
        });
    }
});