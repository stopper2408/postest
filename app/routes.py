from flask import render_template, jsonify, request
from app import app
import json
from app.tables import *



#error handling

@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")



# web page routes

@app.route('/')
@app.route('/login')
def index():
    return render_template('login.html')


@app.route('/waiter_table_view')
def waiter_table_view():
    return render_template('waiter_table_view.html')


@app.route('/kitchen')
def kitchen():
    return render_template('kitchen_new.html')


@app.route('/bar')
def bar():
    return render_template('bar_new.html')


@app.route('/table_view/<int:tableNumber>')
def table_view(tableNumber):
    return render_template('table_view_new.html', tableNumber=tableNumber)

@app.route('/manager_interface')
def manager_interface():
    return render_template('manager_interface.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')
















# action paths
@app.route('/modify_table/<int:tableId>')
def modify_table(tableId):
    tempValueOfNumberOfGuests = request.args.get('numberOfGuests')
    with Session(engine) as session:
        table = session.get(Table, tableId)
        table.status = True
        table.numberOfGuests = tempValueOfNumberOfGuests
        session.commit()
        return jsonify(success=True)    

@app.route('/add_order/<int:tableId>')
def add_order(tableId):
    itemId = request.args.get('itemId')
    quantity = request.args.get('quantity')
    with Session(engine) as session:
        menu_item = session.get(MenuItems, itemId)
        if menu_item.needToBeMainAway == False:
            order_status = 1
        else:
            order_status = 0

            
        order = Order(
            table_id=tableId,
            item_id=itemId,
            quantity=quantity,
            status=order_status
        )
        session.add(order)
        session.commit()
        return jsonify(success=True)


@app.route('/close_table/<int:tableId>')
def close_table(tableId):
    with Session(engine) as session:
        table = session.get(Table, tableId)
        table.status = False
        table.numberOfGuests = 0
        stmt = Select(Order).where(Order.table_id == tableId)
        tableOrdersTemp= session.execute(stmt).scalars().all()
        for order in tableOrdersTemp:
            session.delete(order)
        session.commit()
        return jsonify(success=True)
    

@app.route('/main_away_order/<int:tableID>')
def main_away_order(tableID):
    with Session(engine) as session:
        stmt = Select(Order).join(Order.item).where(Order.table_id == tableID, MenuItems.needToBeMainAway == True, Order.status == 0)
        ordersToMainAway = session.execute(stmt).scalars().all()
        for order in ordersToMainAway:
            order.status = 1
        session.commit()
    return jsonify(success=True)


@app.route('/complete_order/<int:orderID>')
def complete_order(orderID):
    with Session(engine) as session:
        order = session.get(Order, orderID)
        order.status = 2
        session.commit()
    return jsonify(success=True)















#checking paths

@app.route('/checker/total_number_of_tables')
def checker_total_number_of_tables():
    with Session(engine) as session:
        stmt = Select(Table)
        totalNumberOfTablesTemp = session.execute(stmt).scalars().all()
        totalNumberOfTablesTemp = len(totalNumberOfTablesTemp)
    return jsonify(success=True, number_of_tables=totalNumberOfTablesTemp)

@app.route('/checker/tables/')
def checker_tables():
    stmt = Select(Table)
    with Session(engine) as session:
        allTablesValuesTemp= session.execute(stmt).scalars().all()
        allTablesValuesTemp = [
            {
                "id": table.id,
                "status": table.status,
                "guests": table.numberOfGuests
            }
            for table in allTablesValuesTemp
        ]
    return jsonify(allTablesValuesTemp)


@app.route('/checker/tables/<int:checkerId>')
def checker_tables_specific(checkerId):
    stmt = Select(Table).where(Table.id == checkerId)
    with Session(engine) as session:
        tableTemp= session.execute(stmt).scalar_one()
        tableTemp = {
            "id": tableTemp.id,
            "status": tableTemp.status,
            "guests": tableTemp.numberOfGuests
        }
    return jsonify(tableTemp)


@app.route('/checker/orders/<int:tableID>')
def return_table_orders(tableID):
    stmt = Select(Order).where(Order.table_id == tableID)
    with Session(engine) as session:
        tableOrdersTemp= session.execute(stmt).scalars().all()
        tableOrdersTemp = [
            {
                "id": order.id,
                "item_id": order.item_id,
                "item_name": order.item.name,
                "quantity": order.quantity,
                "status": order.status,
                "price": order.item.price
            }
            for order in tableOrdersTemp
        ]
    return jsonify(tableOrdersTemp)

