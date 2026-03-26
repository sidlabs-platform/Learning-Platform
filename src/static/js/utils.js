/**
 * utils.js — Shared frontend utilities for Learning Platform
 *
 * Provides:
 *   - apiFetch(url, options)  — centralised fetch wrapper with JSON handling
 *   - showToast(message, type) — in-page toast notifications
 *   - formatDate(isoString)   — human-readable date formatting
 *   - debounce(fn, delay)     — function debouncing
 *   - initTabs(container)     — tab component initialiser
 */

/* ============================================================
   Configuration
   ============================================================ */

/** Base path for all API calls. Empty string means same origin. */
const API_BASE = '';

/* ============================================================
   1. API Fetch Wrapper
   ============================================================ */

/**
 * Centralised fetch wrapper that:
 *   - Prepends API_BASE to relative URLs
 *   - Sets Content-Type: application/json for JSON bodies
 *   - Parses JSON responses automatically
 *   - Throws a descriptive Error on HTTP error status codes
 *   - Throws a descriptive Error on network failures
 *
 * @param {string} url     - URL path (e.g. "/api/v1/courses"). Absolute URLs pass through.
 * @param {RequestInit} [options={}] - fetch() options (method, body, headers, etc.)
 * @returns {Promise<any>}  Parsed JSON response body.
 *
 * @throws {ApiError} On HTTP 4xx / 5xx responses (includes status + body).
 * @throws {Error}    On network failure or JSON parse errors.
 *
 * @example
 *   const courses = await apiFetch('/api/v1/courses');
 *   const created = await apiFetch('/api/v1/courses', {
 *     method: 'POST',
 *     body: JSON.stringify({ title: 'My Course' })
 *   });
 */
async function apiFetch(url, options = {}) {
    // Resolve URL
    const resolvedUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;

    // Default headers
    const headers = Object.assign({ 'Accept': 'application/json' }, options.headers || {});

    // Auto-set Content-Type for JSON bodies
    if (options.body && typeof options.body === 'string') {
        headers['Content-Type'] = 'application/json';
    }

    let response;
    try {
        response = await fetch(resolvedUrl, Object.assign({}, options, { headers }));
    } catch (networkError) {
        throw new Error(`Network error: unable to reach ${resolvedUrl}. Please check your connection.`);
    }

    // Handle empty responses (e.g. 204 No Content)
    if (response.status === 204) {
        return null;
    }

    // Parse response body (try JSON first, fall back to text)
    let body;
    const contentType = response.headers.get('content-type') || '';
    try {
        if (contentType.includes('application/json')) {
            body = await response.json();
        } else {
            body = await response.text();
        }
    } catch (_) {
        body = null;
    }

    // Throw on error status codes
    if (!response.ok) {
        const message = (body && body.detail)
            ? body.detail
            : (typeof body === 'string' && body.length < 200)
                ? body
                : `Request failed with status ${response.status}`;
        const error = new ApiError(message, response.status, body);
        throw error;
    }

    return body;
}

/**
 * Custom error class for API errors.
 * Carries HTTP status code and raw response body.
 */
class ApiError extends Error {
    /**
     * @param {string} message - Human-readable error message.
     * @param {number} status  - HTTP status code.
     * @param {any}    body    - Raw parsed response body.
     */
    constructor(message, status, body) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.body = body;
    }
}

/* ============================================================
   2. Toast Notifications
   ============================================================ */

/**
 * Display a toast notification message.
 *
 * @param {string} message  - Text to display.
 * @param {'success'|'danger'|'warning'|'info'} [type='info'] - Visual variant.
 * @param {number} [duration=4000] - Auto-dismiss after ms. 0 = never auto-dismiss.
 */
function showToast(message, type = 'info', duration = 4000) {
    // Ensure container exists
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        container.setAttribute('aria-live', 'polite');
        container.setAttribute('aria-atomic', 'false');
        document.body.appendChild(container);
    }

    // Build toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible toast`;
    toast.setAttribute('role', 'alert');

    const icons = { success: '✓', danger: '✕', warning: '⚠', info: 'ℹ' };
    toast.innerHTML = `
        <span class="alert-icon" aria-hidden="true">${icons[type] || 'ℹ'}</span>
        <span>${escapeHtml(message)}</span>
        <button class="alert-close" onclick="this.closest('.toast').remove()" aria-label="Dismiss">×</button>
    `;

    container.appendChild(toast);

    // Auto-dismiss
    if (duration > 0) {
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.2s ease';
                setTimeout(() => toast.remove(), 220);
            }
        }, duration);
    }
}

