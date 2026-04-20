from dash import dcc, html

# Примеры и подсказки для пользователя
KERNEL_EXAMPLES = {
    "Экспоненциальное": "0.2 * exp(-(x - t))",
    "Косинусоидальное": "0.3 * cos(x - t)",
    "Параболическое": "0.1 * (x - t)^2",
    "Синусоидальное": "0.25 * sin(x + t)",
    "Модифицированное экспоненциальное": "0.15 * exp(-abs(x - t))"
}

RHS_EXAMPLES = {
    "Синус": "sin(x)",
    "Косинус двойного аргумента": "cos(2*x)",
    "Парабола": "x * (1-x)",
    "Экспонента": "exp(-x)",
    "Синусоида": "sin(pi*x)"
}

def create_input_panel():
    """Создает панель ввода параметров"""
    return html.Div([
        html.Div([
            html.Div([
                html.Label('Ядро K(x,t):', style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#333'}),
                dcc.Textarea(
                    id='kernel-input',
                    placeholder='Введите выражение для ядра K(x,t) (используйте x и t как переменные)',
                    value='0.2 * exp(-(x - t))',
                    n_blur=0,
                    style={
                        'width': '100%',
                        'height': '60px',
                        'fontFamily': 'monospace',
                        'fontSize': '13px',
                        'padding': '8px',
                        'borderRadius': '5px',
                        'border': '1px solid #ccc',
                        'backgroundColor': '#fff'
                    }
                ),
                html.Div(id='kernel-validation', style={'color': '#c0392b', 'fontSize': '0.85em', 'marginTop': '5px'}),
                html.Div([
                    html.Span('Примеры ядер K(x,t): ', style={'fontWeight': 'bold', 'marginRight': '10px', 'color': '#555'}),
                    html.Div([
                        html.Button(name, id={'type': 'kernel-example', 'index': i}, 
                                   style={'margin': '2px', 'padding': '4px 8px', 'fontSize': '12px',
                                          'backgroundColor': '#e0e0e0', 'border': '1px solid #ccc',
                                          'borderRadius': '3px', 'cursor': 'pointer'})
                        for i, name in enumerate(KERNEL_EXAMPLES.keys())
                    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '5px'})
                ], style={'marginTop': '10px', 'padding': '8px', 'backgroundColor': '#f0f0f0', 
                         'borderRadius': '5px'})
            ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
            
            html.Div([
                html.Label('Правая часть f(x):', style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#333'}),
                dcc.Textarea(
                    id='rhs-input',
                    placeholder='Введите выражение для правой части f(x) (используйте x как переменную)',
                    value='sin(x)',
                    n_blur=0,
                    style={
                        'width': '100%',
                        'height': '60px',
                        'fontFamily': 'monospace',
                        'fontSize': '13px',
                        'padding': '8px',
                        'borderRadius': '5px',
                        'border': '1px solid #ccc',
                        'backgroundColor': '#fff'
                    }
                ),
                html.Div(id='rhs-validation', style={'color': '#c0392b', 'fontSize': '0.85em', 'marginTop': '5px'}),
                html.Div([
                    html.Span('Примеры правых частей: ', style={'fontWeight': 'bold', 'marginRight': '10px', 'color': '#555'}),
                    html.Div([
                        html.Button(name, id={'type': 'rhs-example', 'index': i},
                                   style={'margin': '2px', 'padding': '4px 8px', 'fontSize': '12px',
                                          'backgroundColor': '#e0e0e0', 'border': '1px solid #ccc',
                                          'borderRadius': '3px', 'cursor': 'pointer'})
                        for i, name in enumerate(RHS_EXAMPLES.keys())
                    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '5px'})
                ], style={'marginTop': '10px', 'padding': '8px', 'backgroundColor': '#f0f0f0',
                         'borderRadius': '5px'})
            ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '20px'}),
        
        html.Div([
            html.Label('Количество точек N (от 50 до 500, шаг 50):', style={'fontWeight': 'bold', 'color': '#333'}),
            html.Div([
                dcc.Input(
                    id='n-input',
                    type='number',
                    min=50,
                    max=500,
                    step=50,
                    value=200,
                    style={
                        'width': '150px',
                        'padding': '8px',
                        'borderRadius': '5px',
                        'border': '2px solid #2980b9',
                        'fontSize': '14px',
                        'textAlign': 'center'
                    }
                ),
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginTop': '10px'}),
        ], style={'padding': '20px', 'textAlign': 'center'}),
        
        # Красивое отображение уравнения (без заголовка)
        html.Div([
            html.Div(id='equation-display', 
                     style={'padding': '12px', 'backgroundColor': '#e8eef2', 
                            'borderRadius': '8px', 'fontFamily': 'monospace', 
                            'fontSize': '1.1em', 'textAlign': 'center',
                            'color': '#333'}),
        ], style={'padding': '20px', 'marginTop': '10px'}),
        
        # Легенда функций (без смайликов)
        html.Div([
            html.Div([
                html.H5('Поддерживаемые функции и константы:', 
                        style={'color': '#1a5276', 'marginBottom': '10px', 'cursor': 'pointer'},
                        id='legend-toggle'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.H6('Тригонометрические:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('sin, cos, tan, cot, sec, csc', style={'margin': '0 0 10px 0', 'color': '#333'}),
                            html.H6('Обратные тригонометрические:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('arcsin, arccos, arctan, arccot', 
                                   style={'margin': '0 0 10px 0', 'color': '#333'}),
                            html.H6('Гиперболические:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('sinh, cosh, tanh, coth', style={'margin': '0 0 10px 0', 'color': '#333'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.H6('Обратные гиперболические:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('asinh, acosh, atanh', style={'margin': '0 0 10px 0', 'color': '#333'}),
                            html.H6('Логарифмы и степени:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('ln, lg, log, log2, exp, sqrt, abs', style={'margin': '0 0 10px 0', 'color': '#333'}),
                            html.H6('Константы:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('pi, e', style={'margin': '0 0 10px 0', 'color': '#333'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.H6('Особенности ввода:', style={'color': '#2980b9', 'marginBottom': '5px'}),
                            html.P('2sinx → 2*sin(x) - умножение автоматическое', style={'margin': '0 0 5px 0', 'color': '#333'}),
                            html.P('sinx → sin(x) - скобки автоматические', style={'margin': '0 0 5px 0', 'color': '#333'}),
                            html.P('x^2 или x**2 - степень', style={'margin': '0 0 5px 0', 'color': '#333'}),
                            html.P('Регистр не важен', style={'margin': '0 0 5px 0', 'color': '#333'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ])
                ], id='legend-content', style={'display': 'none', 'marginTop': '10px'}),
            ], style={'padding': '15px', 'backgroundColor': '#f0f0f0', 'borderRadius': '8px', 'marginTop': '20px'}),
        ]),
        
        html.Div([
            html.Button('Решить уравнение', id='solve-button',  disabled=True,
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
            
            html.Div([
                html.Div(id='loading-indicator', children=[
                    html.Div(style={
                        'border': '4px solid #e0e0e0',
                        'borderTop': '4px solid #3498db',
                        'borderRadius': '50%',
                        'width': '30px',
                        'height': '30px',
                        'animation': 'spin 1s linear infinite',
                        'margin': '0 auto'
                    }),
                    html.P('Вычисление... Пожалуйста, подождите', 
                           style={'textAlign': 'center', 'marginTop': '10px', 'color': '#666'})
                ], style={'display': 'none', 'marginTop': '20px'})
            ], style={'textAlign': 'center'})
        ]),
    ])