@app.route('/checker/menu_items/')
def return_menu_items():
    stmt = Select(MenuItems)
    with Session(engine) as session:
        itemsOnMenuTemp = session.execute(stmt).scalars().all()
        itemsOnMenuTemp = [
            {
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "category": item.category,
                "subcategory": item.subcategory
            }
            for item in itemsOnMenuTemp
        ]
        return jsonify(itemsOnMenuTemp)
    
@app.route('/checker/orders/<string:typeOfRequest>')
def return_order_status_per_place(typeOfRequest):
    if typeOfRequest == 'kitchen':
        stmt = Select(Order).join(Order.item).where(MenuItems.place_to_go == 'kitchen')
    elif typeOfRequest == 'bar':
        stmt = Select(Order).join(Order.item).where(MenuItems.place_to_go == 'bar')
    else:
        return jsonify("Error")
    
    with Session(engine) as session:
        returnOrdersTemp= session.execute(stmt).scalars().all()
        returnOrdersTemp = [
            {
                "id": orderItem.id,
                "name": orderItem.item.name,
                "quantityOfOrder": orderItem.quantity,
                "status": orderItem.status,
                "tableID": orderItem.table_id
            }
            for orderItem in returnOrdersTemp
        ]
    return jsonify(returnOrdersTemp)





# THIS WILL BE THE MANAGER INTERFACE PATHS

@app.route('/manager/add_menu_item')
def manager_add_menu_item():
    itemName = request.args.get('name', type=str)
    itemPrice = request.args.get('price', type=float)
    itemCategory = request.args.get('category', type=str)
    itemSubcategory = request.args.get('subcategory', type=str) or None
    needToBeMainAway = request.args.get('need_to_be_main_away', default='false').lower() == 'true' # this will make it js bool and if there is an input then it will be true
    itemPlaceToGo = request.args.get('place_to_go', type=str)

    if not itemName or not itemPrice or not itemCategory or not itemPlaceToGo: # this is some validation to see if the essential strings are there
        return jsonify(success=False)
    
    if itemSubcategory == '':
        itemSubcategory = None
    if itemPlaceToGo not in ['kitchen', 'bar']:
        return jsonify(success=False)
    if itemPrice < 0.01 or itemPrice > 1000.00 or round(itemPrice * 100, 2) % 1 != 0: # this will check if there are 2 digits after the decimal point
        return jsonify(success=False) # there will be the js that makes it 2 decimal points if it is 12.3 for example
    


    with Session(engine) as session:
        menu_item = MenuItems(
            name=itemName,
            price=itemPrice,
            category=itemCategory,
            subcategory=itemSubcategory,
            needToBeMainAway=needToBeMainAway,
            place_to_go=itemPlaceToGo
        )
        session.add(menu_item)
        session.commit()
        return jsonify(success=True)



@app.route('/manager/delete_menu_item/<int:itemId>')
def manager_delete_menu_item(itemId):
    with Session(engine) as session:
        session.execute(delete(Order).where(Order.item_id == itemId))
        menu_item = session.get(MenuItems, itemId)
        if not menu_item:
            return jsonify(success=False)
        session.delete(menu_item)
        session.commit()
        return jsonify(success=True)


@app.route('/manager/number_of_tables/<int:numberOfTables>')
def number_of_tables(numberOfTables):
        with Session(engine) as session:
            session.execute(delete(Order))
            session.execute(delete(Table))
            for i in range(1, numberOfTables + 1):
                table = Table(id=i, status=False, numberOfGuests=0)
                session.add(table)
            session.commit()
            return jsonify(success=True)


# ========================================
# NEW ADVANCED FEATURES
# ========================================

# Batch Order Submission (Cart functionality)
@app.route('/add_order_batch/<int:tableId>', methods=['POST'])
def add_order_batch(tableId):
    """Submit multiple orders at once from the cart"""
    try:
        data = request.get_json()
        orders = data.get('orders', [])
        
        with Session(engine) as session:
            for order_data in orders:
                menu_item = session.get(MenuItems, order_data['itemId'])
                if not menu_item:
                    continue
                    
                order_status = 1 if not menu_item.needToBeMainAway else 0
                
                order = Order(
                    table_id=tableId,
                    item_id=order_data['itemId'],
                    quantity=order_data['quantity'],
                    status=order_status,
                    seat_number=order_data.get('seatNumber')
                )
                session.add(order)
            session.commit()
            return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


