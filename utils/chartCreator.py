
import logging
import datetime
from quickchart import QuickChart
from utils.db import DB

class ChartCreator():

    def __init__(self, db):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._db:DB = db

    def getChartUrl(self, userData, userName):
        chartData = self._getChartData(userData)

        qc = QuickChart()
        qc.width = 720
        qc.height = 480
           
        qc.device_pixel_ratio = 1
        qc.config = {
            "type": "line",
            "data": {
                "labels": chartData["labels"],
                "datasets": [{
                    "yAxisID": "rankAxis",
                    "label": "Platz",
                    "data": chartData["platz"],
                    "fill": False,
                    "pointRadius": 1,
                },{
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
                    "text": userName,
                },
                "scales": {
                    "xAxes": [{
                        "stacked": True
                    }],
                    "yAxes": [{
                        "id": "rankAxis",
                        "display": True,
                        "position": "left",
                        "stacked": True,
                    },{
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
        return qc.get_short_url()

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
