# Import packages
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import json
import requests
import datetime as datetime
import dash_bootstrap_components as dbc

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
    df = pd.json_normalize(package_dict, record_path=["stations", "measurements"])
    df.to_csv("test_data.csv")

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
    df = df[["PM2_5", "NO2", "PM10", "EndLocal"]]
    df["EndLocal"] = pd.to_datetime(df["EndLocal"])  # format without hour
    #df["EndLocal"] = df["EndLocal"].dt.floor('D')
    df["EndLocal"] = df["EndLocal"].dt.date
    # print(df[["EndLocal"]])

    #df_pm["month"] = df_pm['EndLocal'].dt.month
    #df_pm["year"] = df_pm['EndLocal'].dt.year
    #df["day"] = df['EndLocal'].dt.day
    df["ExceededPM2"] = df["PM2_5"].apply(check_limit_PM2)
    df["ExceededNO2"] = df["NO2"].apply(check_limit_NO2)
    df["ExceededPM10"] = df["PM10"].apply(check_limit_PM10)

    return df


def pivot_data(df, val):
    return df.pivot_table(values=val, columns='EndLocal', aggfunc="first")


df = get_data()
df = process_data(df)


# Initialize the app
#app = Dash(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Luftforurening i København")
        ], width=6,),
    ], justify="center"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='plot')
        ], width=10),
        dbc.Col([
            html.Div(
                children="", className="box1",
                style={
                    'backgroundColor': 'rgb(54, 13, 18)',
                    'color': 'lightsteelblue',
                    'height': '18px',
                    'width': '45%',
                    'display': 'inline-block',

                }


            ), html.Div(children="Overskrider WHO grænseværdi", style={'textAlign': 'left', 'display': 'inline-block'}),
            html.Div(
                children="", className="box1",
                style={
                    'backgroundColor': 'rgb(240, 236, 236)',
                    'color': 'lightsteelblue',
                    'height': '18px',
                    'width': '45%',
                    'display': 'inline-block',

                }), html.Div(children="Under WHO grænseværdi", style={'textAlign': 'left', 'display': 'inline-block'})

        ], width=2)

    ], justify="center"),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown([
                {
                    "label": html.Span(['PM2.5'], style={'font-size': 15, 'font': 'Segoe UI'}),
                    "value": "ExceededPM2",
                },
                {
                    "label": html.Span(['PM10'], style={'font-size': 15, 'font': 'Segoe UI'}),
                    "value": "ExceededPM10",
                },
                {
                    "label": html.Span(['NO2'], style={'font-size': 15, 'font': 'Segoe UI'}),
                    "value": "ExceededNO2",
                }],  value='ExceededPM2',  id='controls-and-radio-item'










            )
        ], width=2)
    ], justify="left")


])


# App layout


# Add controls to build the interaction


@callback(
    Output(component_id='plot', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    df_piv = pivot_data(df, col_chosen)
    # , range_color =[-0.9,1.8]#color_continuous_scale='RdBu_r', range_color =[-0.5,1.2]
    names = {"ExceededPM2": "PM2.5",
             "ExceededPM10": "PM10", "ExceededNO2": "NO2"}
    exceeded = {0: "Nej", 1: "Ja"}
    colorscale = [[0, '#454D59'],
                  [1, '#454D59']]
    fig = px.imshow(df_piv, template="ggplot2",
                    title=f"{names[col_chosen]} målt ved søtorvet 5", zmin=0, zmax=1, color_continuous_scale='amp')

    fig.update_traces(hoverongaps=False, showscale=False,
                      hovertemplate="Pollutant measured: %{y}"
                      "<br>Date: %{x}"
                      "<br>Overskrider grænseværdi: %{z}")
    fig.update_layout(xaxis_nticks=12, xaxis_title=None)
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_coloraxes(showscale=False)
    fig.layout.coloraxis.colorbar.title = 'Title<br>Here'
    fig.update_traces(showscale=False)

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
