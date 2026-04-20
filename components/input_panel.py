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
            # Блок для ядра K(x,t)
            html.Div([
                html.Div([
                    html.Label('Ядро K(x,t):', style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#2C3E50', 'marginBottom': '10px', 'display': 'block', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"}),
                    dcc.Textarea(
                        id='kernel-input',
                        placeholder='Введите выражение для ядра K(x,t) (используйте x и t как переменные)',
                        value='0.2 * exp(-(x - t))',
                        n_blur=0,
                        style={
                            'width': '100%',
                            'height': '60px',
                            'fontFamily': "'Roboto', monospace",
                            'fontSize': '13px',
                            'padding': '8px',
                            'borderRadius': '5px',
                            'border': '2px solid #D1D9E6',
                            'backgroundColor': '#FFFFFF',
                            'color': '#2C3E50',
                            'transition': 'border-color 0.3s ease'
                        }
                    ),
                    html.Div(id='kernel-validation', style={'color': '#E74C3C', 'fontSize': '0.85em', 'marginTop': '5px'}),
                ], style={'marginBottom': '15px'}),
                
                # Заголовок для выпадающего списка примеров ядер
                html.Div([
                    html.Div('▼ Примеры ядер K(x,t):', 
                            style={
                                'fontWeight': 'bold', 
                                'marginBottom': '5px', 
                                'color': '#2C3E50',
                                'cursor': 'pointer',
                                'userSelect': 'none',
                                'padding': '5px 10px',
                                'backgroundColor': '#E8ECF1',
                                'borderRadius': '6px',
                                'transition': 'all 0.3s ease',
                                'fontSize': '0.9em',
                                'fontFamily': "'Roboto', 'Segoe UI', sans-serif"
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
                                        'width': '51%',
                                        'textAlign': 'left',
                                        'margin': '3px 0',
                                        'padding': '5px 10px',
                                        'fontSize': '11px',
                                        'background': 'linear-gradient(135deg, #2C3E50 0%, #34495E 50%, #9DABB8 100%)',
                                        'color': '#FFFFFF',
                                        'border': 'none',
                                        'borderRadius': '15px',
                                        'cursor': 'pointer',
                                        'transition': 'all 0.3s ease',
                                        'fontFamily': "'Roboto', 'Segoe UI', sans-serif",
                                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                )
                                for i, name in enumerate(KERNEL_EXAMPLES.keys())
                            ])
                        ]
                    )
                ], style={'padding': '8px 12px', 'backgroundColor': '#FFFFFF', 
                         'borderRadius': '8px', 'border': '1px solid #D1D9E6'})
            ], style={
                'width': '48%', 
                'display': 'inline-flex',
                'flexDirection': 'column',
                'marginRight': '2%', 
                'verticalAlign': 'top',
                'padding': '15px',
                'border': '2px solid #D1D9E6',
                'borderRadius': '12px',
                'backgroundColor': '#FFFFFF',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'minHeight': 'auto'
            }),
            
            # Блок для правой части f(x)
            html.Div([
                html.Div([
                    html.Label('Правая часть f(x):', style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#2C3E50', 'marginBottom': '10px', 'display': 'block', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"}),
                    dcc.Textarea(
                        id='rhs-input',
                        placeholder='Введите выражение для правой части f(x) (используйте x как переменную)',
                        value='sin(x)',
                        n_blur=0,
                        style={
                            'width': '100%',
                            'height': '60px',
                            'fontFamily': "'Roboto', monospace",
                            'fontSize': '13px',
                            'padding': '8px',
                            'borderRadius': '5px',
                            'border': '2px solid #D1D9E6',
                            'backgroundColor': '#FFFFFF',
                            'color': '#2C3E50',
                            'transition': 'border-color 0.3s ease'
                        }
                    ),
                    html.Div(id='rhs-validation', style={'color': '#E74C3C', 'fontSize': '0.85em', 'marginTop': '5px'}),
                ], style={'marginBottom': '15px'}),
                
                # Заголовок для выпадающего списка примеров правых частей
                html.Div([
                    html.Div('▼ Примеры правых частей f(x):', 
                            style={
                                'fontWeight': 'bold', 
                                'marginBottom': '5px', 
                                'color': '#2C3E50',
                                'cursor': 'pointer',
                                'userSelect': 'none',
                                'padding': '5px 10px',
                                'backgroundColor': '#E8ECF1',
                                'borderRadius': '6px',
                                'transition': 'all 0.3s ease',
                                'fontSize': '0.9em',
                                'fontFamily': "'Roboto', 'Segoe UI', sans-serif"
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
                                        'width': '51%',
                                        'textAlign': 'left',
                                        'margin': '3px 0',
                                        'padding': '5px 10px',
                                        'fontSize': '11px',
                                        'background': 'linear-gradient(135deg, #2C3E50 0%, #34495E 50%, #9DABB8 100%)',
                                        'color': '#FFFFFF',
                                        'border': 'none',
                                        'borderRadius': '15px',
                                        'cursor': 'pointer',
                                        'transition': 'all 0.3s ease',
                                        'fontFamily': "'Roboto', 'Segoe UI', sans-serif",
                                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                )
                                for i, name in enumerate(RHS_EXAMPLES.keys())
                            ])
                        ]
                    )
                ], style={'padding': '8px 12px', 'backgroundColor': '#FFFFFF',
                         'borderRadius': '8px', 'border': '1px solid #D1D9E6'})
            ], style={
                'width': '48%', 
                'display': 'inline-flex',
                'flexDirection': 'column',
                'verticalAlign': 'top',
                'padding': '15px',
                'border': '2px solid #D1D9E6',
                'borderRadius': '12px',
                'backgroundColor': '#FFFFFF',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'minHeight': 'auto'
            }),
        ], style={'padding': '15px', 'display': 'flex', 'justifyContent': 'space-between'}),
        
        # Начальное условие
        html.Div([
            html.Label('Начальное условие φ(0):', style={'fontWeight': 'bold', 'color': '#2C3E50', 'marginBottom': '8px', 'display': 'block', 'textAlign': 'left', 'fontSize': '0.95em', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"}),
            dcc.Input(
                id='initial-condition',
                type='number',
                value=0.0,
                step=0.1,
                style={
                    'width': '120px',
                    'padding': '6px',
                    'borderRadius': '5px',
                    'border': '2px solid #D1D9E6',
                    'backgroundColor': '#FFFFFF',
                    'color': '#2C3E50',
                    'fontSize': '14px',
                    'textAlign': 'center',
                    'display': 'block',
                    'fontFamily': "'Roboto', monospace"
                }
            ),
        ], style={'padding': '15px', 'textAlign': 'left', 'width': '60%', 'margin': '0 auto'}),
        
        # Красивое отображение уравнения
        html.Div([
            html.Div(id='equation-display', 
                     style={'padding': '10px', 'backgroundColor': '#FFFFFF', 
                            'borderRadius': '8px', 'fontFamily': "'Roboto', monospace", 
                            'fontSize': '1em', 'textAlign': 'center',
                            'color': '#2C3E50', 'border': '2px solid #D1D9E6',
                            'width': '60%', 'margin': '0 auto'}),
        ], style={'padding': '15px', 'marginTop': '5px'}),
        
        # Легенда функций
        html.Div([
            html.Div([
                html.H5('▼ Поддерживаемые функции и константы:', 
                        style={'color': '#2C3E50', 'marginBottom': '8px', 'cursor': 'pointer', 'fontSize': '0.95em', 'fontFamily': "'Roboto', 'Segoe UI', sans-serif"},
                        id='legend-toggle'),
                html.Div([
                    html.Div([
                        html.P('✓ Ввод распознает синонимы функций, как asin, arsin, arcsin', 
                               style={'margin': '0 0 10px 0', 'color': '#7F8C8D', 'fontSize': '0.8em', 'fontStyle': 'italic', 'fontFamily': "'Roboto', sans-serif"}),
                    ]),
                    
                    html.Div([
                        html.Div([
                            html.H6('Тригонометрические и обратные:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em', 'fontFamily': "'Roboto', sans-serif"}),
                            html.P('sin, cos, tan, tg, cot, ctg, sec, csc, cosec', 
                                   style={'margin': '0 0 8px 0', 'color': '#2C3E50', 'fontSize': '0.8em', 'fontFamily': "'Roboto', monospace"}),
                            html.P('arcsin, arccos, arctan, arctg, arccot, arcsec, arccsc', 
                                   style={'margin': '0 0 8px 0', 'color': '#2C3E50', 'fontSize': '0.8em', 'fontFamily': "'Roboto', monospace"}),
                            
                            html.H6('Гиперболические и обратные:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em', 'fontFamily': "'Roboto', sans-serif"}),
                            html.P('sinh, sh, cosh, ch, tanh, th, coth, cth, sech, csch', 
                                   style={'margin': '0 0 8px 0', 'color': '#2C3E50', 'fontSize': '0.8em', 'fontFamily': "'Roboto', monospace"}),
                            html.P('arsinh, arcosh, artanh, arcoth, arsech, arcsch', 
                                   style={'margin': '0 0 8px 0', 'color': '#2C3E50', 'fontSize': '0.8em', 'fontFamily': "'Roboto', monospace"}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.H6('Логарифмы:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em', 'fontFamily': "'Roboto', sans-serif"}),
                            html.P('ln, lg, log, log2, log10, log(a, x)', 
                                   style={'margin': '0 0 8px 0', 'color': '#2C3E50', 'fontSize': '0.8em', 'fontFamily': "'Roboto', monospace"}),
                            
                            html.H6('Степени и корни:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em', 'fontFamily': "'Roboto', sans-serif"}),
                            html.P('x^2, x**2, sqrt, sqrt(n, x)', 
                                   style={'margin': '0 0 8px 0', 'color': '#2C3E50', 'fontSize': '0.8em', 'fontFamily': "'Roboto', monospace"}),
                            
                            html.H6('Модуль и экспонента:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em', 'fontFamily': "'Roboto', sans-serif"}),
                            html.P('abs(x), exp(x), e^x', 
                                   style={'margin': '0 0 8px 0', 'color': '#2C3E50', 'fontSize': '0.8em', 'fontFamily': "'Roboto', monospace"}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            html.H6('Константы:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em', 'fontFamily': "'Roboto', sans-serif"}),
                            html.P('pi, π, e', 
                                   style={'margin': '0 0 8px 0', 'color': '#2C3E50', 'fontSize': '0.8em', 'fontFamily': "'Roboto', monospace"}),
                            
                            html.H6('Греческие буквы:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em', 'fontFamily': "'Roboto', sans-serif"}),
                            html.P('alpha, beta, gamma, delta, epsilon, zeta, eta, theta', 
                                   style={'margin': '0 0 3px 0', 'color': '#2C3E50', 'fontSize': '0.75em', 'fontFamily': "'Roboto', monospace"}),
                            html.P('iota, kappa, lambda, mu, nu, xi, pi, rho', 
                                   style={'margin': '0 0 3px 0', 'color': '#2C3E50', 'fontSize': '0.75em', 'fontFamily': "'Roboto', monospace"}),
                            html.P('sigma, tau, upsilon, phi, chi, psi, omega', 
                                   style={'margin': '0 0 8px 0', 'color': '#2C3E50', 'fontSize': '0.75em', 'fontFamily': "'Roboto', monospace"}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ]),
                    
                ], id='legend-content', style={'display': 'none', 'marginTop': '8px'}),
            ], style={'padding': '10px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'marginTop': '15px', 'border': '1px solid #D1D9E6'}),
        ]),
        
        html.Div([
            html.Button('Решить уравнение', id='solve-button',  disabled=True,
                       style={
                           'background': 'linear-gradient(135deg, #2C3E50 0%, #34495E 50%, #2C3E50 100%)',
                           'color': '#FFFFFF',
                           'padding': '8px 16px',
                           'fontSize': '14px',
                           'border': 'none',
                           'borderRadius': '5px',
                           'cursor': 'pointer',
                           'margin': '10px auto',
                           'display': 'block',
                           'width': '180px',
                           'fontFamily': "'Roboto', 'Segoe UI', sans-serif",
                           'transition': 'all 0.3s ease',
                           'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                       }),
            
            html.Div([
                html.Div(id='loading-indicator', children=[
                    html.Div(style={
                        'border': '4px solid #D1D9E6',
                        'borderTop': '4px solid #2C3E50',
                        'borderRadius': '50%',
                        'width': '30px',
                        'height': '30px',
                        'animation': 'spin 1s linear infinite',
                        'margin': '0 auto'
                    }),
                    html.P('Вычисление... Пожалуйста, подождите', 
                           style={'textAlign': 'center', 'marginTop': '10px', 'color': '#7F8C8D', 'fontSize': '0.9em', 'fontFamily': "'Roboto', sans-serif"})
                ], style={'display': 'none', 'marginTop': '20px'})
            ], style={'textAlign': 'center'})
        ]),
    ])