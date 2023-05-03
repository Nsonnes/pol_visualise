# Import packages
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import json
import requests
import datetime as datetime
import dash_bootstrap_components as dbc
import numpy as np


def get_hour():
    now = datetime.datetime.now()
    end_date = now.strftime("%d")
    end_hour = now.strftime("%H")
    print(end_hour)
    end_month = now.strftime("%m")
    if int(end_hour) == 0:
        return [end_hour, end_date, end_month]

    else:
        return [end_hour, end_date, end_month]


def get_data(val):
    url = f"https://kbh-proxy.septima.dk/api/measurements?stations={val}&meanValueTypes=24H&start=2021-01-01T08%3A00%3A00Z&end=2023-{get_hour()[2]}-{get_hour()[1]}T{get_hour()[0]}%3A00%3A00Z"
    print(url)
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
    df = df[["PM2_5", "NO2", "PM10", "EndLocal"]]

    df["EndLocal"] = pd.to_datetime(df["EndLocal"])  # format without hour
    df["year"] = df['EndLocal'].dt.year

    df["month"] = df['EndLocal'].dt.month
    df["EndLocal"] = df["EndLocal"].dt.date

    df["ExceededPM2"] = df["PM2_5"].apply(check_limit_PM2)
    df["ExceededNO2"] = df["NO2"].apply(check_limit_NO2)
    df["ExceededPM10"] = df["PM10"].apply(check_limit_PM10)

    return df


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA, "https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap"],  meta_tags=[{'name': 'viewport',
                                                                                                                                                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'},])
server = app.server


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1([
                "Overskridelser af WHO grænseværdier"]),
            html.H2(id="heading")

        ], xs=9, lg=10, xl=10, class_name="heading"),
    ], justify="center"),

    dbc.Row([
        dbc.Col([html.Div(style={"margin-top": '70px'}),
            html.Div([
                dcc.Dropdown(id="loc-dropdown", options=[{'label': 'Søtorvet 5, København N', 'value': 2}, {'label': 'Krügersgade 5, København K', 'value': 1}, {
                             'label': 'Folehaven 72, Valby', 'value': 3}, {'label': 'Hillerødgade 79, København N', 'value': 4}, {'label': 'Backersvej/Formosavej, København S', 'value': 5}], value=2,  style={'font-family': 'Inter'}),
                html.Div(id='crossfilter-year--slider', className="drop")
            ])
        ],  xs=12, lg=5, xl=10)
    ], justify="center"),


    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='plot')
            ], style={"margin-top": "50px"}, className='firstplot')
        ], xs=12, lg=5, xl=12),

    ], justify="center"),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='plot2')
            ], style={"margin-top": "50px"}, className='firstplot')

        ], xs=12, lg=5, xl=12)
    ], justify="left"),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='plot3')
            ], style={"margin-top": "50px", "margin-bottom": "40px"}, className='firstplot')
        ], xs=12, lg=5, xl=12)
    ])


], class_name='firstplot1')


def make_graph(df, title):
    f = px.imshow(df, template="ggplot2", color_continuous_scale="amp",  # amp
                  labels=dict(color="Antal dage overskredet"),
                  x=['Jan', 'Feb', 'Mar', 'Apr', 'Maj', "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"], text_auto=True, range_color=[0, 16]

                  )

    f.update_layout(
        yaxis_nticks=5,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgb(245,244,244)',
        width=1250,
        height=400,
        yaxis = dict(
        tickmode = 'linear',
        tick0 = 2020,
        dtick = 1
        ),


        title=dict(text=f'<b>{title}<b>', y=0.98, x=0, xanchor='left',
                   yanchor='top', font=dict(family='Inter Black 900', size=20)),



        legend_title="Legend Title",
        font=dict(
            family="Inter",
            size=17,
            color="rgb(126,121,120)"
        ),
        yaxis_title=None,
        xaxis_title=None
    )

    f.update_xaxes(side="top")
    f.update_traces(hoverongaps=False)
    f.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

    return f


@app.callback(
    Output('plot', 'figure'),
    Output('plot2', 'figure'),
    Output('plot3', 'figure'),
    Output('heading', component_property='children'),
    Input('loc-dropdown', 'value'))
def update_graph(val):
    dict = {1: "Krügersgade 5", 2: "Søtorvet 5", 3: "Folehaven 72",
            4: "Hillerødgade 79", 5: "Backersvej/Formosavej"}

    name = dict[val]
    df = get_data(val)
    df = process_data(df)
    pollution = df.pivot_table(
        values='ExceededPM2', columns="month", index="year", aggfunc=np.sum)
    pollution2 = df.pivot_table(
        values='ExceededPM10', columns="month", index="year", aggfunc=np.sum)
    pollution3 = df.pivot_table(
        values='ExceededNO2', columns="month", index="year", aggfunc=np.sum)

    fig = make_graph(pollution, "PM2.5")
    fig2 = make_graph(pollution2, "PM10")
    fig3 = make_graph(pollution3, "NO2")

    return fig, fig2, fig3, name


if __name__ == '__main__':
    app.run_server(debug=True)
