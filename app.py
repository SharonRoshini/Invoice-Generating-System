from flask import Flask, render_template, request, Response, jsonify, session, redirect, url_for, make_response
import pymongo
from functools import wraps
import jwt
from datetime import datetime, timedelta
from bson.objectid import ObjectId
# import pdfkit

app = Flask(__name__)
app.secret_key = 'super secret key'


CONNECTION_STRING = 'mongodb+srv://user:root@miniproject.q9hgigl.mongodb.net/?retryWrites=true&w=majority'

client = pymongo.MongoClient(CONNECTION_STRING)

db = client.get_database('miniproject-software')
user_collection = pymongo.collection.Collection(db, 'users')
item_collection = pymongo.collection.Collection(db, 'items')
invoice_collection = pymongo.collection.Collection(db, 'invoice')

# # decorator for verifying the JWT


# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         # jwt is passed in the request header
#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']
#         # return 401 if token is not passed
#         if not token:
#             return jsonify({'message': 'Token is missing !!'}), 401

#         try:
#             # decoding the payload to fetch the stored details
#             data = jwt.decode(token, app.config['SECRET_KEY'])
#             current_user = user_collection.find({'username': data['name']})
#         except:
#             return jsonify({
#                 'message': 'Token is invalid !!'
#             }), 401
#         # returns the current logged in users contex to the routes
#         return f(current_user, *args, **kwargs)

#     return decorated


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:

            return render_template('index.html', invalid_password=True)

        user = user_collection.find(
            {'username': username, 'password': password})
        user = list(user)
        if user == []:

            return render_template('index.html', invalid_password=True)
        else: 
            if user[0]['password'] == password:

                token = jwt.encode({
                    'emp_id': user[0]['emp_id'],
                    'name': user[0]['username'],
                    'exp': datetime.utcnow() + timedelta(minutes=90)
                }, app.config['SECRET_KEY'])

                session['token'] = token
                return redirect(url_for('dashboard'))

        return render_template('index.html', invalid_password=True)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if request.method == 'GET':
        token = session['token']
        if token:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = user_collection.find({'username': data['name']})
        return render_template('dashboard_new.html', user=current_user[0])


@app.route('/logout')
def logout():
    session.pop('token')
    return redirect('/')


@app.route('/create-invoice', methods=('GET', 'POST'))
def create_invoice():
    if request.method == 'GET':
        # return render_template('invoice_creation_form.html', flag=False)
        return render_template('create-invoice.html', flag=False)

    if request.method == 'POST':
        cust_name = request.form['cust_name']
        session['cust_address'] = request.form['cust_address']
        session['mode_of_dispatch'] = request.form['mode_of_dispatch']
        session['payment'] = request.form['payment']
        session['station'] = request.form['station']
        session['transporter'] = request.form['transporter']
        session['customer_name'] = cust_name
        # user = user_collection.find({'username': session['user']})
        return redirect(url_for('get_item'))


@app.route('/add-item', methods=['GET', 'POST'])
def get_item():
    if request.method == 'GET':
        items = item_collection.find()
        return render_template('add-item.html', items=list(items))

    if request.method == 'POST':
        cust_name = session['customer_name']
        cust_address = session['cust_address']
        mode_of_dispatch = session['mode_of_dispatch']
        payment = session['payment']
        station = session['station']
        transporter = session['transporter']

        item_ids = request.form.getlist('chkbox')
        quant = request.form.getlist('quantity')
        quant_list = [0 for i in range(len(quant))]
        # print(quant_list)                                         ###########################################TODO
        # for i in range(len(quant_list)):
        #     quant_list[item_ids[i-1]] = quant[i]
        # print(item_ids, quant, cust_name, quant_list)             ###########################################TODO
        items = []
        for index, item_id in enumerate(item_ids):
            item = item_collection.find({'item_id': int(item_id)})
            item = item[0]
            if 'quantity' not in item:
                item['quantity'] = int(quant[index])
            items.append(item)
        inserted_datetime = datetime.now()
        rec_inserted = invoice_collection.insert_one({'customer_name': cust_name, 'customer_address': cust_address, 'mode_of_dispatch': mode_of_dispatch,
                                                     'payment': payment, 'station': station, 'transporter': transporter, 'items_purchased': items, 'timestamp': inserted_datetime})
        user_data = {
            'customer_name': cust_name, 'customer_address': cust_address, 'mode_of_dispatch': mode_of_dispatch,
            'payment': payment, 'station': station, 'transporter': transporter
        }
        return render_template('create-invoice.html', flag=True, items=items, user_data=user_data)


@app.route('/view-invoice', methods=['GET', 'POST'])
def view_invoice():
    if request.method == 'GET':
        invoices = invoice_collection.find()
        invoice_list = list(invoices)
        return render_template('view-invoice-new.html', invoic=invoice_list, name=invoice_list[0]['payment'])


@app.route('/view-invoice/<id>', methods=['GET', 'POST'])
def view_single_invoice(id):
    if request.method == 'GET':
        invoice = invoice_collection.find_one({'_id': ObjectId(id)})
        return render_template('invoice.html', invoice=invoice)

    # if request.method == 'POST':
    #     invoice = invoice_collection.find_one({'_id': ObjectId(id)})
    #     rendered = render_template('invoice.html', invoice=invoice)

    #     # PDF options
    #     options = {
    #         "orientation": "landscape",
    #         "page-size": "A4",
    #         "margin-top": "1.0cm",
    #         "margin-right": "1.0cm",
    #         "margin-bottom": "1.0cm",
    #         "margin-left": "1.0cm",
    #         "encoding": "UTF-8",
    #     }
    #     # by using configuration you can add path value.
    #     wkhtml_path = pdfkit.configuration(
    #         wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")

    #     # Build PDF from HTML
    #     pdf = pdfkit.from_string(rendered, options=options, configuration=wkhtml_path)

    #     # Download the PDF
    #     return Response(pdf, mimetype="application/pdf")
    # render_template('success.html')


@app.route('/delete-invoice/<id>')
def delete_invoice(id):
    result = invoice_collection.delete_one({'_id': ObjectId(id)})
    return redirect('/view-invoice')


@app.route('/item-details')
def view_items():
    items = item_collection.find()
    item_list = list(items)
    return render_template('item-details-new.html', items=item_list)


@app.route('/edit-item/<id>', methods=['GET', 'POST'])
def edit_item(id):
    if request.method == 'GET':
        item_detail = item_collection.find_one({'_id': ObjectId(id)})
        return render_template('edit-item.html', item=item_detail)
    elif request.method == 'POST':
        item_id = request.form['item-id']
        item_name = request.form['item-name']
        price = request.form['price']
        item_collection.update_one({
            '_id': ObjectId(id)
        }, {
            "$set": {
                'item_id': int(item_id),
                'name': item_name,
                'price': int(price)
            }
        })
    return redirect('/item-details')


@app.route('/delete-item/<id>')
def delete_item(id):
    item_collection.delete_one({'_id': ObjectId(id)})
    return redirect('/item-details')


@app.route('/new-item', methods=['GET', 'POST'])
def new_item():
    if request.method == 'GET':
        return render_template('new-item.html')

    elif request.method == 'POST':
        item_id = request.form['item-id']
        item_name = request.form['item-name']
        price = request.form['price']
        item_collection.insert_one(
            {'item_id': int(item_id), 'name': item_name, 'price': int(price)})
        return redirect('/item-details')


if __name__ == '__main__':
    app.run(debug=True)
