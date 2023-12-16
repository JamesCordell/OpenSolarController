import os
import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import dash_table
from sqlalchemy import create_engine
import warnings # see bug https://github.com/pandas-dev/pandas/issues/45660
import numbers
import numpy as np
from datetime import date
import time

app_name = 'dash-mysqledataplot'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'openSolar Controller data'

@app.callback(Output('computed-table-status','data'),
              Input('interval-component-status', 'n_intervals'))
def getStatus(data):

    url = 'mariadb+mariadbconnector://openSolar:openSolar@localhost/openSolar' #?charset=utf8mb4'

    engine = create_engine(url, echo=True)
    connection = engine.raw_connection()

    with warnings.catch_warnings():
      warnings.simplefilter('ignore', UserWarning)

      status = pd.read_sql("""SELECT sensorId,value,Description from openSolar.status WHERE sensorId IN('cvcc','fw-version','i-out','model','power','protect','t1','t2','t3','t4','u-in','u-out')""",connection)
    data=status.to_dict("records")
    #columns=[{"name": i, "id": i} for i in status.columns]
    return data

#@app.callback(
#    Output('computed-table-editable', 'data'),
#    Input('computed-table-editable', 'data_timestamp'),
#    State('computed-table-editable', 'data'))
#def update_rows(timestamp, rows):
#    cnxn = mod.connect(user='openSolar',password='openSolar',database='openSolar',host='ubuntu.local',port=3306)

#    mycursor = cnxn.cursor()

#    for row in rows:
#        try:
#            sql = "UPDATE status SET value= %s WHERE sensorId=%s"
#            val = ( row['value'] , row['sensorId'] )
#            mycursor.execute(sql, val)
#        except:
#            row['output-data'] = 'NA'
#    cnxn.commit()
#
#    return rows

@app.callback(
              Output('computed-table-editable','data'),
              #Input('interval-component-editable', 'n_intervals'),
              Input('computed-table-editable', 'data_timestamp'),
              State('computed-table-editable', 'data'))
def getEditable( data_timestamp, rows):

    url = 'mariadb+mariadbconnector://openSolar:openSolar@localhost/openSolar' #?charset=utf8mb4'
    engine = create_engine(url, echo=True)
    connection = engine.raw_connection()
    cursor = connection.cursor()

    status = pd.read_sql("""SELECT sensorId,value,description,time from openSolar.status WHERE sensorId IN('control0-loop-onoff','i-set','lock','on','s-ocp','s-opp','s-ovp','u-set','control1-on2offThress','control1-off2onThress')""",connection)
    data=status.to_dict("records")

    dataFromDb = pd.DataFrame(data)
    dataFromWeb = pd.DataFrame(rows)
    webUpdateTime = None
    if rows is not None:
      if isinstance(data_timestamp, numbers.Number): 
        webUpdateTime = int(data_timestamp / 1000)
        df = dataFromWeb[['sensorId','value']].join(dataFromDb[['sensorId','value','time']],lsuffix='_web',rsuffix='_db',how='left')
        df = df[df['value_web'] != df['value_db']]
        df['value_newest'] = np.where( df['time'] > webUpdateTime, df['value_db'], df['value_web'] )
        if data_timestamp is not None:
          for i,r in df.iterrows():
            try:
              sql = "UPDATE status SET value=%s,time=%s WHERE sensorId=%s"
              val = ( r['value_newest'] ,webUpdateTime ,r['sensorId_web'] )
              for row in data:
                if row['sensorId'] == r['sensorId_web']:
                  row.update( { 'value': r['value_newest'] })
              cursor.execute(sql, val)
            except:
              row['output-data'] = 'NA'
          connection.commit()
        else:
          print(data_timestamp)

    return data


@app.callback(
    Output('output-container-date-picker-single', 'children'),
    Input('my-date-picker-single', 'date'))
def update_output(date_value):
    string_prefix = 'You have selected: '
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime('%B %d, %Y')
        return string_prefix + date_string

