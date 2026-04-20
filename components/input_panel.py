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
        # Store для хранения состояния раскрытия блоков
        dcc.Store(id='kernel-examples-state', data={'expanded': False}),
        dcc.Store(id='rhs-examples-state', data={'expanded': False}),
        
        html.Div([
            # Блок для ядра K(x,t) - объединен в одну карточку
            html.Div([
                html.Div([
                    html.Label('Ядро K(x,t):', style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#1a5276', 'marginBottom': '10px', 'display': 'block'}),
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
                            'border': '2px solid #a8d5e8',
                            'backgroundColor': '#fff',
                            'transition': 'border-color 0.3s ease'
                        }
                    ),
                    html.Div(id='kernel-validation', style={'color': '#c0392b', 'fontSize': '0.85em', 'marginTop': '5px'}),
                ], style={'marginBottom': '15px'}),
                
                # Заголовок для выпадающего списка примеров ядер - УМЕНЬШЕН
                html.Div([
                    html.Div('▼ Примеры ядер K(x,t):', 
                            style={
                                'fontWeight': 'bold', 
                                'marginBottom': '5px', 
                                'color': '#1a5276',
                                'cursor': 'pointer',
                                'userSelect': 'none',
                                'padding': '5px 10px',
                                'backgroundColor': '#e8eef2',
                                'borderRadius': '6px',
                                'transition': 'all 0.3s ease',
                                'fontSize': '0.9em'
                            },
                            id='kernel-examples-toggle'),
                    html.Div(
                        id='kernel-examples-content',
                        style={'display': 'none', 'marginTop': '8px'},
                        children=[
                            html.Div([
                                html.Button(
                                    name, 
                                    id={'type': 'kernel-example', 'index': i},
                                    style={
                                        'width': '55%',
                                        'textAlign': 'left',
                                        'margin': '3px 0',
                                        'padding': '5px 10px',
                                        'fontSize': '11px',
                                        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                        'color': 'white',
                                        'border': 'none',
                                        'borderRadius': '15px',
                                        'cursor': 'pointer',
                                        'transition': 'transform 0.2s ease, box-shadow 0.2s ease'
                                    }
                                )
                                for i, name in enumerate(KERNEL_EXAMPLES.keys())
                            ])
                        ]
                    )
                ], style={'padding': '8px 12px', 'backgroundColor': '#f8f9fa', 
                         'borderRadius': '8px', 'border': '1px solid #e0e0e0'})  # Уменьшен padding
            ], style={
                'width': '48%', 
                'display': 'inline-flex',
                'flexDirection': 'column',
                'marginRight': '2%', 
                'verticalAlign': 'top',
                'padding': '15px',  # Уменьшен с 20px
                'border': '2px solid #a8d5e8',
                'borderRadius': '12px',
                'backgroundColor': '#ffffff',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'minHeight': 'auto'
            }),
            
            # Блок для правой части f(x) - объединен в одну карточку
            html.Div([
                html.Div([
                    html.Label('Правая часть f(x):', style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#1a5276', 'marginBottom': '10px', 'display': 'block'}),
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
                            'border': '2px solid #a8d5e8',
                            'backgroundColor': '#fff',
                            'transition': 'border-color 0.3s ease'
                        }
                    ),
                    html.Div(id='rhs-validation', style={'color': '#c0392b', 'fontSize': '0.85em', 'marginTop': '5px'}),
                ], style={'marginBottom': '15px'}),
                
                # Заголовок для выпадающего списка примеров правых частей - УМЕНЬШЕН
                html.Div([
                    html.Div('▼ Примеры правых частей f(x):', 
                            style={
                                'fontWeight': 'bold', 
                                'marginBottom': '5px', 
                                'color': '#1a5276',
                                'cursor': 'pointer',
                                'userSelect': 'none',
                                'padding': '5px 10px',
                                'backgroundColor': '#e8eef2',
                                'borderRadius': '6px',
                                'transition': 'all 0.3s ease',
                                'fontSize': '0.9em'
                            },
                            id='rhs-examples-toggle'),
                    html.Div(
                        id='rhs-examples-content',
                        style={'display': 'none', 'marginTop': '8px'},
                        children=[
                            html.Div([
                                html.Button(
                                    name, 
                                    id={'type': 'rhs-example', 'index': i},
                                    style={
                                        'width': '55%',
                                        'textAlign': 'left',
                                        'margin': '3px 0',
                                        'padding': '5px 10px',
                                        'fontSize': '11px',
                                        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                        'color': 'white',
                                        'border': 'none',
                                        'borderRadius': '15px',
                                        'cursor': 'pointer',
                                        'transition': 'transform 0.2s ease, box-shadow 0.2s ease'
                                    }
                                )
                                for i, name in enumerate(RHS_EXAMPLES.keys())
                            ])
                        ]
                    )
                ], style={'padding': '8px 12px', 'backgroundColor': '#f8f9fa',
                         'borderRadius': '8px', 'border': '1px solid #e0e0e0'})  # Уменьшен padding
            ], style={
                'width': '48%', 
                'display': 'inline-flex',
                'flexDirection': 'column',
                'verticalAlign': 'top',
                'padding': '15px',  # Уменьшен с 20px
                'border': '2px solid #a8d5e8',
                'borderRadius': '12px',
                'backgroundColor': '#ffffff',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'minHeight': 'auto'
            }),
        ], style={'padding': '15px', 'display': 'flex', 'justifyContent': 'space-between'}),  # Уменьшен padding
        
        # Начальное условие
        html.Div([
            html.Label('Начальное условие φ(0):', style={'fontWeight': 'bold', 'color': '#333', 'marginBottom': '8px', 'display': 'block', 'textAlign': 'left', 'fontSize': '0.95em'}),
            dcc.Input(
                id='initial-condition',
                type='number',
                value=0.0,
                step=0.1,
                style={
                    'width': '120px',
                    'padding': '6px',
                    'borderRadius': '5px',
                    'border': '2px solid #a8d5e8',
                    'fontSize': '14px',
                    'textAlign': 'center',
                    'display': 'block'
                }
            ),
        ], style={'padding': '15px', 'textAlign': 'left', 'width': '60%', 'margin': '0 auto'}),
        
        # Красивое отображение уравнения - 60% ширины, по центру
        html.Div([
            html.Div(id='equation-display', 
                     style={'padding': '10px', 'backgroundColor': '#e8eef2', 
                            'borderRadius': '8px', 'fontFamily': 'monospace', 
                            'fontSize': '1em', 'textAlign': 'center',
                            'color': '#333', 'border': '2px solid #a8d5e8',
                            'width': '60%', 'margin': '0 auto'}),
        ], style={'padding': '15px', 'marginTop': '5px'}),
        
       # Легенда функций - компактная версия
