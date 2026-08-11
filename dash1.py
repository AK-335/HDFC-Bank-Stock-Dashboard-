import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import base64
import io

app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("Stock Dashboard", style={"textAlign": "center"}),

    # Upload CSV
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload File here'),
        multiple=False
    ),

    html.Br(),

    # 🔽 Dropdown
    dcc.Dropdown(
        id='column-select',
        options=[
            {'label': 'Open', 'value': 'OPEN'},
            {'label': 'Close', 'value': 'CLOSE'},
            {'label': 'High', 'value': 'HIGH'},
            {'label': 'Low', 'value': 'LOW'}
        ],
        value='OPEN',
        style={"width": "50%", "margin": "auto"}
    ),

    html.Br(),

    # 📅 Date Range Picker (NEW)
    dcc.DatePickerRange(
        id='date-range',
        start_date_placeholder_text="Start Date",
        end_date_placeholder_text="End Date",
        style={"margin": "auto", "display": "block"}
    ),

    html.Br(),

    # KPI Cards
    html.Div(id='kpi-cards', style={
        "display": "flex",
        "justifyContent": "space-around",
        "marginBottom": "30px"
    }),

    # Graph
    dcc.Graph(id='stock-chart')

])


@app.callback(
    [Output('kpi-cards', 'children'),
     Output('stock-chart', 'figure')],
    [Input('upload-data', 'contents'),
     Input('column-select', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_dashboard(contents, selected_col, start_date, end_date):

    if contents is None:
        return "", {}

    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Clean column names
        df.columns = df.columns.str.strip().str.upper()

        # Fix DATE
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

        # Clean selected column
        df[selected_col] = df[selected_col].astype(str).str.replace(',', '')
        df[selected_col] = pd.to_numeric(df[selected_col], errors='coerce')

        # Drop bad rows
        df = df.dropna(subset=['DATE', selected_col])

        # 📅 Apply Date Filter (NEW)
        if start_date and end_date:
            df = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]

        # KPI
        min_val = df[selected_col].min()
        max_val = df[selected_col].max()
        avg_val = round(df[selected_col].mean(), 2)

        # Cards
        cards = [
            card("Min " + selected_col, min_val),
            card("Max " + selected_col, max_val),
            card("Avg " + selected_col, avg_val)
        ]

        # Chart
        fig = px.line(df, x='DATE', y=selected_col,
                      title=f"{selected_col} Price Trend")

        return cards, fig

    except Exception as e:
        print("ERROR:", e)
        return html.Div("Error loading file. Check CSV format."), {}


def card(title, value):
    return html.Div([
        html.H4(title),
        html.H2(value)
    ], style={
        "border": "2px solid black",
        "padding": "15px",
        "width": "30%",
        "textAlign": "center",
        "borderRadius": "10px",
        "boxShadow": "2px 2px 5px grey"
    })


if __name__ == '__main__':
    app.run(debug=True)