/* ============================================================
   3. HTML Escape (XSS prevention)
   ============================================================ */

/**
 * Escape a string for safe insertion into HTML content.
 * Prevents XSS when inserting user-controlled text via innerHTML.
 *
 * @param {string} str - Raw string to escape.
 * @returns {string}   HTML-safe string.
 */
function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/* ============================================================
   4. Date Formatting
   ============================================================ */

/**
 * Format an ISO 8601 date string into a human-readable locale string.
 *
 * @param {string} isoString - ISO date string (e.g. "2024-03-15T10:30:00Z").
 * @param {object} [opts]    - Intl.DateTimeFormat options.
 * @returns {string}           Formatted date string, or empty string on error.
 */
function formatDate(isoString, opts = { year: 'numeric', month: 'short', day: 'numeric' }) {
    if (!isoString) return '';
    try {
        return new Intl.DateTimeFormat(navigator.language, opts).format(new Date(isoString));
    } catch (_) {
        return isoString;
    }
}

/**
 * Return a relative time string (e.g. "3 hours ago", "just now").
 *
 * @param {string} isoString - ISO date string.
 * @returns {string}           Relative time string.
 */
function timeAgo(isoString) {
    if (!isoString) return '';
    try {
        const seconds = Math.round((Date.now() - new Date(isoString).getTime()) / 1000);
        if (seconds < 60) return 'just now';
        const intervals = [
            [31536000, 'year'],
            [2592000,  'month'],
            [86400,    'day'],
            [3600,     'hour'],
            [60,       'minute'],
        ];
        for (const [secs, label] of intervals) {
            const count = Math.floor(seconds / secs);
            if (count >= 1) return `${count} ${label}${count > 1 ? 's' : ''} ago`;
        }
        return 'just now';
    } catch (_) {
        return '';
    }
}

/* ============================================================
   5. Debounce
   ============================================================ */

/**
 * Returns a debounced version of the provided function.
 *
 * @param {Function} fn    - Function to debounce.
 * @param {number}   delay - Milliseconds to delay.
 * @returns {Function}       Debounced function.
 */
function debounce(fn, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

/* ============================================================
   6. Tab Component Initialiser
   ============================================================ */

/**
 * Initialise a tab group inside a container element.
 *
 * Expected HTML structure:
 *   <div data-tabs>
 *     <div class="tabs">
 *       <ul class="tabs__list">
 *         <li class="tabs__item active"><a href="#panel1" class="tab-link active">Tab 1</a></li>
 *         <li class="tabs__item"><a href="#panel2" class="tab-link">Tab 2</a></li>
 *       </ul>
 *     </div>
 *     <div id="panel1" class="tab-panel active">...</div>
 *     <div id="panel2" class="tab-panel">...</div>
 *   </div>
 *
 * @param {HTMLElement} [container=document] - Root element to search within.
 */
function initTabs(container = document) {
    const tabContainers = container.querySelectorAll('[data-tabs]');
    tabContainers.forEach(function (tabContainer) {
        const links = tabContainer.querySelectorAll('.tab-link');
        links.forEach(function (link) {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = link.getAttribute('href');
                if (!targetId || !targetId.startsWith('#')) return;

                // Deactivate all links and panels within this group
                links.forEach(function (l) {
                    l.classList.remove('active');
                    l.closest('.tabs__item') && l.closest('.tabs__item').classList.remove('active');
                });
                tabContainer.querySelectorAll('.tab-panel').forEach(function (p) {
                    p.classList.remove('active');
                });

                // Activate selected
                link.classList.add('active');
                link.closest('.tabs__item') && link.closest('.tabs__item').classList.add('active');
                const panel = tabContainer.querySelector(targetId);
                if (panel) panel.classList.add('active');
            });
        });
    });
}