html.Div([
    html.Div([
        html.H5('▼ Поддерживаемые функции и константы:', 
                style={'color': '#1a5276', 'marginBottom': '8px', 'cursor': 'pointer', 'fontSize': '0.95em'},
                id='legend-toggle'),
        html.Div([
            # Вводная информация о синонимах
            html.Div([
                html.P('✓ Ввод распознает синонимы функций, как asin, arsin, arcsin', 
                       style={'margin': '0 0 10px 0', 'color': '#555', 'fontSize': '0.8em', 'fontStyle': 'italic'}),
            ]),
            
            html.Div([
                # Колонка 1
                html.Div([
                    html.H6('Тригонометрические и обратные:', style={'color': '#2980b9', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                    html.P('sin, cos, tan, tg, cot, ctg, sec, csc, cosec', 
                           style={'margin': '0 0 8px 0', 'color': '#333', 'fontSize': '0.8em'}),
                    html.P('arcsin, arccos, arctan, arctg, arccot, arcsec, arccsc', 
                           style={'margin': '0 0 8px 0', 'color': '#333', 'fontSize': '0.8em'}),
                    
                    html.H6('Гиперболические и обратные:', style={'color': '#2980b9', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                    html.P('sinh, sh, cosh, ch, tanh, th, coth, cth, sech, csch', 
                           style={'margin': '0 0 8px 0', 'color': '#333', 'fontSize': '0.8em'}),
                    html.P('arsinh, arcosh, artanh, arcoth, arsech, arcsch', 
                           style={'margin': '0 0 8px 0', 'color': '#333', 'fontSize': '0.8em'}),
                ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                
                # Колонка 2
                html.Div([
                    html.H6('Логарифмы:', style={'color': '#2980b9', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                    html.P('ln, lg, log, log2, log10, log(a, x)', 
                           style={'margin': '0 0 8px 0', 'color': '#333', 'fontSize': '0.8em'}),
                    
                    html.H6('Степени и корни:', style={'color': '#2980b9', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                    html.P('x^2, x**2, sqrt, sqrt(n, x)', 
                           style={'margin': '0 0 8px 0', 'color': '#333', 'fontSize': '0.8em'}),
                    
                    html.H6('Модуль и экспонента:', style={'color': '#2980b9', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                    html.P('abs(x), exp(x), e^x', 
                           style={'margin': '0 0 8px 0', 'color': '#333', 'fontSize': '0.8em'}),
                ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                
                # Колонка 3
                html.Div([
                    html.H6('Константы:', style={'color': '#2980b9', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                    html.P('pi, π, e', 
                           style={'margin': '0 0 8px 0', 'color': '#333', 'fontSize': '0.8em'}),
                    
                    html.H6('Греческие буквы:', style={'color': '#2980b9', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                    html.P('alpha, beta, gamma, delta, epsilon, zeta, eta, theta', 
                           style={'margin': '0 0 3px 0', 'color': '#333', 'fontSize': '0.75em'}),
                    html.P('iota, kappa, lambda, mu, nu, xi, pi, rho', 
                           style={'margin': '0 0 3px 0', 'color': '#333', 'fontSize': '0.75em'}),
                    html.P('sigma, tau, upsilon, phi, chi, psi, omega', 
                           style={'margin': '0 0 8px 0', 'color': '#333', 'fontSize': '0.75em'}),
                    
                ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ]),
            
        ], id='legend-content', style={'display': 'none', 'marginTop': '8px'}),
    ], style={'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'marginTop': '15px', 'border': '1px solid #e0e0e0'}),
]),
        
        html.Div([
            html.Button('Решить уравнение', id='solve-button',  disabled=True,
                       style={
                           'backgroundColor': '#3498db',
                           'color': 'white',
                           'padding': '8px 16px',
                           'fontSize': '14px',
                           'border': 'none',
                           'borderRadius': '5px',
                           'cursor': 'pointer',
                           'margin': '10px auto',
                           'display': 'block',
                           'width': '180px'
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
                           style={'textAlign': 'center', 'marginTop': '10px', 'color': '#666', 'fontSize': '0.9em'})
                ], style={'display': 'none', 'marginTop': '20px'})
            ], style={'textAlign': 'center'})
        ]),
    ])