"""horaroCreateJSON."""
import requests
import json
from datetime import datetime

jsonHoraroSchedule = requests.get('https://horaro.org/-/api/v1/schedules/2c11gz9fup46dc7a1c').json()
listRunners = None

"""Consume the horaro schedule to create the runners json file"""
def generateRunners(horaroSchedule):
    listRunnersRaw = []
    for objRuns in horaroSchedule['data']['items']:
        listRunnersRaw.append(objRuns['data'][1])
    setRunnersRaw = set(listRunnersRaw)
    print setRunnersRaw
    jsonRunners = []
    global listRunners
    listRunners = list(setRunnersRaw)
    pkCounter = 0
    for runner in setRunnersRaw:
        pkCounter += 1
        if "](" in runner:
            listRunnerObjs = runner.split('](')
            listRunnerObjs[0] = listRunnerObjs[0][1:]
            listRunnerObjs[1] = listRunnerObjs[1][:-1]
        else:
            listRunnerObjs = [runner, ""]
        # print listRunnerObjs
        jsonRunners.append({
            "fields": {
                "name": listRunnerObjs[0],
                "donor": None,
                "public": listRunnerObjs[0],
                "twitter": isTwitter(listRunnerObjs[1]),
                "youtube": isYoutube(listRunnerObjs[1]),
                "stream": listRunnerObjs[1]
            },
            "model": "tracker.runner",
            "pk": pkCounter
        })
    return jsonRunners

""" Consume the horaro schedule to create the schedule json file """
def generateSchedule(horaroSchedule):
    # listScheduleRaw = []
    pkCounter = 0
    jsonSchedule = []
    for objRuns in horaroSchedule['data']['items']:
        strName = objRuns['data'][0]
        strRunner = objRuns['data'][1].split('](')[0][1:] if '](' in objRuns['data'][1] else objRuns['data'][1]
        # print listRunners
        jsonSchedule.append({
            "fields": {
                "category": "",
                "giantbomb_id": None,
                "end_time": gdqDateFormat(objRuns['scheduled_t'] + objRuns['length_t']),
                "console": "",
                "name": strName,
                "description": "",
                "setup_time": "0:05:00",
                "public": strName,
                "run_time": gdqTimeFormat(objRuns['length_t']),
                "starttime": gdqDateFormat(objRuns['scheduled_t']),
                "display_name": strName,
                "commentators": "",
                "order": pkCounter,
                "deprecated_runners": strRunner,
                "event": 1,
                "runners": [listIndex + 1 for listIndex, listValue in enumerate(listRunners) if strRunner in listValue],
                "release_year": None
            },
            "model": "tracker.speedrun",
            "pk": pkCounter
        })
    return jsonSchedule

""" Checks if string contains twitter.com, returns if true, returns blank if false"""
def isTwitter(url):
    if "twitter.com" in url:
        return url
    else:
        return ""

""" Checks if string contains youtube.com, returns if true, returns blank if false"""
def isYoutube(url):
    if "youtube.com" in url:
        return url
    else:
        return ""

""" Consumes an integer representing seconds, and returns in h:mm:ss """
def gdqTimeFormat(intTime):
    return '{dt.hour}:{dt.minute:02}:{dt.second:02}'.format(dt=datetime.utcfromtimestamp(intTime))

""" Consume an integer representing seconds from Unix Epoch and return ISO 8601 format """
def gdqDateFormat(intTime):
    return datetime.utcfromtimestamp(intTime).isoformat() + "Z"

with open('runners.json', 'w+') as runnersOutputFile:
    jsonGDQRunners = generateRunners(jsonHoraroSchedule)
    json.dump(jsonGDQRunners, runnersOutputFile)
    runnersOutputFile.close()

with open('schedule.json', 'w+') as scheduleOutputFile:
    jsonGDQSchedule = generateSchedule(jsonHoraroSchedule)
    json.dump(jsonGDQSchedule, scheduleOutputFile)
    scheduleOutputFile.close()

# print listRunners
