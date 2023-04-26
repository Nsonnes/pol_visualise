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
    #print(end_hour)
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
    #print(df)
    df["EndLocal"] = pd.to_datetime(df["EndLocal"])  # format without hour
    df["year"] = df['EndLocal'].dt.year
    #df["EndLocal"] = df["EndLocal"].dt.floor('D')
    df["EndLocal"] = df["EndLocal"].dt.date
    # print(df[["EndLocal"]])

    #df_pm["month"] = df_pm['EndLocal'].dt.month
    #df["year"] = df_pm['EndLocal'].dt.year
    #df["day"] = df['EndLocal'].dt.day
    df["ExceededPM2"] = df["PM2_5"].apply(check_limit_PM2)
    df["ExceededNO2"] = df["NO2"].apply(check_limit_NO2)
    df["ExceededPM10"] = df["PM10"].apply(check_limit_PM10)

    return df


def pivot_data(df, var):

    return df.pivot_table(values=var, columns='EndLocal', aggfunc="first")


df = get_data()
#(df)
df = process_data(df)


# Initialize the app
#app = Dash(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA],  meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}])
server = app.server



# App layout


# Add controls to build the interaction






# Run the app





app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Luftforurening i København")
        ], xs=9, lg=5, xl=8),
    ], justify="center"),

    dbc.Row([
        dbc.Col([
            html.Div([
    dcc.RangeSlider(marks={2020:"2020", 2021:"2021", 2022:"2022", 2023:"2023"}, step=1, min=2020,max=2023, value=[2020,2023], dots=True, id='my-range-slider'),
    html.Div(id='crossfilter-year--slider')
            ])
        ],  xs=9, lg=5, xl=10)
    ], justify="left"),

    dbc.Row([
        dbc.Col([
                html.Div(
                children="", className="box1",
                style={
                    'backgroundColor': 'rgb(54, 13, 18)',
                    'color': 'lightsteelblue',
                    'height': '30px',
                    'width': '50px',
                    'display': 'inline-block',
                    "margin-left": '100px',
                    "margin-top": '40px'

                }


            ), html.Div(children="Overskrider WHO grænseværdi", style={'textAlign': 'center', 'display': 'inline-block', "margin-left": '15px'}),
                            html.Div(
                children="", className="box1",
                style={
                    'backgroundColor': 'rgb(240, 236, 236)',
                    'color': 'lightsteelblue',
                    'height': '30px',
                    'width': '50px',
                    'display': 'inline-block',
                    "margin-left": '100px',
                    "margin-top": '40px'

                }


            ), html.Div(children="Overskrider ikke WHO grænseværdi", style={'textAlign': 'center', 'display': 'inline-block', "margin-left": '15px'}),

    
            
        ],xs=8, lg=5, xl=10)
    ], justify="left"),


    dbc.Row([
        dbc.Col([
            dcc.Graph(id='plot')
        ], xs=12, lg=5, xl=10),

    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='plot2')
 
        ], xs=12, lg=5, xl=10)
    ], justify="left"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="plot3")
        ], xs=12, lg=5, xl=10)
    ])


])


def get_range_val(range, list):

    for year in range:
        if year not in list:
            list.append(year)
            list.sort()
    print(range)
    return list

@app.callback(
    Output('plot', 'figure'),
    Output('plot2','figure'),
    Output('plot3','figure'),
    Input('my-range-slider', 'value'))



def update_graph(val):
    print(val)
    # instead of updating graph from three seperate calls, make all the calls from here
    vars = ["ExceededPM2","ExceededPM10","ExceededNO2"]
    if len(set(val)) == 1:
        df_sorted = df.loc[df['year']==val[0]]
    else:
        year_range = range(val[0],val[1])
        range_val = get_range_val(year_range, val)
        df_sorted = df.loc[df['year'].isin(range_val)]

    


    #df_sorted = df.loc[df['year'].isin(range_val)]

    df_piv = pivot_data(df_sorted, "ExceededPM2")
    df_piv2 = pivot_data(df_sorted, "ExceededPM10")
    df_piv3 = pivot_data(df_sorted, "ExceededNO2")

    df_list = [df_piv,df_piv2, df_piv3]

    names = {"ExceededPM2": "PM2.5",
            "ExceededPM10": "PM10", "ExceededNO2": "NO2"}
    exceeded = {0: "Nej", 1: "Ja"}
    fig = px.imshow(df_piv, template="ggplot2",
                    title=f"PM2.5 målt ved søtorvet 5", zmin=0, zmax=1, color_continuous_scale='amp')

    fig.update_traces(hoverongaps=False, showscale=False,
                    hovertemplate="Pollutant measured: %{y}"
                    "<br>Date: %{x}"
                    "<br>Overskrider grænseværdi: %{z}")
    fig.update_layout(xaxis_nticks=12, xaxis_title=None)
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_coloraxes(showscale=False)
    fig.layout.coloraxis.colorbar.title = 'Title<br>Here'
    fig.update_traces(showscale=False)
    

    fig2 = px.imshow(df_piv2, template="ggplot2",
            title=f"PM10 målt ved søtorvet 5", zmin=0, zmax=1, color_continuous_scale='amp')

    fig2.update_traces(hoverongaps=False, showscale=False,
                    hovertemplate="Pollutant measured: %{y}"
                    "<br>Date: %{x}"
                    "<br>Overskrider grænseværdi: %{z}")
    fig2.update_layout(xaxis_nticks=12, xaxis_title=None)
    fig2.update_yaxes(visible=False, showticklabels=False)
    fig2.update_coloraxes(showscale=False)
    fig2.layout.coloraxis.colorbar.title = 'Title<br>Here'
    fig2.update_traces(showscale=False)

    fig3 = px.imshow(df_piv3, template="ggplot2",
        title=f"NO2 målt ved søtorvet 5", zmin=0, zmax=1, color_continuous_scale='amp')

    fig3.update_traces(hoverongaps=False, showscale=False,
                    hovertemplate="Pollutant measured: %{y}"
                    "<br>Date: %{x}"
                    "<br>Overskrider grænseværdi: %{z}")
    fig3.update_layout(xaxis_nticks=12, xaxis_title=None)
    fig3.update_yaxes(visible=False, showticklabels=False)
    fig3.update_coloraxes(showscale=False)
    fig3.layout.coloraxis.colorbar.title = 'Title<br>Here'
    fig3.update_traces(showscale=False)



    

    return fig, fig2, fig3

if __name__ == '__main__':
    app.run_server(debug=True)
