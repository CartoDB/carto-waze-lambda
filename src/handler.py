"""
Carto Waze Lambda Connector

Developed by Geographica, 2017-2018.
"""

import json
import requests
from src.wazedata import WazeData
from src.wazecartomodel import WazeCartoModel
from src.wazegeorss import WazeGeoRSS, WazeGeoRSSException
from src.config import Config
from src.logger import Logger


def carto_waze_lambda_handler(event, context):

    lg = Logger(level='INFO')
    logger = lg.get()

    waze_georss = WazeGeoRSS(*Config.WAZE_GEORSS)

    resp = requests.get(waze_georss.req_url, timeout=10)

    if (resp.status_code == requests.codes.ok):
        data = resp.json()

        if not data:
            data = {"msg": "no_data"}

        waze_data = WazeData(data)
        waze_time = waze_data.get_time_range
        waze_st = waze_time.get('start_time')
        alerts_data = waze_data.build_alerts()
        jams_data = waze_data.build_jams()
        irrgs_data = waze_data.build_irrgs()

        waze_model = WazeCartoModel(Config.CARTO_API_KEY, Config.CARTO_USER,
                                    Config.TRAFFICO_PREFIX)
        waze_model.store_alerts(alerts_data)
        waze_model.store_jams(jams_data)
        waze_model.store_irrgs(irrgs_data)

        waze_model.refresh_mviews()

        response = {
            'statusCode': 200,
            'body': 'Function executed. GEORSS date: {}'.format(waze_st)
        }

        logger.info(response)

        return response

    else:
        msg = 'Request http error: {}'.format(resp.status_code)
        raise WazeGeoRSSException(msg)
