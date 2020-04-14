from flask import Flask, request, jsonify, Response, g
from dicttoxml import dicttoxml
import time
import calendar
from src.estimator import estimator
app = Flask(__name__)
app.config['SECRET_KEY'] = 'zadhc0z0f6efd2b5e7507087d1114cacf'
"""default route"""
@app.route("/api/v1/on-covid-19", methods=["POST"])
def defaultApi():
    try:
        if not request.is_json:
            return jsonify(message=['Invalid or empty data'])
        jdata =request.json['data']
        resp =jsonify(estimator(jdata))
        resp.status_code = 200
        resp.content_type = "application/json"
        return resp

    except:
        return not_found()

"""json route"""
@app.route("/api/v1/on-covid-19/json", methods=["POST"])
def jsonApi():
    try:
        if not request.is_json:
            return jsonify(message=['Invalid or empty data'])
        jdata = request.json['data']
        resp = jsonify(estimator(jdata))
        resp.status_code = 200
        resp.content_type = "application/json"
        return resp
    except:
        return not_found()


"""json route"""
@app.route("/api/v1/on-covid-19/xml", methods=["POST"])
def xmlApi():
    try:
        if not request.is_json:
            return jsonify(message=['Invalid or empty data'])
        jdata =request.json['data']
        resp = dicttoxml(estimator(jdata))

        return Response(resp,mimetype = 'application/xml')
    except:
        return not_found()

@app.route("/api/v1/on-covid-19/log", methods=["GET"])
def send_log():
  message =""
  with open("log.txt","r") as file_ref:
    lines = file_ref.readlines()
    for line in lines:
      message =message+line+"<br>"
  return message

@app.before_request
def start_timing():
  g.start_time =time.time()


@app.after_request
def stop_timing(response):
  duration = f"done in {round(time.time()-g.start_time,2)} ms"
  url = request.path
  path =url.strip('/api/v1/')
  currDate = calendar.timegm(time.gmtime())
  with open('log.txt', 'a') as file_ref:
    print("{}\t\t{}\t\t{}".format(currDate,path,duration), file=file_ref)
  return response


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

if __name__=="__main__":
    app.run(debug=True)