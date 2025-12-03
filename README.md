# Premium Point of Sale (PoS) System

A high-performance, visually stunning, and feature-rich Point of Sale system built with Flask. Features a modern design system, real-time updates, and advanced order management capabilities.

## 🚀 Features

### Architecture & Performance
- **Optimized SQLite** with WAL (Write-Ahead Logging) for concurrent read/write operations
- **Threading enabled** for simultaneous requests (e.g., waiter ordering while kitchen updates tickets)
- **Comprehensive database indexing** on high-frequency columns for optimal performance
- **Binds to 0.0.0.0** allowing access from local network devices (phones, tablets, PCs)

### Premium Design System - "Modern Slate & Indigo"
- **CSS Variables** for unified theming across all pages
- **Glassmorphism effects** on sticky headers and navigation
- **Smooth animations** with physics-based transitions
- **Responsive layouts** optimized for mobile and desktop
- **Tactile interactions** with hover lift effects and press feedback
- **Breathing status indicators** for active tables

### Advanced Ordering System
- **Client-side cart** with optimistic UI updates
- **Batch order submission** - accumulate items before sending
- **Seat assignment** capability (configurable)
- **Order editing** - modify cart before submission
- **No page reloads** - all actions use AJAX/Fetch

### Table Management
- **Transfer orders** between tables
- **Order voiding** with optional PIN protection
- **Real-time status** updates with breathing indicators
- **Guest count tracking**

### Specialized Views

#### Kitchen View
- Shows **food items only**
- **Time-based color coding**: Green → Yellow → Red
- **Priority ordering** based on wait time
- Auto-refresh every 5 seconds

#### Bar View
- Shows **drink items only**
- **Auto-grouping** of identical drinks (e.g., "3x Mojito")
- **Table breakdown** showing quantity per table
- Optimized for high-volume drink preparation

### Security & Management
- **Master PIN system** for protected features
- **PIN-protected dashboard** with real-time statistics
- **Digital receipts** generation and storage
- **Configurable settings** for features and security
- **Activity logging**

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd postest
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run database migration** (if upgrading from an older version)
```bash
python migrate_database.py
```

4. **Start the application**
```bash
python run.py
```

The application will be available at:
- Local: `http://127.0.0.1:5000`
- Network: `http://<your-ip>:5000`

## 🎨 Design System

### Color Palette
- **Background**: Off-white (#F8FAFC) for light mode
- **Primary**: Indigo (#6366F1)
- **Success**: Emerald (#10B981)
- **Warning**: Amber (#F59E0B)
- **Danger**: Red (#EF4444)
- **Dark Elements**: Deep Slate (#0F172A)

### Typography
- **Font**: Inter or Plus Jakarta Sans (Google Fonts)
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold), 800 (heavy)
- **Numbers**: Heavy weight (800) for prices and quantities

### Components
- **Cards**: 12px rounded corners with soft elevation shadows
- **Buttons**: Minimum 48px tap targets, lift on hover, press on click
- **Animations**: 200-400ms with cubic-bezier easing
- **Spacing**: Consistent 8px base unit

## 📱 Usage

### Waiter Flow
1. Navigate to **Waiter** view
2. Select a table (red = available, green = occupied)
3. Set number of guests (first time)
4. Browse menu by category
5. Add items to cart
6. Optionally assign seats to items
7. Submit batch order
8. Mark items for "Main Away" when ready
9. Generate receipt when complete
10. Close table

### Kitchen Flow
1. Navigate to **Kitchen** view
2. View all food orders with table numbers
3. Orders color-coded by wait time:
   - **Green**: Fresh (<10 min)
   - **Yellow**: Cooking (10-20 min)
   - **Red**: Urgent (>20 min)
4. Mark items as done when complete

### Bar Flow
1. Navigate to **Bar** view
2. View grouped drink orders
3. See quantity breakdown by table
4. Mark individual table drinks as complete

### Manager Flow
1. Navigate to **Manager Interface**
2. Configure number of tables
3. Add/remove menu items
4. Access **Settings** for:
   - Master PIN setup
   - Feature toggles (seat selection, floor plan mode)
   - Dashboard statistics
   - Security settings

## ⚙️ Configuration

### Settings Options
- **Master PIN**: Set a PIN for protected features
- **Require PIN for voiding**: Toggle PIN requirement for order voids
- **Enable seat assignment**: Allow waiters to assign seats to orders
- **Floor Plan Mode**: Choose between Basic, Detailed, or Status views

### API Endpoints

#### Order Management
- `POST /add_order_batch/<tableId>` - Submit multiple orders
- `POST /void_order/<orderId>` - Void an order (PIN protected)
- `GET /checker/orders/kitchen_enhanced` - Enhanced kitchen orders
- `GET /checker/orders/bar_enhanced` - Enhanced bar orders

#### Table Management
- `GET /modify_table/<tableId>` - Set guest count
- `GET /close_table/<tableId>` - Close table and clear orders
- `POST /transfer_table/<from>/<to>` - Transfer orders between tables

#### Settings & Auth
- `POST /auth/setup_pin` - Setup master PIN
- `POST /auth/verify_pin` - Verify PIN
- `GET /settings/get/<key>` - Get setting value
- `POST /settings/set` - Set setting value
- `GET /settings/all` - Get all settings

#### Dashboard
- `GET /dashboard/stats` - Get real-time statistics
- `GET /receipt/generate/<tableId>` - Generate receipt
- `POST /receipt/save/<tableId>` - Save receipt to database

## 🔧 Database Schema

### Tables
- **tables**: Table status and guest count
- **orders**: Order items with status tracking
- **menu**: Menu items with pricing and categories
- **settings**: Application settings
- **receipts**: Saved receipt records

### Indexes
- `orders(table_id, status)` - Compound index for filtering
- `orders(created_at, status)` - Time-based queries
- Single indexes on frequently queried columns

## 🎯 Performance Optimizations

1. **WAL Mode**: Allows concurrent reads during writes
2. **Database Indexing**: Optimized query performance
3. **Optimistic UI**: Immediate feedback, background sync
4. **Auto-refresh**: Kitchen/Bar views update every 5 seconds
5. **Efficient grouping**: Bar view groups identical items
6. **Minimal DOM updates**: JavaScript efficiently updates only changed elements

## 🔒 Security Features

- **PIN Protection**: Secure access to sensitive features
- **Order Voiding**: Requires PIN verification (configurable)
- **Settings Protection**: PIN-gated configuration access
- **Session Management**: Secure authentication flow

## 📄 License

This is a school project.

## 🙏 Acknowledgments

Built with:
- Flask 3.0.0
- SQLAlchemy 2.0.23
- Modern CSS3 with variables
- Vanilla JavaScript (no frameworks)

Design inspired by modern UI/UX principles with emphasis on performance and usability.
