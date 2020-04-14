from flask import Flask, request, jsonify, Response, g
from dicttoxml import dicttoxml
import math
import time
import calendar
app = Flask(__name__)
app.config['SECRET_KEY'] = 'zadhc0z0f6efd2b5e7507087d1114cacf'
data = {
    "region": {
        "name": "Africa",
        "avgAge": 19.7,
        "avgDailyIncomeInUSD": 5,
        "avgDailyIncomePopulation": 0.71
    },
    "periodType": "days",
    "timeToElapse": 58,
    "reportedCases": 674,
    "population": 66622705,
    "totalHospitalBeds": 1380614
}

output_data = {
    "data": {},
    "impact": {},
    "severeImpact": {}
}


# returns duration
def computeDuration(data):
    if data['periodType'] == 'months':
        duration = data['timeToElapse'] * 30
    elif data['periodType'] == 'weeks':
        duration = data['timeToElapse'] * 7
    else:
        duration = data['timeToElapse'] * 1
    return duration

"""Challenge one"""
def ChallengeOne(data):
    impactCurrentlyInfected=data['reportedCases']*10
    severeImpactCurentlyInfected = data['reportedCases'] * 50
    output_data["impact"]["currentlyInfected"]=impactCurrentlyInfected
    output_data['severeImpact']['currentlyInfected']=severeImpactCurentlyInfected
    """user // to remove decimals"""
    impactInfectionsByRequestedTime=impactCurrentlyInfected * (2**(computeDuration(data) // 3))
    severeInfectionsByRequestedTime =severeImpactCurentlyInfected * (2**(computeDuration(data) // 3))
    output_data["data"]=data
    output_data["impact"]["infectionsByRequestedTime"] = impactInfectionsByRequestedTime
    output_data["severeImpact"]["infectionsByRequestedTime"] = severeInfectionsByRequestedTime
    return output_data

"""challenge two solution"""
def ChallengeTwo(data):
    challengeOneData=ChallengeOne(data=data)
    impactInfectionsByRequestedTime=math.trunc(challengeOneData["impact"]["infectionsByRequestedTime"] * 0.15)
    severeInfectionsByRequestedTime =math.trunc(challengeOneData["severeImpact"]["infectionsByRequestedTime"] * 0.15)
    challengeOneData["impact"]["severeCasesByRequestedTime"] = impactInfectionsByRequestedTime
    challengeOneData["severeImpact"]["severeCasesByRequestedTime"] =severeInfectionsByRequestedTime


    """available beds"""
    impacthospitalBedsByRequestedTime=math.trunc(data["totalHospitalBeds"] * 0.35 - impactInfectionsByRequestedTime)
    severehospitalBedsByRequestedTime=math.trunc(data["totalHospitalBeds"] * 0.35 - severeInfectionsByRequestedTime)
    challengeOneData["impact"]["hospitalBedsByRequestedTime"] = impacthospitalBedsByRequestedTime
    challengeOneData["severeImpact"]["hospitalBedsByRequestedTime"] = severehospitalBedsByRequestedTime
    return challengeOneData


"""Challenge 3 solution"""
def ChallengeThree(data):
    challengeTwoData = ChallengeTwo(data=data)
    """requires ICU"""
    ImpactcasesForICUByRequestedTime=math.trunc(challengeTwoData["impact"]["infectionsByRequestedTime"] * 0.05)
    SeverecasesForICUByRequestedTime = math.trunc(challengeTwoData["severeImpact"]["infectionsByRequestedTime"] * 0.05)
    challengeTwoData["impact"]["casesForICUByRequestedTime"] = ImpactcasesForICUByRequestedTime
    challengeTwoData["severeImpact"]["casesForICUByRequestedTime"] =  SeverecasesForICUByRequestedTime
    """require ventilators"""
    ImpactcasesForVentilatorsByRequestedTime=math.trunc(challengeTwoData["impact"]["infectionsByRequestedTime"] * 0.02)
    SeverecasesForVentilatorsByRequestedTime= math.trunc(challengeTwoData["severeImpact"]["infectionsByRequestedTime"] * 0.02)
    challengeTwoData["impact"]["casesForVentilatorsByRequestedTime"] = ImpactcasesForVentilatorsByRequestedTime
    challengeTwoData["severeImpact"]["casesForVentilatorsByRequestedTime"] = SeverecasesForVentilatorsByRequestedTime

    """compute Money lost(Dollar Flight)"""
    ImpactdollarsInFlight = math.trunc(challengeTwoData["impact"]["infectionsByRequestedTime"] * data["region"]["avgDailyIncomeInUSD"] *
        data["region"]["avgDailyIncomePopulation"] / computeDuration(data))
    SeveredollarsInFlight = math.trunc(challengeTwoData["severeImpact"]["infectionsByRequestedTime"] * data["region"]["avgDailyIncomeInUSD"] *
        data["region"]["avgDailyIncomePopulation"] / computeDuration(data))

    challengeTwoData["impact"]["dollarsInFlight"] = ImpactdollarsInFlight
    challengeTwoData["severeImpact"]["dollarsInFlight"] = SeveredollarsInFlight

    return challengeTwoData

def estimator(data):
    """Challenge one"""
    ChallengeOne(data)

    """Challenge Two"""
    ChallengeTwo(data)

    """Challenge Three"""
    ChallengeThree(data)

    return output_data


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
    estimator(data)
    app.run(debug=True)