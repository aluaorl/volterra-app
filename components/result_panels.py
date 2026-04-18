from dash import dcc, html

def create_result_panels():
    """Создает панели для отображения результатов с дополнительными графиками"""
    return html.Div([
        # Сообщение о статусе вычислений
        html.Div(id='status-message', style={'textAlign': 'center', 'margin': '10px'}),
        
        # Сообщение об ошибке
        html.Div(id='error-message', style={'textAlign': 'center', 'color': 'red', 'fontSize': '1.1em', 'margin': '10px'}),
        
        # Панель с численными результатами
        html.Div([
            html.H3('📊 Численные результаты', style={'color': '#2c3e50', 'marginBottom': '15px'}),
            html.Div(id='numerical-results', style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                'gap': '15px',
                'marginBottom': '20px'
            }),
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '10px'}),
        
        # Основной график решения
        html.Div([
            html.H3('📈 График решения', style={'color': '#2c3e50'}),
            dcc.Graph(id='volterra-graph'),
        ], style={'padding': '10px'}),
        
        # График ошибки
        html.Div([
            html.H3('📉 Анализ ошибки', style={'color': '#2c3e50'}),
            dcc.Graph(id='error-plot'),
        ], style={'padding': '10px', 'marginTop': '20px'}),
        
        # Информация об ошибке (важный компонент!)
        html.Div(id='error-output', style={'textAlign': 'center', 'fontSize': '1.2em', 'marginTop': '20px'}),
        
        # Новая секция: Анализ ядра
        html.Div([
            html.H3('🎯 Анализ ядра K(x,t)', style={'color': '#2c3e50', 'marginBottom': '20px'}),
            
            # Сечения ядра при фиксированных t
            html.Div([
                html.H4('📐 Сечения ядра K(x,t) при фиксированных t', style={'color': '#34495e'}),
                dcc.Graph(id='kernel-sections-plot'),
            ], style={'marginBottom': '30px'}),
            
            # 3D поверхность ядра и контурный график в два столбца
            html.Div([
                html.Div([
                    html.H4('🎨 3D поверхность ядра', style={'color': '#34495e'}),
                    dcc.Graph(id='kernel-3d-plot'),
                ], style={'width': '49%', 'display': 'inline-block'}),
                
                html.Div([
                    html.H4('🗺️ Контурный график ядра', style={'color': '#34495e'}),
                    dcc.Graph(id='kernel-contour-plot'),
                ], style={'width': '49%', 'display': 'inline-block', 'float': 'right'}),
            ], style={'marginBottom': '30px'}),
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '10px'}),
        
        # Новая секция: Анализ правой части и сравнение с решением
        html.Div([
            html.H3('📊 Анализ правой части f(x) и сравнение с решением', style={'color': '#2c3e50', 'marginBottom': '20px'}),
            
            # Сравнение f(x) и решения
            html.Div([
                html.H4('📈 Сравнение f(x) и φ(x)', style={'color': '#34495e'}),
                dcc.Graph(id='f-vs-phi-plot'),
            ], style={'marginBottom': '30px'}),
            
            # Вклад интегрального члена
            html.Div([
                html.H4('⚖️ Вклад интегрального члена vs свободный член', style={'color': '#34495e'}),
                dcc.Graph(id='integral-contribution-plot'),
            ], style={'marginBottom': '30px'}),
            
            # Разность f(x) и φ(x)
            html.Div([
                html.H4('📉 Разность φ(x) - f(x) (вклад интеграла)', style={'color': '#34495e'}),
                dcc.Graph(id='difference-plot'),
            ], style={'marginBottom': '30px'}),
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '10px'}),
        
        # Хранилище для времени вычислений
        dcc.Store(id='computation-time', data=0),
    ])