#!/usr/bin/python

from flask import Flask, request, jsonify
from database import init_db
from database import db_session
from models import *
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

init_db()

@app.route('/')
def index():
    return """
<title>Early-Hamster Backend</title>
<h1>Early-Hamster Backend</h1>
    <span style="font-weight: bold; background-color: lightgreen; padding: 8px">
        is running
    </span>"""

@app.route('/api/storelist', methods=['GET'])
def storelist():
    store_type = request.args.get('type', None)
    results = None

    if store_type is None:
        results = Store.query.all()
    else:
        results = Store.query.filter(Store.store_type == store_type).all()

    result_dicts = []
    for store in results:
        result_dicts.append({
            "StoreID": store.id,
            "Type": store.store_type,
            "Name": store.name,
            "Status": store.status,
        })

    return {"storelist": result_dicts}

@app.route('/api/booking', methods=['GET', 'POST'])
def booking():
    if request.method == "GET":
        user_id = request.args.get('UserID', None)
        results = None

        if user_id is None:
            results = {}
        else:
            results = Booking.query.filter(Booking.user_id == user_id).all()

        result_dicts = []
        for booking in results:
            result_dicts.append({
                "BookingID": booking.id,
                "Startdate": int(booking.start_date.timestamp()),
                "StoreName": booking.store.name
            })

        return {"bookings": result_dicts}

    elif request.method == "POST":

        b = Booking()
        b.start_date = datetime.utcfromtimestamp(int(request.args.get('Startdate')))
        b.user_id = request.args.get('UserID')
        b.store_id = request.args.get('StoreID')

        db_session.add(b)
        db_session.commit()

        return {
            "BookingID": b.id,
            "Startdate": int(b.start_date.timestamp()),
            "StoreName": b.store.name
        }

@app.route('/api/capacity', methods=['GET'])
def capacity():
    start_date = request.args.get('Startdate', '')
    end_date = request.args.get('Enddate', '')
    store_id = request.args.get('StoreID', '')
    results = None

    if not all([start_date, end_date, store_id]):
        results = {}
    else:
        results = Booking.query.filter(
            Booking.store_id == store_id,
            Booking.start_date >= start_date,
            Booking.start_date <= end_date
        ).order_by(Booking.start_date).all()

    histogram = {}
    for booking in results:
        if booking.start_date in histogram:
            histogram[booking.start_date] += 1
        else:
            histogram[booking.start_date] = 1

    result_dicts = []
    for slot, amount in histogram.items():
        result_dicts.append({
            "Timeslot": slot,
            "Amout": amount
        })

    return {"capacity": result_dicts}

app.run(host='0.0.0.0', port=5000)