app.layout = html.Div([
    html.Div([
        html.H1("OpenSolarControl", style={'textAlign': 'center'}),
	    dcc.Graph(
		    id='collector-graph',
        ),
        dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds
            n_intervals=0
        )
    ]),
    html.Div([
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=date(1995, 8, 5),
        max_date_allowed=date(2023, 1, 10),
        initial_visible_month=date(2022,12,25),
        date=date(2022, 12, 25)
    ),
    html.Div(id='output-container-date-picker-single')
    ]),
    html.Div([ 
        dash_table.DataTable(
            id="computed-table-status",
            css=[{
                'selector': '.dash-spreadsheet td div',
                'rule': '''
                line-height: 15px;
                text-align: left;
                max-height: 30px; min-height: 30px; height: 30px;
                display: block;
                overflow-y: hidden;
                '''
            }],
            editable=False,
            style_cell={
                'textAlign': 'left',
                 'minWidth': '20%',
            }),
            dcc.Interval(
                id='interval-component-status',
                interval=5*1000, # in milliseconds
                n_intervals=0
            )
    ]
    ,style={'width': '49%', 'display': 'inline-block'}),
    html.Div([ 
        dash_table.DataTable(
            id="computed-table-editable",
            columns=[{"name": i, "id": i} for i in ['sensorId', 'value', 'description','time']],  #columns=[{"name": i, "id": i} for i in status.columns]
            #data=getEditable(),
            css=[{
                'selector': '.dash-spreadsheet td div',
                'rule': '''
                line-height: 15px;
                text-align: left;
                max-height: 30px; min-height: 30px; height: 30px;
                display: block;
                overflow-y: hidden;
                '''
            }],
            editable=True,
            style_cell={
                'textAlign': 'left',
                 'minWidth': '20%',
            }
        )
        #,
        #dcc.Interval(
        #    id='interval-component-editable',
        #    interval=5*1000, # in milliseconds
        #    n_intervals=0
        #) 
    ]
    ,style={'width': '44%', 'display': 'inline-block', 'margin-left': '5%'}),
])


# Multiple components can update everytime interval gets fired.
@app.callback(Output('collector-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(cnxn):

    url = 'mariadb+mariadbconnector://openSolar:openSolar@localhost/openSolar' #?charset=utf8mb4'

    engine = create_engine(url, echo=True)
    connection = engine.raw_connection()

    t1 = pd.read_sql("SELECT from_unixtime(time) AS time,value FROM openSolar.log WHERE sensorId = 't1' AND time > UNIX_TIMESTAMP() - (24 * 60 * 60)", connection)

    t2 = pd.read_sql("SELECT from_unixtime(time) AS time,value FROM openSolar.log WHERE sensorId = 't2' AND time > UNIX_TIMESTAMP() - (24 * 60 * 60)", connection)

    t3 = pd.read_sql("SELECT from_unixtime(time) AS time,value FROM openSolar.log WHERE sensorId = 't3' AND time > UNIX_TIMESTAMP() - (24 * 60 * 60)", connection)

    t4 = pd.read_sql("SELECT from_unixtime(time) AS time,value FROM openSolar.log WHERE sensorId = 't4' AND time > UNIX_TIMESTAMP() - (24 * 60 * 60)", connection)
    
    control1on2offThress = pd.read_sql("SELECT from_unixtime(unix_timestamp() - (24 * 60 * 60)) AS time,value FROM openSolar.status WHERE sensorId = 'control1-on2offThress'", connection)
    control1off2onThress = pd.read_sql("SELECT from_unixtime(unix_timestamp() - (24 * 60 * 60)) AS time,value FROM openSolar.status WHERE sensorId = 'control1-off2onThress'", connection)

    figure=go.Figure()
    figure.add_trace(go.Scatter(
        x=t4['time'],
        y=t4['value'],
        line=dict(color='#FF0000', width=1),
        name='t4',
        mode='lines'))
 
    figure.add_trace(go.Scatter(
        x=t3['time'],
        y=t3['value'],
        line=dict(color='#0000FF', width=1),
        name='t3',
        mode='lines'))

    figure.add_trace(go.Scatter(
        x=t2['time'],
        y=t2['value'],
        line=dict(color='#FF33FF', width=1),
        name='t2',
        mode='lines'))

    figure.add_trace(go.Scatter(
        x=t1['time'],
        y=t1['value'],
        line=dict(color='#FF8333', width=1),
        name='t1',
        mode='lines'))

    y_off2on = [control1off2onThress['value'][0] , control1off2onThress['value'][0]]
    figure.add_trace(go.Scatter(
        x=[control1off2onThress['time'][0] , time.strftime("%Y-%m-%d %H:%M:%S.000", time.localtime()) ],
        y=y_off2on,
        line=dict(color='#00DD00', width=1),
        name='control0-off2onThress',
        mode='lines'))
    y_on2off = [int(control1on2offThress['value'][0]) + int(t1['value'].iloc[-1]) , int(control1on2offThress['value'][0]) + int(t1['value'].iloc[-1])]
    figure.add_trace(go.Scatter(
        x=[control1on2offThress['time'][0] , time.strftime("%Y-%m-%d %H:%M:%S.000", time.localtime()) ],
        y=y_on2off,
        line=dict(color='#000000', width=1),
        name='control0-on2offThress',
        mode='lines'))

    figure['layout']['uirevision'] = 'some_value'
    figure.update_layout(height=600)

    return figure

    
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port="8080",debug=True)


