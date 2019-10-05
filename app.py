import numpy as np
import sqlalchemy
import datetime as dt
import pandas as pd

from flask import Flask, jsonify, request, escape
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


# /
# Home page.
# List all routes that are available.


app = Flask(__name__)

@app.route('/')
def home():
    return (
        f"/api/v1.0/precipitation<br/>" 
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# /api/v1.0/precipitation
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route('/api/v1.0/precipitation')
def precipitation():
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_data_point = last_data_point[0]
    one_year_ago = dt.datetime.strptime(last_data_point, "%Y-%m-%d")- dt.timedelta(days=366)
    
    data = session.query(Measurement.date, Measurement.prcp)\
                    .filter(Measurement.date >= one_year_ago)\
                    .filter(Measurement.date <= last_data_point).all()
    return jsonify(dict(data))

# /api/v1.0/stations
# Return a JSON list of stations from the dataset.

@app.route('/api/v1.0/stations')
def stations():
    number_of_station = session.query(Station.station).count()
    most_active_stations = session.query(Measurement.station, func.count(Measurement.prcp))\
                                    .group_by(Measurement.station)\
                                    .order_by(func.count(Measurement.prcp).desc()).all()

    most_active_stations_results = []
    for stations in most_active_stations:
        stations_dict = {'station':stations[0], 'count':stations[1]}
        most_active_stations_results.append(stations_dict) 
        
    return jsonify(most_active_stations_results)                                


# # /api/v1.0/tobs
# # query for the dates and temperature observations from a year from the last data point.
# # Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route('/api/v1.0/tobs')
def tobs():
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_data_point = last_data_point[0]
    one_year_ago = dt.datetime.strptime(last_data_point, "%Y-%m-%d")- dt.timedelta(days=366)

    # number_of_station = session.query(Station.station).count()
    most_active_stations = session.query(Measurement.station, func.count(Measurement.prcp))\
                                    .group_by(Measurement.station)\
                                    .order_by(func.count(Measurement.prcp).desc()).all()
    most_active_station = most_active_stations[0][0]

    
    last_one_year = session.query(Measurement.station, Measurement.tobs)\
                                .filter(Measurement.station==most_active_station)\
                                .filter(Measurement.date >=(one_year_ago))\
                                .all()
    
    last_one_year_temp = []
    for tobs in last_one_year:
        tobs_dict = {'station':tobs[0], 'tobs':tobs[1]}
        last_one_year_temp.append(tobs_dict) 
        
    
    return jsonify(last_one_year_temp)


# # /api/v1.0/<start> and /api/v1.0/<start>/<end>
# # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route('/api/v1.0/<start>')
def start(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # results_list = []
    # for stats in results:
    #     results_dict = {'min_temp':stats[0][0], 'avg_temp':stats[0][1], 'max_temp':stats[0][2]}
    #     # results_list.append(results_dict)
    
    return jsonify(results)

@app.route('/api/v1.0/<start>/<end>')
def startend(start,end):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
