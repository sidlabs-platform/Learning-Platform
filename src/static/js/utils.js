/**
 * utils.js — Shared JavaScript utilities for the Learning Platform.
 * Provides: apiFetch(), navbar toggle, flash message auto-dismiss.
 */

'use strict';

/* ---------------------------------------------------------------------------
   API Fetch Wrapper
   --------------------------------------------------------------------------- */

/**
 * Central fetch wrapper that handles JSON parsing, error status codes,
 * and provides loading-state helpers.
 *
 * @param {string} url - Relative or absolute URL to fetch.
 * @param {RequestInit} [options={}] - Fetch options (method, body, headers…).
 * @returns {Promise<any>} Parsed JSON response data.
 * @throws {Error} On non-2xx HTTP status or network failure.
 */
async function apiFetch(url, options = {}) {
    const defaultHeaders = { 'Content-Type': 'application/json' };

    const config = {
        credentials: 'same-origin',
        ...options,
        headers: {
            ...defaultHeaders,
            ...(options.headers || {}),
        },
    };

    let response;
    try {
        response = await fetch(url, config);
    } catch (networkError) {
        throw new Error(`Network error: ${networkError.message || 'Unable to reach server'}`);
    }

    // Parse body (JSON or text fallback)
    let data;
    const contentType = response.headers.get('Content-Type') || '';
    try {
        data = contentType.includes('application/json')
            ? await response.json()
            : await response.text();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const message =
            (data && (data.detail || data.message || data.error)) ||
            `HTTP ${response.status}: ${response.statusText}`;
        const err = new Error(message);
        err.status = response.status;
        err.data = data;
        throw err;
    }

    return data;
}

/* ---------------------------------------------------------------------------
   Flash Message Helpers
   --------------------------------------------------------------------------- */

/**
 * Show a temporary flash alert at the top of the page.
 *
 * @param {string} text - Message text to display.
 * @param {'success'|'error'|'warning'|'info'} [type='info'] - Alert type.
 * @param {number} [duration=4000] - Auto-dismiss delay in ms (0 = no auto-dismiss).
 */
function showFlash(text, type = 'info', duration = 4000) {
    let container = document.querySelector('.flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages container';
        container.setAttribute('role', 'alert');
        container.setAttribute('aria-live', 'polite');
        const main = document.getElementById('main-content');
        if (main) {
            main.insertAdjacentElement('afterbegin', container);
        } else {
            document.body.insertAdjacentElement('afterbegin', container);
        }
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
        <span class="alert-content">${escapeHtml(text)}</span>
        <button class="alert-close" aria-label="Dismiss message" onclick="this.closest('.alert').remove()">×</button>
    `;
    container.appendChild(alert);

    if (duration > 0) {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s';
            setTimeout(() => alert.remove(), 300);
        }, duration);
    }
}

/**
 * Escape HTML special characters to prevent XSS.
 *
 * @param {string} str - Raw string to escape.
 * @returns {string} HTML-safe string.
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(String(str)));
    return div.innerHTML;
}

/* ---------------------------------------------------------------------------
   Loading State Helpers
   --------------------------------------------------------------------------- */

/**
 * Set a button into a loading state (disables it and shows a spinner).
 *
 * @param {HTMLButtonElement} btn - Button element.
 * @param {string} [loadingText='Loading…'] - Accessible label while loading.
 */
function setButtonLoading(btn, loadingText = 'Loading…') {
    btn.disabled = true;
    btn.classList.add('loading');
    btn._originalText = btn.textContent;
    btn.setAttribute('aria-label', loadingText);
}

/**
 * Restore a button from loading state.
 *
 * @param {HTMLButtonElement} btn - Button element previously set to loading.
 */
function clearButtonLoading(btn) {
    btn.disabled = false;
    btn.classList.remove('loading');
    if (btn._originalText !== undefined) {
        btn.textContent = btn._originalText;
    }
    btn.removeAttribute('aria-label');
}

/* ---------------------------------------------------------------------------
   Navbar Toggle (Mobile)
   --------------------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');
    const navRight = document.getElementById('nav-right');

    if (toggle && (navLinks || navRight)) {
        toggle.addEventListener('click', () => {
            const isOpen = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', String(!isOpen));

            if (navLinks) navLinks.classList.toggle('open', !isOpen);
            if (navRight) navRight.classList.toggle('open', !isOpen);
        });

        // Close nav on outside click
        document.addEventListener('click', (e) => {
            if (!toggle.contains(e.target) &&
                !(navLinks && navLinks.contains(e.target)) &&
                !(navRight && navRight.contains(e.target))) {
                toggle.setAttribute('aria-expanded', 'false');
                if (navLinks) navLinks.classList.remove('open');
                if (navRight) navRight.classList.remove('open');
            }
        });

        // Close nav on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                toggle.setAttribute('aria-expanded', 'false');
                if (navLinks) navLinks.classList.remove('open');
                if (navRight) navRight.classList.remove('open');
                toggle.focus();
            }
        });
    }

    // Auto-dismiss flash messages after 5 seconds
    document.querySelectorAll('.flash-messages .alert').forEach((alert) => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Active nav link highlighting via current URL
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach((link) => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

/* ---------------------------------------------------------------------------
   Progress Bar Animator
   --------------------------------------------------------------------------- */

/**
 * Animate a progress bar fill to a given percentage.
 *
 * @param {HTMLElement} fillEl - The .progress-fill element.
 * @param {number} pct - Target percentage (0–100).
 */
function animateProgress(fillEl, pct) {
    if (!fillEl) return;
    const clamped = Math.min(100, Math.max(0, pct));
    // Delay for CSS transition to trigger
    requestAnimationFrame(() => {
        fillEl.style.width = `${clamped}%`;
    });
}

// Animate all progress bars on page load
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.progress-fill[data-pct]').forEach((el) => {
        animateProgress(el, parseFloat(el.dataset.pct));
    });
});

/* ---------------------------------------------------------------------------
   Tab Component
   --------------------------------------------------------------------------- */

/**
 * Initialize tab groups on the page.
 * Tabs expect: <button class="tab" data-target="panel-id"> and <div id="panel-id" class="tab-content">
 */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.tabs').forEach((tabGroup) => {
        const tabs = tabGroup.querySelectorAll('.tab[data-target]');
        tabs.forEach((tab) => {
            tab.addEventListener('click', () => {
                // Deactivate all tabs in group
                tabs.forEach((t) => {
                    t.classList.remove('active');
                    t.setAttribute('aria-selected', 'false');
                });
                // Hide all panels
                tabs.forEach((t) => {
                    const panel = document.getElementById(t.dataset.target);
                    if (panel) panel.classList.remove('active');
                });
                // Activate clicked tab
                tab.classList.add('active');
                tab.setAttribute('aria-selected', 'true');
                const target = document.getElementById(tab.dataset.target);
                if (target) target.classList.add('active');
            });
        });
    });
});

/* ---------------------------------------------------------------------------
   Expose globals
   --------------------------------------------------------------------------- */

window.apiFetch = apiFetch;
window.showFlash = showFlash;
window.escapeHtml = escapeHtml;
window.setButtonLoading = setButtonLoading;
window.clearButtonLoading = clearButtonLoading;
window.animateProgress = animateProgress;
