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
    if int(end_hour) < 10:
        end_hour = str(f"0{end_hour}")
        return [end_hour, end_date, end_month]
    else:
        return [end_hour, end_date, end_month]


def get_data():
    url = f"https://kbh-proxy.septima.dk/api/measurements?stations=2&meanValueTypes=24H&start=2018-01-01T08%3A00%3A00Z&end=2023-{get_hour()[2]}-{get_hour()[1]}T{get_hour()[0]}%3A00%3A00Z"
    req = requests.get(url)
    package_dict = json.loads(req.content)
    return pd.json_normalize(package_dict, record_path=["stations", "measurements"])


def check_limit_PM2(val):
    if val >= 15:
        return 1
    else:
        return 0


def check_limit_NO2(val):
    if val >= 25:
        return 1
    else:
        return 0


def check_limit_PM10(val):
    if val >= 45:
        return 1
    else:
        return 0


def process_data(df):
    df_pm = df[["PM2_5", "NO2", "PM10", "EndLocal"]]
    pd.to_datetime(df_pm["EndLocal"])

    df_pm["EndLocal"] = pd.to_datetime(df_pm["EndLocal"])
    #df_pm["month"] = df_pm['EndLocal'].dt.month
    #df_pm["year"] = df_pm['EndLocal'].dt.year
    #df_pm["day"] = df_pm['EndLocal'].dt.day
    df["ExceededPM2"] = df_pm["PM2_5"].apply(check_limit_PM2)
    df["ExceededNO2"] = df_pm["NO2"].apply(check_limit_NO2)
    df["ExceededPM10"] = df_pm["PM10"].apply(check_limit_PM10)

    return df


def pivot_data(df, val):
    return df.pivot_table(values=val, columns='EndLocal', aggfunc="first")


df = get_data()
df = process_data(df)


# Initialize the app
app = Dash(__name__)
server = app.server
# App layout
app.layout = html.Div([
    html.Div(children='My First App with Data, Graph, and Controls'),
    html.Hr(),
    dcc.RadioItems(options=['ExceededPM2', 'PM10', 'NO2'],
                   value='NO2', id='controls-and-radio-item'),
    dcc.Graph(figure={}, id='controls-and-graph')
])

# Add controls to build the interaction


@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    df_piv = pivot_data(df, col_chosen)
    fig = px.imshow(df_piv,template="ggplot2")
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
