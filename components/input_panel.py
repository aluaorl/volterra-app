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
        dcc.Store(id='kernel-examples-state', data={'expanded': False}),
        dcc.Store(id='rhs-examples-state', data={'expanded': False}),
        
        # Блоки ввода в два столбца
        html.Div([
            # Левая колонка - ядро
            html.Div([
                html.Label('Ядро K(x,t):', style={'fontWeight': 'bold', 'fontSize': '1.1em'}),
                dcc.Textarea(
                    id='kernel-input',
                    placeholder='Введите выражение для ядра K(x,t) (используйте x и t как переменные)',
                    value='0.2 * exp(-(x - t))',
                    style={'width': '100%', 'height': '60px'}
                ),
                
                # Примеры ядер
                html.Div([
                    html.Div('▼ Примеры ядер K(x,t):', className='example-toggle', id='kernel-examples-toggle'),
                    html.Div(
                        id='kernel-examples-content',
                        style={'display': 'none', 'marginTop': '8px'},
                        children=[
                            html.Button(name, id={'type': 'kernel-example', 'index': i}, className='example-button')
                            for i, name in enumerate(KERNEL_EXAMPLES.keys())
                        ]
                    )
                ], style={'padding': '8px 12px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'border': '1px solid #D1D9E6', 'marginTop': '10px'})
            ], className='input-card', style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
            
            # Правая колонка - правая часть
            html.Div([
                html.Label('Правая часть f(x):', style={'fontWeight': 'bold', 'fontSize': '1.1em'}),
                dcc.Textarea(
                    id='rhs-input',
                    placeholder='Введите выражение для правой части f(x) (используйте x как переменную)',
                    value='sin(x)',
                    style={'width': '100%', 'height': '60px'}
                ),
                
                # Примеры правых частей
                html.Div([
                    html.Div('▼ Примеры правых частей f(x):', className='example-toggle', id='rhs-examples-toggle'),
                    html.Div(
                        id='rhs-examples-content',
                        style={'display': 'none', 'marginTop': '8px'},
                        children=[
                            html.Button(name, id={'type': 'rhs-example', 'index': i}, className='example-button')
                            for i, name in enumerate(RHS_EXAMPLES.keys())
                        ]
                    )
                ], style={'padding': '8px 12px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'border': '1px solid #D1D9E6', 'marginTop': '10px'})
            ], className='input-card', style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '15px'}),
        
        # Начальное условие
        html.Div([
            html.Label('Начальное условие φ(0):'),
            dcc.Input(
                id='initial-condition',
                type='number',
                value=0.0,
                step=0.1,
                style={'width': '120px', 'padding': '6px', 'textAlign': 'center'}
            ),
        ], style={'padding': '15px', 'textAlign': 'left', 'width': '60%', 'margin': '0 auto'}),
        
        # Отображение уравнения
        html.Div(id='equation-display', style={'marginTop': '5px'}),
        
        # Легенда функций
        html.Div([
            html.Div([
                html.H5('▼ Поддерживаемые функции и константы:', id='legend-toggle', style={'marginBottom': '8px'}),
                html.Div(id='legend-content', style={'display': 'none'}, children=[
                    html.P('✓ Ввод распознает синонимы функций, как asin, arsin, arcsin', 
                           style={'margin': '0 0 10px 0', 'color': '#7F8C8D', 'fontSize': '0.8em', 'fontStyle': 'italic'}),
                    html.Div([
                        html.Div([
                            html.H6('Тригонометрические и обратные:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                            html.P('sin, cos, tan, tg, cot, ctg, sec, csc, cosec', style={'margin': '0 0 8px 0', 'fontSize': '0.8em'}),
                            html.P('arcsin, arccos, arctan, arctg, arccot, arcsec, arccsc', style={'margin': '0 0 8px 0', 'fontSize': '0.8em'}),
                            html.H6('Гиперболические и обратные:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                            html.P('sinh, sh, cosh, ch, tanh, th, coth, cth, sech, csch', style={'margin': '0 0 8px 0', 'fontSize': '0.8em'}),
                            html.P('arsinh, arcosh, artanh, arcoth, arsech, arcsch', style={'margin': '0 0 8px 0', 'fontSize': '0.8em'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        html.Div([
                            html.H6('Логарифмы:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                            html.P('ln, lg, log, log2, log10, log(a, x)', style={'margin': '0 0 8px 0', 'fontSize': '0.8em'}),
                            html.H6('Степени и корни:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                            html.P('x^2, x**2, sqrt, sqrt(n, x)', style={'margin': '0 0 8px 0', 'fontSize': '0.8em'}),
                            html.H6('Модуль и экспонента:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                            html.P('abs(x), exp(x), e^x', style={'margin': '0 0 8px 0', 'fontSize': '0.8em'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        html.Div([
                            html.H6('Константы:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                            html.P('pi, π, e', style={'margin': '0 0 8px 0', 'fontSize': '0.8em'}),
                            html.H6('Греческие буквы:', style={'color': '#34495E', 'marginBottom': '3px', 'fontSize': '0.85em'}),
                            html.P('alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iota, kappa, lambda, mu, nu, xi, pi, rho, sigma, tau, upsilon, phi, chi, psi, omega', 
                                   style={'margin': '0 0 8px 0', 'fontSize': '0.75em'}),
                        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ]),
                ]),
            ], style={'padding': '10px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'marginTop': '15px', 'border': '1px solid #D1D9E6'})
        ]),
        
        # Кнопка решения
        html.Button('Решить уравнение', id='solve-button', disabled=True),
        
        # Индикатор загрузки
        html.Div([
            html.Div(className='loader'),
            html.P('Вычисление... Пожалуйста, подождите', style={'textAlign': 'center', 'marginTop': '10px', 'color': '#7F8C8D'})
        ], id='loading-indicator', style={'display': 'none', 'marginTop': '20px', 'textAlign': 'center'})
    ])