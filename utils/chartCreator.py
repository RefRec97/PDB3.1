
import logging
import datetime
from quickchart import QuickChart
from utils.db import DB

class ChartCreator():

    def __init__(self, db):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._db:DB = db
    
    def getAllianceUrl(self, allianceData, allianceName):
        
        groupedData = self._groupAllianceData(allianceData)
        chartData = self._getAllianceChartData(groupedData)

        return self._createChartUrl(chartData, allianceName, False)


    def _groupAllianceData(self, allianceData):
        
        groupedData = [
            {
                "score": 0,
                "researchScore": 0,
                "buildingScore": 0,
                "defensiveScore": 0,
                "fleetScore": 0,
                "timestamp": allianceData[0][7]
            }
        ]
        currentDay = allianceData[0][7].day
        currentHour = allianceData[0][7].hour
        idx = 0
        for datapoint in allianceData:
            timestamp:datetime.datetime = datapoint[7]

            if not (currentDay == timestamp.day and currentHour == timestamp.hour ):
                currentDay = timestamp.day
                currentHour = timestamp.hour
                idx+=1
                groupedData.append(
                    {
                        "score": 0,
                        "researchScore": 0,
                        "buildingScore": 0,
                        "defensiveScore": 0,
                        "fleetScore": 0,
                        "timestamp": timestamp
                    }
                )
            
            groupedData[idx]["score"] += datapoint[2]
            groupedData[idx]["researchScore"] += datapoint[3]
            groupedData[idx]["buildingScore"] += datapoint[4]
            groupedData[idx]["defensiveScore"] += datapoint[5]
            groupedData[idx]["fleetScore"] += datapoint[6]

        return groupedData

    def getChartUrl(self, userData, userName):
        chartData = self._getChartData(userData)

        return self._createChartUrl(chartData, userName, True)

    def _createChartUrl(self,chartData,name, useRank:bool):
        qc = QuickChart()
        qc.width = 720
        qc.height = 480
           
        qc.device_pixel_ratio = 1

        qc.config = {
            "type": "line",
            "data": {
                "labels": chartData["labels"],
                "datasets": [{
                    "yAxisID": "pointAxis",
                    "label": "Gesamtpunkte",
                    "data": chartData["gesamt"],
                    "fill": False,
                    "pointRadius": 1,
                },{
                    "yAxisID": "pointAxis",
                    "label": "Gebäude",
                    "data": chartData["gebäude"],
                    "fill": False,
                    "pointRadius": 1,
                },{
                    "yAxisID": "pointAxis",
                    "label": "Forschung",
                    "data": chartData["forschung"],
                    "fill": False,
                    "pointRadius": 1,
                },{
                    "yAxisID": "pointAxis",
                    "label": "Flotte",
                    "data": chartData["flotte"],
                    "fill": False,
                    "pointRadius": 1,
                },{
                    "yAxisID": "pointAxis",
                    "label": "Defensive",
                    "data": chartData["defensive"],
                    "fill": False,
                    "pointRadius": 1,
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": name,
                },
                "scales": {
                    "xAxes": [{
                        "stacked": True
                    }],
                    "yAxes": [{
                        "id": "pointAxis",
                        "display": True,
                        "position": "right",
                        "gridLines": {
                            "drawOnChartArea": False
                        },
                        "ticks": {
                            "beginAtZero": True}
                    }]
                }
            }
        }
        
        if useRank:
            qc.config["data"]["datasets"].append(
                {
                    "yAxisID": "rankAxis",
                    "label": "Platz",
                    "data": chartData["platz"],
                    "fill": False,
                    "pointRadius": 1,
                }
            )
            qc.config["options"]["scales"]["yAxes"].append(
                {
                    "id": "rankAxis",
                    "display": True,
                    "position": "left",
                    "stacked": True,
                }
            )
        
        return qc.get_short_url()

    def _getAllianceChartData(self, allianceData):
        chartData= {
            "labels": [],
            "gesamt": [],
            "flotte": [],
            "gebäude": [],
            "defensive": [],
            "forschung": []
        }

        for datapoint in allianceData:
            chartData["labels"].append(datetime.datetime.strftime(datapoint["timestamp"], "%H-%d.%m.%Y") )
            chartData["gesamt"].append(datapoint["score"])
            chartData["forschung"].append(datapoint["researchScore"])
            chartData["gebäude"].append(datapoint["buildingScore"])
            chartData["defensive"].append(datapoint["defensiveScore"])
            chartData["flotte"].append(datapoint["fleetScore"])
        
        return chartData

    def _getChartData(self, userData):
        chartData= {
            "labels": [],
            "gesamt": [],
            "platz": [],
            "flotte": [],
            "gebäude": [],
            "defensive": [],
            "forschung": []
        }

        for datapoint in reversed(userData):
            chartData["labels"].append(datetime.datetime.strftime(datapoint[-1], "%H-%d.%m.%Y") )
            chartData["platz"].append(datapoint[1])
            chartData["gesamt"].append(datapoint[2])
            chartData["forschung"].append(datapoint[4])
            chartData["gebäude"].append(datapoint[6])
            chartData["defensive"].append(datapoint[8])
            chartData["flotte"].append(datapoint[10])
        
        return chartData
