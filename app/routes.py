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
    return render_template('kitchen.html')


@app.route('/bar')
def bar():
    return render_template('bar.html')


@app.route('/table_view/<int:tableNumber>')
def table_view(tableNumber):
    return render_template('table_view.html', tableNumber=tableNumber)

@app.route('/manager_interface')
def manager_interface():
    return render_template('manager_interface.html')
















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






# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates