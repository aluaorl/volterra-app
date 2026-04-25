#
import dash
from dash import html
from components.input_panel import create_input_panel
from components.result_panels import create_result_panels
from components.history_panel import create_history_panel
from components.callbacks import register_callbacks

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div(children=[
    html.H1(children='Решатель ИДУ Вольтерра'),
    create_input_panel(),
    create_result_panels(),
    create_history_panel(),
], id='main-container')

register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)