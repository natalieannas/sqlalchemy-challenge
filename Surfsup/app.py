# Import the dependenciespy
import numpy as np
import datetime as dt
from datetime import timedelta, datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

def get_last_year_date():
      most_recent_date=dt.datetime(2017, 8, 23)
      last_year_date= most_recent_date-dt.timedelta(366)
      return last_year_date


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )
    

@app.route("/api/v1.0/precipitation")
def percp_df():
        one_year_ago = get_last_year_date()
        results= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>one_year_ago).all()
        session.close()
        precipitation_dict = {date: prcp for date, prcp in results}
        return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
      
      station_results=session.query(Station.station).all()
      session.close()
      all_station_results=[station[0] for station in station_results]
      return jsonify(all_station_results)      

@app.route("/api/v1.0/tobs")   
def tobs():
      
      most_active_station="USC00519281"
      one_year_ago = get_last_year_date()
      results = session.query(Measurement.tobs, Measurement.date)\
            .filter(Measurement.station == most_active_station)\
            .filter(Measurement.date >= one_year_ago)\
            .all()
      session.close()
      temperatures=[temp[0]for temp in results]
      return jsonify(temperatures)
     
 

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end=None):
      temp_query=[
           func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)]
      
      
      if end is None: 
            
            results = session.query(*temp_query).filter(Measurement.date >= start).all()
            session.close()  
            temp_dict={
            "tmin": results[0][0],
            "tavg": results[0][1],
            'tmax': results[0][2]}
      
            
            return jsonify(temp_dict)

      results = session.query(*temp_query).filter(Measurement.date >= start, Measurement.date <= end).all()
     
      temp_dict={
            "tmin": results[0][0],
            "tavg": results[0][1],
            'tmax': results[0][2]}
      
      session.close()

      return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True) 