# Void Order with PIN check
@app.route('/void_order/<int:orderId>', methods=['POST'])
def void_order(orderId):
    """Void an order with optional PIN verification"""
    try:
        data = request.get_json()
        pin = data.get('pin')
        
        # Check if PIN is required
        with Session(engine) as session:
            pin_required_setting = session.execute(
                Select(Settings).where(Settings.key == 'require_pin_for_void')
            ).scalar_one_or_none()
            
            if pin_required_setting and pin_required_setting.value == 'true':
                # Verify PIN
                master_pin_setting = session.execute(
                    Select(Settings).where(Settings.key == 'master_pin')
                ).scalar_one_or_none()
                
                if not master_pin_setting or master_pin_setting.value != pin:
                    return jsonify(success=False, error='Invalid PIN')
            
            # Void the order
            order = session.get(Order, orderId)
            if order:
                order.voided = True
                session.commit()
                return jsonify(success=True)
            return jsonify(success=False, error='Order not found')
    except Exception as e:
        return jsonify(success=False, error=str(e))


# Transfer Table
@app.route('/transfer_table/<int:fromTableId>/<int:toTableId>', methods=['POST'])
def transfer_table(fromTableId, toTableId):
    """Transfer all orders from one table to another"""
    try:
        with Session(engine) as session:
            from_table = session.get(Table, fromTableId)
            to_table = session.get(Table, toTableId)
            
            if not from_table or not to_table:
                return jsonify(success=False, error='Table not found')
            
            # Transfer orders
            stmt = Select(Order).where(Order.table_id == fromTableId, Order.voided.is_(False))
            orders = session.execute(stmt).scalars().all()
            
            for order in orders:
                order.table_id = toTableId
            
            # Update table statuses
            to_table.status = True
            to_table.numberOfGuests += from_table.numberOfGuests
            from_table.status = False
            from_table.numberOfGuests = 0
            
            session.commit()
            return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


# Settings Management
@app.route('/settings/get/<string:key>')
def get_setting(key):
    """Get a specific setting value"""
    with Session(engine) as session:
        setting = session.execute(
            Select(Settings).where(Settings.key == key)
        ).scalar_one_or_none()
        
        if setting:
            return jsonify(success=True, value=setting.value)
        return jsonify(success=False, value=None)


@app.route('/settings/set', methods=['POST'])
def set_setting():
    """Set or update a setting"""
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        
        with Session(engine) as session:
            setting = session.execute(
                Select(Settings).where(Settings.key == key)
            ).scalar_one_or_none()
            
            if setting:
                setting.value = value
            else:
                setting = Settings(key=key, value=value)
                session.add(setting)
            
            session.commit()
            return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/settings/all')
def get_all_settings():
    """Get all settings"""
    with Session(engine) as session:
        settings = session.execute(Select(Settings)).scalars().all()
        settings_dict = {s.key: s.value for s in settings}
        return jsonify(success=True, settings=settings_dict)


# PIN Authentication for Manager
@app.route('/auth/verify_pin', methods=['POST'])
def verify_pin():
    """Verify master PIN"""
    try:
        data = request.get_json()
        pin = data.get('pin')
        
        with Session(engine) as session:
            master_pin_setting = session.execute(
                Select(Settings).where(Settings.key == 'master_pin')
            ).scalar_one_or_none()
            
            if master_pin_setting and master_pin_setting.value == pin:
                return jsonify(success=True)
            return jsonify(success=False, error='Invalid PIN')
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/auth/setup_pin', methods=['POST'])
def setup_pin():
    """Set up master PIN on first run"""
    try:
        data = request.get_json()
        pin = data.get('pin')
        
        with Session(engine) as session:
            # Check if PIN already exists
            existing = session.execute(
                Select(Settings).where(Settings.key == 'master_pin')
            ).scalar_one_or_none()
            
            if existing:
                return jsonify(success=False, error='PIN already set')
            
            setting = Settings(key='master_pin', value=pin)
            session.add(setting)
            session.commit()
            return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


