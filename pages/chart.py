import dash

dash.register_page(__name__)


import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash import Input, Output, callback
import pandas as pd

def load_com(exchange):
    with open(f'datas/{exchange}/com.txt') as f:
        content = f.read()
        com = content.split(',')
        f.close()
    return com[:-1]

exchange_com_dict = dict(hose=load_com('hose'), hnx=load_com('hnx'), upcom=load_com('upcom'))
exchanges = list(exchange_com_dict.keys())

coms = load_com('hose')
indis  = ['sma-5','sma-50', 'sma-200']

def layout(com=coms[0], indi = indis[1]):
    return html.Div([
        html.Div(
            [dcc.Dropdown(
            id = 'exchange',
            options = [
                {"label": x, "value": x} for x in exchanges
            ],
            value=com,
            clearable=False,
        ),
                dcc.Dropdown(
            id = 'com',
            value=com,
            clearable=False,
        ),
        dcc.Dropdown(
            id = 'indicator',
            options = [
                {"label": x, "value": x} for x in indis
            ],
            value=[indi],
            clearable=False,
            multi=True,
            
        )
        ]),
    dcc.Graph(className='plot', id='chart')
])

def SMA(df, day):
    return df.Close.rolling(day).mean().tail(100)

sma_color = ['blue','red','orange']

@callback(Output('com','options'),Input('exchange','value'))
def update_date_dropdown(name):
    return [{'label': i, 'value': i} for i in exchange_com_dict[name]]

@callback(Output("chart", "figure"),Input("exchange", "value"), Input("com", "value"), Input('indicator', 'value'))
def update_bar_chart(exchange,com, indi):
    df = pd.read_csv(f'datas/{exchange}/{com}.csv')
    df.drop(labels='Unnamed: 0', axis=1, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'],format='%d/%m/%Y')
    # df['SMA'] = df.Close.rolling(20).mean()
    
    smafig = []
    for i in range(len(indi)):
        if indi[i].startswith('sma'):
            day = int(indi[i].split('-')[1])
            smafig.append(go.Scatter(x=df.Date.tail(100), y=SMA(df, day), line=dict(color=sma_color[i], width=1)))

    df = df.tail(100)
    figdata=[go.Candlestick(x=df['Date'],
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'])]
    figdata.extend(smafig)
    
    fig = go.Figure(data= figdata)
    fig.update_layout(title= dict(text='100 days chart'),                 
                            paper_bgcolor='#ffffff',
                            plot_bgcolor='#ffffff',
                            modebar=dict(add=['drawopenpath','eraseshape'],remove=['lasso'],orientation='v'),xaxis_rangeslider_visible=False)
    fig.update_yaxes(title_text= 'Price',
                            showgrid=False,
                            )

    fig.update_traces(increasing_fillcolor='#26A69A',increasing_line=dict(color='#26A69A',width=0.5),
    decreasing_fillcolor='#EF5350',decreasing_line=dict(color='#EF5350',width=0.5),line=dict(width=0.5), selector=dict(type='candlestick'))
    return fig

