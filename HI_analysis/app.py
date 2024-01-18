# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# List all routes on landing page
@app.route("/")
def welcome():
    return(
        '''
        Welcome to my analysis of Honolulu, HI precipitation and temperature from August 2016 - August 2017:<br/>
        Available Routes: <br/>
        <br/>
        A list of rain fall for August 2016 - August 2017:<br/>
        /api/v1.0/precipitation <br/>
        <br/>
        A list of stations that collect data:<br/>
        /api/v1.0/stations <br/>
        <br/>
        A list of temperatures from August 2016 - August 2017 from station USC00519281: <br/>
        /api/v1.0/tobs <br/>
        <br/>
        Minimum temp, maximum temp, and average temp values for Honolulu in date format YYYY-MM-DD format: <br/>
        /api/v1.0/<start> <br/>
        '''
    ) 


# A list of rain fall for previous year
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year_prcp = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_prcp).all()
    session.close()

# Create a list of dicts with date as key and prcp as the value
    prcp_totals = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_totals.append(prcp_dict)

    return jsonify(prcp_totals)


# All the stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    session.close()
    return jsonify(stations.to_dict())


# A list of temperatures for previous year from station USC00519281
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()
    session.close()


# A list of dicts with date as the key and tobs as the value
    temperature_totals = []
    for date, tobs in year_temp:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temperature_totals.append(temp_dict)

    return jsonify(temperature_totals)


# Min, avg, and max temp
@app.route("/api/v1.0/<start>")
def temp_statistics(start):
    session = Session(engine)

    # Temp statistics from chosen date to end of data
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    statistics = session.query(*sel).\
        filter(Measurement.date >= start).all()
    session.close()

    # Create the dictionary for the statistics results
    stat_results = []

    for min, max, avg in statistics:
        stat_dict = {}
        stat_dict["min"] = min
        stat_dict["max"] = max
        stat_dict["avg"] = avg
        stat_results.append(stat_dict)

    return jsonify(stat_results)



if __name__ == "__main__":
    app.run(debug=True)