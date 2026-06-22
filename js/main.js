// 22PM - Drop-Servicing AI Workflows
// Main JavaScript for client interactions, animations, and form handling

document.addEventListener('DOMContentLoaded', () => {

    // ===== SMOOTH SCROLL FOR NAV =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ===== NAVBAR SCROLL EFFECT =====
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        if (currentScroll > 100) {
            navbar.style.background = 'rgba(10, 10, 15, 0.95)';
            navbar.style.borderBottomColor = 'rgba(108, 92, 231, 0.3)';
        } else {
            navbar.style.background = 'rgba(10, 10, 15, 0.8)';
            navbar.style.borderBottomColor = 'rgba(108, 92, 231, 0.2)';
        }
        lastScroll = currentScroll;
    });

    // ===== SCROLL REVEAL ANIMATIONS =====
    const revealElements = document.querySelectorAll('.service-card, .step, .pricing-card, .stack-item');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    revealElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        revealObserver.observe(el);
    });

    // ===== CONTACT FORM HANDLING =====
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = '⏳ Sending...';
            submitBtn.disabled = true;

            // Collect form data
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData.entries());

            // Simulate sending (replace with actual webhook/API endpoint)
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Success state
            submitBtn.textContent = '✅ Sent Successfully!';
            submitBtn.style.background = 'linear-gradient(135deg, #00cec9, #00b894)';

            // Reset form
            contactForm.reset();

            setTimeout(() => {
                submitBtn.textContent = originalText;
                submitBtn.style.background = '';
                submitBtn.disabled = false;
            }, 3000);
        });
    }

    // ===== SERVICE CARD INTERACTIONS =====
    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            // Add subtle parallax to card icon
            const icon = card.querySelector('.card-icon');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotate(-5deg)';
                icon.style.transition = 'transform 0.3s ease';
            }
        });

        card.addEventListener('mouseleave', () => {
            const icon = card.querySelector('.card-icon');
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
        });
    });

    // ===== PRICING HIGHLIGHT =====
    const pricingCards = document.querySelectorAll('.pricing-card');
    pricingCards.forEach(card => {
        card.addEventListener('click', () => {
            // Scroll to contact section
            document.querySelector('#contact').scrollIntoView({ behavior: 'smooth' });
        });
    });

    // ===== COUNTER ANIMATION FOR STATS =====
    function animateCounter(element, target, suffix = '') {
        let current = 0;
        const increment = target / 60;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current) + suffix;
        }, 20);
    }

    // ===== WORKFLOW ANIMATION NODE SEQUENCING =====
    const workflowNodes = document.querySelectorAll('.workflow-animation .node, .workflow-animation .arrow');
    workflowNodes.forEach((node, index) => {
        node.style.opacity = '0';
        node.style.transform = 'translateY(10px)';
        setTimeout(() => {
            node.style.opacity = '1';
            node.style.transform = 'translateY(0)';
            node.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        }, 300 * (index + 1));
    });

    // ===== MOBILE MENU TOGGLE (simple hamburger fallback) =====
    // Since nav is hidden on mobile, we add a minimal toggle
    const logo = document.querySelector('.logo');
    const navLinks = document.querySelector('.nav-links');

    if (window.innerWidth <= 768) {
        logo.addEventListener('click', () => {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
            navLinks.style.flexDirection = 'column';
            navLinks.style.position = 'absolute';
            navLinks.style.top = '100%';
            navLinks.style.left = '0';
            navLinks.style.right = '0';
            navLinks.style.background = 'rgba(10, 10, 15, 0.98)';
            navLinks.style.padding = '20px';
            navLinks.style.borderBottom = '1px solid rgba(108, 92, 231, 0.2)';
            navLinks.style.gap = '16px';
        });
    }

    // ===== CONSOLE BRANDING =====
    console.log('%c 22PM ', 'background: linear-gradient(135deg, #6c5ce7, #00cec9); color: white; font-size: 20px; font-weight: bold; padding: 8px 16px; border-radius: 4px;');
    console.log('%c Drop-servicing AI Workflows — Zero Capital, Infinite Ambition.', 'color: #a0a0b8; font-size: 14px;');
    console.log('%c 👉 hello@22pm.work', 'color: #6c5ce7; font-size: 12px;');

});