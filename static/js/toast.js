/**
 * Enhanced Toast Notification System
 * Provides a programmatic API for displaying toast notifications throughout the application
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.maxToasts = 5;
        this.defaultDuration = 6000;
        this.init();
    }

    init() {
        // Create or get toast container
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed top-20 right-4 z-50 space-y-3 w-full max-w-sm sm:right-5';
            container.setAttribute('role', 'region');
            container.setAttribute('aria-live', 'polite');
            container.setAttribute('aria-label', 'Notifications');
            document.body.appendChild(container);
        }
        this.container = container;
    }

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Type of toast: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in milliseconds (0 = no auto-dismiss)
     * @param {object} options - Additional options (icon, action, etc.)
     */
    show(message, type = 'info', duration = null, options = {}) {
        const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const toastDuration = duration !== null ? duration : this.defaultDuration;

        // Limit number of toasts
        if (this.toasts.length >= this.maxToasts) {
            const oldestToast = this.toasts.shift();
            this.remove(oldestToast.id);
        }

        // Create toast element
        const toast = this.createToastElement(toastId, message, type, options);
        
        // Add to container
        this.container.appendChild(toast);
        this.toasts.push({ id: toastId, element: toast });

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.add('toast-enter');
        });

        // Auto-dismiss if duration is set
        if (toastDuration > 0) {
            setTimeout(() => {
                this.remove(toastId);
            }, toastDuration);
        }

        return toastId;
    }

    createToastElement(id, message, type, options) {
        const toast = document.createElement('div');
        toast.id = id;
        toast.className = 'toast-message max-w-sm w-full bg-white shadow-xl rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-atomic', 'true');

        // Type-specific styling
        const typeConfig = {
            success: {
                border: 'border-green-400',
                bg: 'bg-green-50/30',
                icon: `<svg class="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>`,
                textColor: 'text-green-800'
            },
            error: {
                border: 'border-red-400',
                bg: 'bg-red-50/30',
                icon: `<svg class="h-6 w-6 text-red-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>`,
                textColor: 'text-red-800'
            },
            warning: {
                border: 'border-yellow-400',
                bg: 'bg-yellow-50/30',
                icon: `<svg class="h-6 w-6 text-yellow-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>`,
                textColor: 'text-yellow-800'
            },
            info: {
                border: 'border-blue-400',
                bg: 'bg-blue-50/30',
                icon: `<svg class="h-6 w-6 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>`,
                textColor: 'text-blue-800'
            }
        };

        const config = typeConfig[type] || typeConfig.info;
        const customIcon = options.icon || config.icon;

        toast.innerHTML = `
            <div class="p-4 border-l-4 ${config.border} ${config.bg}">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        ${customIcon}
                    </div>
                    <div class="ml-3 w-0 flex-1 pt-0.5">
                        ${options.title ? `<p class="text-sm font-semibold ${config.textColor} mb-1">${this.escapeHtml(options.title)}</p>` : ''}
                        <p class="text-sm font-medium ${config.textColor}">
                            ${this.escapeHtml(message)}
                        </p>
                        ${options.action ? `
                            <div class="mt-3">
                                <button onclick="${options.action.onClick}" class="text-xs font-medium ${config.textColor} underline hover:opacity-80">
                                    ${this.escapeHtml(options.action.label)}
                                </button>
                            </div>
                        ` : ''}
                    </div>
                    <button type="button" 
                            class="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-md p-1"
                            onclick="window.toast.remove('${id}')"
                            aria-label="Close notification">
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>
        `;

        // Add click handler for action
        if (options.action) {
            const actionButton = toast.querySelector('button[onclick*="action"]');
            if (actionButton) {
                actionButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (typeof options.action.onClick === 'function') {
                        options.action.onClick();
                    }
                });
            }
        }

        return toast;
    }

    /**
     * Remove a toast by ID
     */
    remove(id) {
        const toast = document.getElementById(id);
        if (toast) {
            toast.classList.add('toast-exit');
            setTimeout(() => {
                toast.remove();
                this.toasts = this.toasts.filter(t => t.id !== id);
                
                // Update aria-live if no more toasts
                if (this.container.children.length === 0) {
                    this.container.setAttribute('aria-live', 'off');
                    setTimeout(() => this.container.setAttribute('aria-live', 'polite'), 100);
                }
            }, 300);
        }
    }

    /**
     * Clear all toasts
     */
    clear() {
        this.toasts.forEach(toast => this.remove(toast.id));
    }

    /**
     * Convenience methods
     */
    success(message, duration = null, options = {}) {
        return this.show(message, 'success', duration, options);
    }

    error(message, duration = null, options = {}) {
        return this.show(message, 'error', duration || 8000, options); // Errors stay longer
    }

    warning(message, duration = null, options = {}) {
        return this.show(message, 'warning', duration, options);
    }

    info(message, duration = null, options = {}) {
        return this.show(message, 'info', duration, options);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize toast system when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.toast = new ToastNotification();
    });
} else {
    window.toast = new ToastNotification();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ToastNotification;
}