# Dashboard Statistics
@app.route('/dashboard/stats')
def dashboard_stats():
    """Get dashboard statistics"""
    with Session(engine) as session:
        # Count open tables
        open_tables = session.execute(
            Select(Table).where(Table.status == True)
        ).scalars().all()
        open_tables_count = len(open_tables)
        
        # Calculate revenue (completed orders)
        stmt = Select(Order).join(Order.item).where(Order.status == 2, Order.voided.is_(False))
        completed_orders = session.execute(stmt).scalars().all()
        total_revenue = sum(order.quantity * order.item.price for order in completed_orders)
        
        # Count pending orders
        pending_orders_count = session.execute(
            Select(Order).where(Order.status.in_([0, 1]), Order.voided.is_(False))
        ).scalars().all()
        pending_orders_count = len(pending_orders_count)
        
        return jsonify(
            success=True,
            open_tables=open_tables_count,
            total_revenue=total_revenue,
            pending_orders=pending_orders_count
        )


# Receipt Generation
@app.route('/receipt/generate/<int:tableId>')
def generate_receipt(tableId):
    """Generate receipt for a table"""
    with Session(engine) as session:
        table = session.get(Table, tableId)
        if not table:
            return jsonify(success=False, error='Table not found')
        
        # Get all non-voided orders
        stmt = Select(Order).join(Order.item).where(
            Order.table_id == tableId,
            Order.voided.is_(False)
        )
        orders = session.execute(stmt).scalars().all()
        
        # Calculate totals
        receipt_items = []
        total = 0
        for order in orders:
            item_total = order.quantity * order.item.price
            total += item_total
            receipt_items.append({
                'name': order.item.name,
                'quantity': order.quantity,
                'price': order.item.price,
                'total': item_total
            })
        
        receipt_data = {
            'table_id': tableId,
            'guests': table.numberOfGuests,
            'items': receipt_items,
            'total': total,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(success=True, receipt=receipt_data)


@app.route('/receipt/save/<int:tableId>', methods=['POST'])
def save_receipt(tableId):
    """Save receipt to database"""
    try:
        data = request.get_json()
        receipt_data = data.get('receipt')
        
        with Session(engine) as session:
            receipt = Receipt(
                table_id=tableId,
                total_amount=receipt_data['total'],
                receipt_data=json.dumps(receipt_data)
            )
            session.add(receipt)
            session.commit()
            return jsonify(success=True, receipt_id=receipt.id)
    except Exception as e:
        return jsonify(success=False, error=str(e))


# Enhanced Kitchen View - Time-based filtering
@app.route('/checker/orders/kitchen_enhanced')
def return_kitchen_orders_enhanced():
    """Enhanced kitchen view with time-based priority"""
    with Session(engine) as session:
        stmt = Select(Order).join(Order.item).where(
            MenuItems.place_to_go == 'kitchen',
            Order.voided.is_(False)
        )
        orders = session.execute(stmt).scalars().all()
        
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        enhanced_orders = []
        for order in orders:
            time_diff = (now - order.created_at).total_seconds() / 60  # minutes
            
            # Determine priority based on time
            if time_diff < 10:
                priority = 'fresh'
            elif time_diff < 20:
                priority = 'cooking'
            else:
                priority = 'urgent'
            
            enhanced_orders.append({
                'id': order.id,
                'name': order.item.name,
                'quantity': order.quantity,
                'status': order.status,
                'tableID': order.table_id,
                'priority': priority,
                'wait_time': int(time_diff)
            })
        
        return jsonify(enhanced_orders)


# Enhanced Bar View - Auto-grouping
@app.route('/checker/orders/bar_enhanced')
def return_bar_orders_enhanced():
    """Enhanced bar view with auto-grouping of identical drinks"""
    with Session(engine) as session:
        stmt = Select(Order).join(Order.item).where(
            MenuItems.place_to_go == 'bar',
            Order.voided.is_(False)
        )
        orders = session.execute(stmt).scalars().all()
        
        # Group by item name and status
        grouped = {}
        for order in orders:
            key = f"{order.item.name}_{order.status}"
            if key not in grouped:
                grouped[key] = {
                    'name': order.item.name,
                    'status': order.status,
                    'total_quantity': 0,
                    'tables': []
                }
            grouped[key]['total_quantity'] += order.quantity
            grouped[key]['tables'].append({
                'table_id': order.table_id,
                'quantity': order.quantity,
                'order_id': order.id
            })
        
        enhanced_orders = list(grouped.values())
        return jsonify(enhanced_orders)


# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates