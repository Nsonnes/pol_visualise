# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import json
import requests
import datetime
# Incorporate data


# Morning hours are formatted as 08... and evening hours are formatted as 8
def get_hour():
    now = datetime.datetime.now()
    end_date = now.strftime("%d")
    end_hour = now.strftime("%H")
    end_month = now.strftime("%m")
    if int(end_hour) == 0:
        return [end_hour, end_date, end_month]

    if int(end_hour) < 10:
        end_hour = str(f"0{end_hour}")
        return [end_hour, end_date, end_month]
    else:
        return [end_hour, end_date, end_month]


def get_data():
    url = f"https://kbh-proxy.septima.dk/api/measurements?stations=2&meanValueTypes=24H&start=2018-01-01T08%3A00%3A00Z&end=2023-{get_hour()[2]}-{get_hour()[1]}T{get_hour()[0]}%3A00%3A00Z"
    print(url)
    req = requests.get(url)
    package_dict = json.loads(req.content)
    df = pd.json_normalize(package_dict, record_path=["stations", "measurements"])
    print(df)
    #df.to_csv("test_data.csv")




df = get_data()
