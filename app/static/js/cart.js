/**
 * Client-side Cart Management System
 * Optimistic UI with background sync
 */

class Cart {
    constructor() {
        this.items = [];
        this.seatSelectionEnabled = false;
        this.loadSeatSelectionSetting();
    }

    async loadSeatSelectionSetting() {
        try {
            const response = await fetch('/settings/get/enable_seat_selection');
            const data = await response.json();
            if (data.success && data.value === 'true') {
                this.seatSelectionEnabled = true;
            }
        } catch (error) {
            console.error('Failed to load seat selection setting:', error);
            // Graceful degradation - seat selection remains disabled
            this.seatSelectionEnabled = false;
        }
    }

    addItem(itemId, itemName, price, quantity = 1, seatNumber = null) {
        // Optimistic UI - update immediately
        const existingIndex = this.items.findIndex(
            item => item.itemId === itemId && item.seatNumber === seatNumber
        );

        if (existingIndex !== -1) {
            this.items[existingIndex].quantity += quantity;
        } else {
            this.items.push({
                itemId,
                itemName,
                price,
                quantity,
                seatNumber
            });
        }

        this.render();
        this.showNotification(`Added ${itemName} to cart`, 'success');
    }

    removeItem(index) {
        const item = this.items[index];
        this.items.splice(index, 1);
        this.render();
        this.showNotification(`Removed ${item.itemName} from cart`, 'info');
    }

    updateQuantity(index, newQuantity) {
        if (newQuantity <= 0) {
            this.removeItem(index);
            return;
        }
        this.items[index].quantity = newQuantity;
        this.render();
    }

    updateSeat(index, seatNumber) {
        this.items[index].seatNumber = seatNumber;
        this.render();
    }

    clear() {
        this.items = [];
        this.render();
    }

    getTotal() {
        return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }

    async submitOrder(tableId) {
        if (this.items.length === 0) {
            this.showNotification('Cart is empty', 'warning');
            return false;
        }

        // Show loading state
        const submitBtn = document.getElementById('submit-cart-btn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';
        }

        try {
            const response = await fetch(`/add_order_batch/${tableId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    orders: this.items
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Order sent successfully!', 'success');
                this.clear();
                return true;
            } else {
                this.showNotification('Failed to send order: ' + (data.error || 'Unknown error'), 'danger');
                return false;
            }
        } catch (error) {
            this.showNotification('Network error: ' + error.message, 'danger');
            return false;
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Order';
            }
        }
    }

    render() {
        const cartContainer = document.getElementById('cart-container');
        if (!cartContainer) return;

        if (this.items.length === 0) {
            cartContainer.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: #64748B;">
                    <p>Cart is empty</p>
                    <p style="font-size: 0.875rem;">Add items from the menu</p>
                </div>
            `;
            return;
        }

        let html = '<div class="cart-items" style="max-height: 400px; overflow-y: auto;">';
        
        this.items.forEach((item, index) => {
            const itemTotal = item.price * item.quantity;
            html += `
                <div class="cart-item" style="margin-bottom: 0.5rem; animation: slideIn 0.3s ease-out;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600;">${item.itemName}</div>
                            <div style="font-size: 0.875rem; color: #64748B;">
                                $${item.price.toFixed(2)} × ${item.quantity}
                                ${this.seatSelectionEnabled && item.seatNumber ? ` • Seat ${item.seatNumber}` : ''}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div class="price" style="font-size: 1.125rem;">$${itemTotal.toFixed(2)}</div>
                            <div style="display: flex; gap: 0.25rem; margin-top: 0.25rem;">
                                <button onclick="cart.updateQuantity(${index}, ${item.quantity - 1})" 
                                        class="btn btn-sm" style="padding: 0.25rem 0.5rem; min-height: 32px;">-</button>
                                <button onclick="cart.updateQuantity(${index}, ${item.quantity + 1})" 
                                        class="btn btn-sm" style="padding: 0.25rem 0.5rem; min-height: 32px;">+</button>
                                <button onclick="cart.removeItem(${index})" 
                                        class="btn btn-danger btn-sm" style="padding: 0.25rem 0.5rem; min-height: 32px;">×</button>
                            </div>
                        </div>
                    </div>
                    ${this.seatSelectionEnabled ? this.renderSeatSelector(index, item.seatNumber) : ''}
                </div>
            `;
        });

        html += '</div>';

        // Total
        const total = this.getTotal();
        html += `
            <div style="border-top: 2px solid var(--bg-accent); margin-top: 1rem; padding-top: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.25rem; font-weight: 700;">Total</div>
                    <div class="price" style="font-size: 1.5rem; color: var(--indigo-primary);">$${total.toFixed(2)}</div>
                </div>
                <button id="submit-cart-btn" class="btn btn-success btn-lg w-full" onclick="cart.submitOrder(tableNumber)">
                    Send Order
                </button>
                <button class="btn btn-secondary w-full" style="margin-top: 0.5rem;" onclick="cart.clear()">
                    Clear Cart
                </button>
            </div>
        `;

        cartContainer.innerHTML = html;
    }

    renderSeatSelector(index, currentSeat) {
        const seats = [1, 2, 3, 4, 5, 6, 7, 8];
        let html = '<div style="margin-top: 0.5rem; display: flex; gap: 0.25rem; flex-wrap: wrap;">';
        html += '<span style="font-size: 0.75rem; color: #64748B; width: 100%; margin-bottom: 0.25rem;">Seat:</span>';
        
        seats.forEach(seat => {
            const isActive = currentSeat === seat;
            html += `
                <button onclick="cart.updateSeat(${index}, ${seat})" 
                        class="btn btn-sm ${isActive ? 'btn-primary' : 'btn-outline'}" 
                        style="padding: 0.25rem 0.5rem; min-height: 28px; font-size: 0.75rem;">
                    ${seat}
                </button>
            `;
        });
        
        html += '</div>';
        return html;
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: white;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-xl);
            z-index: 9999;
            animation: slideInRight 0.3s ease-out;
            max-width: 300px;
        `;

        // Color based on type
        let color = 'var(--info)';
        if (type === 'success') color = 'var(--success)';
        else if (type === 'warning') color = 'var(--warning)';
        else if (type === 'danger') color = 'var(--danger)';

        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 4px; height: 40px; background: ${color}; border-radius: 2px;"></div>
                <div>${message}</div>
            </div>
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Add animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(-20px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Initialize global cart instance
const cart = new Cart();
