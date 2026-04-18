from dash import dcc, html

# Примеры и подсказки для пользователя
KERNEL_EXAMPLES = {
    "Экспоненциальное": "0.2 * np.exp(-(x - t))",
    "Косинусоидальное": "0.3 * np.cos(x - t)",
    "Параболическое": "0.1 * (x - t)**2",
    "Синусоидальное": "0.25 * np.sin(x + t)",
    "Модифицированное экспоненциальное": "0.15 * np.exp(-np.abs(x - t))"
}

RHS_EXAMPLES = {
    "Синус": "np.sin(x)",
    "Косинус двойного аргумента": "np.cos(2*x)",
    "Парабола": "x * (1-x)",
    "Экспонента": "np.exp(-x)",
    "Синусоида": "np.sin(np.pi*x)"
}

def create_input_panel():
    """Создает панель ввода параметров"""
    return html.Div([
        html.Div([
            html.Div([
                html.Label('Ядро K(x,t):', style={'fontWeight': 'bold', 'fontSize': '1.1em'}),
                dcc.Textarea(
                    id='kernel-input',
                    placeholder='Введите выражение для ядра K(x,t) (используйте x и t как переменные)\nНапример: 0.2 * np.exp(-(x - t))',
                    value='0.2 * np.exp(-(x - t))',
                    style={
                        'width': '100%',
                        'height': '100px',
                        'fontFamily': 'monospace',
                        'fontSize': '14px',
                        'padding': '10px',
                        'borderRadius': '5px',
                        'border': '2px solid #bdc3c7'
                    }
                ),
                html.Div([
                    html.Span('Примеры: ', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                    html.Div([
                        html.Button(name, id={'type': 'kernel-example', 'index': i}, 
                                   style={'margin': '2px', 'padding': '5px 10px', 
                                          'backgroundColor': '#ecf0f1', 'border': 'none',
                                          'borderRadius': '3px', 'cursor': 'pointer'})
                        for i, name in enumerate(KERNEL_EXAMPLES.keys())
                    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '5px'})
                ], style={'marginTop': '10px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 
                         'borderRadius': '5px'})
            ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
            
            html.Div([
                html.Label('Правая часть f(x):', style={'fontWeight': 'bold', 'fontSize': '1.1em'}),
                dcc.Textarea(
                    id='rhs-input',
                    placeholder='Введите выражение для правой части f(x) (используйте x как переменную)\nНапример: np.sin(x)',
                    value='np.sin(x)',
                    style={
                        'width': '100%',
                        'height': '100px',
                        'fontFamily': 'monospace',
                        'fontSize': '14px',
                        'padding': '10px',
                        'borderRadius': '5px',
                        'border': '2px solid #bdc3c7'
                    }
                ),
                html.Div([
                    html.Span('Примеры: ', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                    html.Div([
                        html.Button(name, id={'type': 'rhs-example', 'index': i},
                                   style={'margin': '2px', 'padding': '5px 10px',
                                          'backgroundColor': '#ecf0f1', 'border': 'none',
                                          'borderRadius': '3px', 'cursor': 'pointer'})
                        for i, name in enumerate(RHS_EXAMPLES.keys())
                    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '5px'})
                ], style={'marginTop': '10px', 'padding': '10px', 'backgroundColor': '#f8f9fa',
                         'borderRadius': '5px'})
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '20px'}),
        
        html.Div([
            html.Label('Количество точек N:', style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='n-slider',
                min=50,
                max=500,
                step=50,
                value=200,
                marks={i: str(i) for i in range(100, 2001, 200)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ], style={'padding': '20px'}),
        
        html.Div([
            html.Button('Решить уравнение', id='solve-button', 
                       style={
                           'backgroundColor': '#3498db',
                           'color': 'white',
                           'padding': '10px 20px',
                           'fontSize': '16px',
                           'border': 'none',
                           'borderRadius': '5px',
                           'cursor': 'pointer',
                           'margin': '10px auto',
                           'display': 'block',
                           'width': '200px'
                       }),
            
            # Индикатор загрузки
            html.Div([
                html.Div(id='loading-indicator', children=[
                    html.Div(style={
                        'border': '4px solid #f3f3f3',
                        'borderTop': '4px solid #3498db',
                        'borderRadius': '50%',
                        'width': '30px',
                        'height': '30px',
                        'animation': 'spin 1s linear infinite',
                        'margin': '0 auto'
                    }),
                    html.P('Вычисление... Пожалуйста, подождите', 
                           style={'textAlign': 'center', 'marginTop': '10px', 'color': '#7f8c8d'})
                ], style={'display': 'none', 'marginTop': '20px'})
            ], style={'textAlign': 'center'})
        ]),
    ])