/* ============================================================
   7. Progress Bar Updater
   ============================================================ */

/**
 * Update a progress bar element's width and ARIA attributes.
 *
 * @param {HTMLElement} barEl       - The `.progress-bar` element.
 * @param {number}      percentage  - 0–100 percentage value.
 */
function updateProgressBar(barEl, percentage) {
    const pct = Math.max(0, Math.min(100, Math.round(percentage)));
    barEl.style.width = `${pct}%`;
    barEl.setAttribute('aria-valuenow', String(pct));
}

/* ============================================================
   8. Form Utilities
   ============================================================ */

/**
 * Serialize a form element to a plain object.
 *
 * @param {HTMLFormElement} form - The form element.
 * @returns {Object}               Key-value pairs of form data.
 */
function serializeForm(form) {
    const data = {};
    new FormData(form).forEach(function (value, key) {
        if (key in data) {
            // Multiple values — convert to array
            if (!Array.isArray(data[key])) data[key] = [data[key]];
            data[key].push(value);
        } else {
            data[key] = value;
        }
    });
    return data;
}

/**
 * Display a field-level validation error on a form input.
 *
 * @param {HTMLElement} inputEl - The input element.
 * @param {string}      message - Error message to display.
 */
function showFieldError(inputEl, message) {
    inputEl.classList.add('is-invalid');
    let errEl = inputEl.parentNode.querySelector('.form-error-message');
    if (!errEl) {
        errEl = document.createElement('p');
        errEl.className = 'form-error-message';
        inputEl.parentNode.appendChild(errEl);
    }
    errEl.textContent = message;
}

/**
 * Clear validation errors on a form input.
 *
 * @param {HTMLElement} inputEl - The input element.
 */
function clearFieldError(inputEl) {
    inputEl.classList.remove('is-invalid');
    const errEl = inputEl.parentNode.querySelector('.form-error-message');
    if (errEl) errEl.remove();
}

/**
 * Clear all validation errors within a form.
 *
 * @param {HTMLFormElement} form - The form element.
 */
function clearFormErrors(form) {
    form.querySelectorAll('.is-invalid').forEach(function (el) {
        clearFieldError(el);
    });
}

/* ============================================================
   9. Loading State Helpers
   ============================================================ */

/**
 * Set a button into a loading state (disables, shows spinner text).
 *
 * @param {HTMLButtonElement} btnEl         - The button element.
 * @param {string}            [label='...'] - Accessible text while loading.
 */
function setBtnLoading(btnEl, label = 'Loading…') {
    btnEl.disabled = true;
    btnEl.dataset.originalText = btnEl.textContent;
    btnEl.classList.add('btn-loading');
    btnEl.setAttribute('aria-label', label);
}

/**
 * Restore a button from loading state.
 *
 * @param {HTMLButtonElement} btnEl - The button element.
 */
function setBtnReady(btnEl) {
    btnEl.disabled = false;
    if (btnEl.dataset.originalText) {
        btnEl.textContent = btnEl.dataset.originalText;
        delete btnEl.dataset.originalText;
    }
    btnEl.classList.remove('btn-loading');
    btnEl.removeAttribute('aria-label');
}

/* ============================================================
   10. DOM Ready
   ============================================================ */

/**
 * Execute a callback once the DOM is ready.
 *
 * @param {Function} fn - Callback to run.
 */
function onDOMReady(fn) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fn);
    } else {
        fn();
    }
}

// Auto-initialise tabs on DOMContentLoaded
onDOMReady(function () {
    initTabs(document);
});

// Expose public API to global scope
window.apiFetch       = apiFetch;
window.ApiError       = ApiError;
window.showToast      = showToast;
window.escapeHtml     = escapeHtml;
window.formatDate     = formatDate;
window.timeAgo        = timeAgo;
window.debounce       = debounce;
window.initTabs       = initTabs;
window.updateProgressBar = updateProgressBar;
window.serializeForm  = serializeForm;
window.showFieldError = showFieldError;
window.clearFieldError= clearFieldError;
window.clearFormErrors= clearFormErrors;
window.setBtnLoading  = setBtnLoading;
window.setBtnReady    = setBtnReady;
window.onDOMReady     = onDOMReady;
