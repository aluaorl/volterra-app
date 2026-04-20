from dash import dcc, html

def create_result_panels():
    """Создает панели для отображения результатов"""
    return html.Div([
        html.Div(id='status-message', className='status-message'),
        html.Div(id='error-message', className='error-message', style={'display': 'none'}),
        
        # Графики
        html.Div([
            html.Div([
                html.H3('График решения φ(x)', className='text-center'),
                dcc.Graph(id='volterra-graph', config={'responsive': True}),
            ], className='graph-card', style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
            
            html.Div([
                html.H3('Производная φ\'(x)', className='text-center'),
                dcc.Graph(id='derivative-plot', config={'responsive': True}),
            ], className='graph-card', style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.Div([
                html.H3('Сечения ядра K(x,t)', className='text-center'),
                dcc.Graph(id='kernel-sections-plot', config={'responsive': True}),
            ], className='graph-card', style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
            
            html.Div([
                html.H3('3D поверхность ядра', className='text-center'),
                dcc.Graph(id='kernel-3d-plot', config={'responsive': True}),
            ], className='graph-card', style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ]),
        
        html.Div(id='error-output', className='error-text', style={'display': 'none'}),
        dcc.Store(id='computation-time', data=0),
    ])