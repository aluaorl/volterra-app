from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import numpy as np
import time
import json
import uuid
from dash import html
import sys
import os
from functools import lru_cache
from dash.dependencies import ALL

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculation_engine import solve_volterra_RK4, get_reference_solution, create_function_from_string
from expression_parser import parse_user_input, format_for_display, validate_expression_detailed
from .input_panel import KERNEL_EXAMPLES, RHS_EXAMPLES

def _pattern_button_index(ctx):
    tid = getattr(ctx, 'triggered_id', None)
    if isinstance(tid, dict) and 'index' in tid:
        return tid['index']
    if not ctx.triggered:
        return None
    raw = ctx.triggered[0]['prop_id'].rsplit('.', 1)[0]
    try:
        return json.loads(raw.replace("'", '"')).get('index')
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
        return None

def run_volterra_solution(kernel_expr, rhs_expr, N_points):
    start_time = time.time()
    
    if not kernel_expr or not kernel_expr.strip():
        raise ValueError("Выражение для ядра K(x,t) не может быть пустым")
    if not rhs_expr or not rhs_expr.strip():
        raise ValueError("Выражение для правой части f(x) не может быть пустым")
    
    parsed_kernel = parse_user_input(kernel_expr, ['x', 't'])
    parsed_rhs = parse_user_input(rhs_expr, ['x'])
    K_current, f_current = get_cached_functions(parsed_kernel, parsed_rhs)
    
    try:
        test_K = K_current(0.5, 0.5)
        test_f = f_current(0.5)
    except Exception as e:
        raise ValueError(f"{str(e)}")

    a = 0
    b = 1
    h = (b - a) / N_points
    x = np.linspace(a, b, N_points + 1)

    phi_numerical = solve_volterra_RK4(x, h, K_current, f_current)
    phi_reference = get_reference_solution(x, K_current, f_current)
    f_values = np.array([f_current(xi) for xi in x])

    fig_solution = go.Figure()
    fig_solution.add_trace(go.Scatter(x=x, y=phi_reference, mode='lines', name='Эталон',
                                      line=dict(color='#e74c3c', width=2)))
    fig_solution.add_trace(go.Scatter(x=x, y=phi_numerical, mode='lines', name='Численное (RK4)',
                                      line=dict(color='#2980b9', dash='dash', width=1.5)))
    fig_solution.update_layout(
        title='Решение уравнения Вольтерры',
        xaxis_title='x', yaxis_title='φ(x)', hovermode='x unified',
        template='plotly_white', height=500)

    error = np.abs(phi_numerical - phi_reference)
    max_error = np.max(error)
    error_text = f'Максимальная ошибка: {max_error:.2e}'

    fig_error = go.Figure()
    fig_error.add_trace(go.Scatter(x=x, y=error, mode='lines', name='Абсолютная ошибка',
                                   line=dict(color='#27ae60', width=2)))
    fig_error.add_trace(go.Scatter(x=x, y=[max_error] * len(x), mode='lines',
                                   name='Максимальная ошибка',
                                   line=dict(color='#e74c3c', dash='dash', width=1)))
    yaxis_type = 'log' if np.all(error > 0) else 'linear'
    fig_error.update_layout(
        title='Абсолютная ошибка |φ_числ - φ_эталон|',
        xaxis_title='x', yaxis_title='Ошибка', yaxis_type=yaxis_type,
        hovermode='x unified', template='plotly_white', height=400)

    t_values = [0, 0.25, 0.5, 0.75, 1.0]
    colors = ['#2980b9', '#27ae60', '#e74c3c', '#f39c12', '#8e44ad']
    fig_kernel_sections = go.Figure()
    for t_val, color in zip(t_values, colors):
        K_section = [K_current(xi, t_val) for xi in x]
        fig_kernel_sections.add_trace(go.Scatter(
            x=x, y=K_section, mode='lines', name=f't = {t_val}', line=dict(color=color, width=2)))
    fig_kernel_sections.update_layout(
        title='Сечения ядра K(x,t) при фиксированных t',
        xaxis_title='x', yaxis_title='K(x,t)', hovermode='x unified',
        template='plotly_white', height=400)

    n_points_3d = min(50, len(x))
    X, T = np.meshgrid(x[:n_points_3d], x[:n_points_3d])
    K_3d = np.zeros_like(X)
    for i in range(len(X)):
        for j in range(len(T)):
            K_3d[i, j] = K_current(X[i, j], T[i, j])
    fig_kernel_3d = go.Figure(data=[go.Surface(z=K_3d, x=X, y=T, colorscale='Blues')])
    fig_kernel_3d.update_layout(
        title='3D поверхность ядра K(x,t)',
        scene=dict(xaxis_title='x', yaxis_title='t', zaxis_title='K(x,t)'),
        height=500)

    fig_diff = go.Figure()
    diff = phi_numerical - f_values
    fig_diff.add_trace(go.Scatter(x=x, y=diff, mode='lines', name='φ(x) - f(x)',
                                  line=dict(color='#e74c3c', width=2), fill='tozeroy'))
    fig_diff.add_trace(go.Scatter(x=x, y=diff, mode='lines', name='Интегральный член',
                                  line=dict(color='#2980b9', width=2, dash='dash')))
    fig_diff.update_layout(
        title='Разность φ(x) - f(x) (вклад интеграла)',
        xaxis_title='x', yaxis_title='Значение', hovermode='x unified',
        template='plotly_white', height=400)

    computation_time = time.time() - start_time
    return (
        fig_solution,
        error_text,
        fig_error,
        fig_kernel_sections,
        fig_kernel_3d,
        fig_diff,
        computation_time,
    )

def create_empty_figure(title="Ожидание ввода"):
    """Создает пустой график без ошибок"""
    fig = go.Figure()
    fig.update_layout(
        title=title,
        xaxis_title='x',
        yaxis_title='y',
        template='plotly_white',
        height=400,
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[-1, 1])
    )
    return fig

@lru_cache(maxsize=128)
def get_cached_functions(kernel_expr, rhs_expr):
    K_current = create_function_from_string(kernel_expr, ['x', 't'])
    f_current = create_function_from_string(rhs_expr, ['x'])
    return K_current, f_current

def format_equation_beautifully(kernel_expr, rhs_expr):
    if not kernel_expr or not rhs_expr:
        return html.Div([
            html.Div("Введите выражения для ядра K(x,t) и правой части f(x)", 
                    style={'color': '#666', 'fontStyle': 'italic', 'textAlign': 'center'})
        ])
    
    try:
        parsed_kernel = parse_user_input(kernel_expr, ['x', 't'])
        parsed_rhs = parse_user_input(rhs_expr, ['x'])
        
        kernel_display = format_for_display(parsed_kernel, is_kernel=True)
        rhs_display = format_for_display(parsed_rhs, is_kernel=False)
        
        kernel_display = kernel_display.replace('K(x,t) = ', '')
        rhs_display = rhs_display.replace('f(x) = ', '')
        
        kernel_display = kernel_display.replace('exp', 'e')
        rhs_display = rhs_display.replace('exp', 'e')
        
        import re
        kernel_display = re.sub(r'e\^\{([^}]+)\}', r'e^{\1}', kernel_display)
        rhs_display = re.sub(r'e\^\{([^}]+)\}', r'e^{\1}', rhs_display)
        
        return html.Div([
            html.Div([
                html.Span("φ(x) = ", style={'fontWeight': 'bold', 'fontSize': '1.2em', 'color': '#1a5276'}),
                html.Span(rhs_display, style={'color': '#27ae60', 'fontWeight': 'bold', 'fontSize': '1.2em'}),
                html.Span(" + ", style={'fontWeight': 'bold', 'fontSize': '1.2em', 'color': '#1a5276'}),
                html.Span("∫₀ˣ ", style={'fontSize': '1.2em', 'color': '#1a5276'}),
                html.Span(kernel_display, style={'color': '#2980b9', 'fontWeight': 'bold', 'fontSize': '1.2em'}),
                html.Span(" · φ(t) dt", style={'fontSize': '1.2em', 'color': '#1a5276'}),
            ], style={'marginBottom': '15px', 'fontFamily': 'monospace', 'textAlign': 'center'}),
        ])
    except Exception as e:
        return html.Div([
            html.Div([
                html.Span("φ(x) = ", style={'fontWeight': 'bold', 'fontSize': '1.1em', 'color': '#1a5276'}),
                html.Span(rhs_expr, style={'color': '#27ae60', 'fontFamily': 'monospace'}),
                html.Span(" + ∫₀ˣ ", style={'fontSize': '1.1em', 'color': '#1a5276'}),
                html.Span(kernel_expr, style={'color': '#2980b9', 'fontFamily': 'monospace'}),
                html.Span(" · φ(t) dt", style={'fontSize': '1.1em', 'color': '#1a5276'}),
            ], style={'marginBottom': '10px', 'textAlign': 'center'}),
        ])
    
def register_callbacks(app):
    
    @app.callback(
        Output('n-input', 'value'),
        Input('n-input', 'value'),
        prevent_initial_call=True
    )
    def validate_n_points(value):
        if value is None or value == '':
            return 200
        try:
            val = int(value)
            if val < 50:
                val = 50
            elif val > 500:
                val = 500
            val = ((val + 25) // 50) * 50
            val = max(50, min(500, val))
            return val
        except (ValueError, TypeError):
            return 200
    
    @app.callback(
        [Output('kernel-input', 'value'),
         Output('rhs-input', 'value')],
        [Input({'type': 'kernel-example', 'index': ALL}, 'n_clicks'),
         Input({'type': 'rhs-example', 'index': ALL}, 'n_clicks')],
        prevent_initial_call=True
    )
    def fill_example(kernel_clicks, rhs_clicks):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        triggered_dict = json.loads(triggered_id.replace("'", '"'))
        
        if triggered_dict['type'] == 'kernel-example':
            example_name = list(KERNEL_EXAMPLES.keys())[triggered_dict['index']]
            return KERNEL_EXAMPLES[example_name], no_update
        else:
            example_name = list(RHS_EXAMPLES.keys())[triggered_dict['index']]
            return no_update, RHS_EXAMPLES[example_name]
    
    @app.callback(
        Output('legend-content', 'style'),
        Input('legend-toggle', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_legend(n_clicks):
        if n_clicks is None:
            return {'display': 'none', 'marginTop': '10px'}
        return {'display': 'block', 'marginTop': '10px', 'animation': 'fadeIn 0.3s ease-in'}
    
    @app.callback(
        Output('equation-display', 'children'),
        [Input('kernel-input', 'value'),
         Input('rhs-input', 'value')]
    )
    def update_equation_display(kernel_expr, rhs_expr):
        if not kernel_expr or not rhs_expr:
            return html.Div([
                html.Div("Введите выражения для ядра K(x,t) и правой части f(x)", 
                        style={'color': '#666', 'fontStyle': 'italic', 'textAlign': 'center'})
            ])
        return format_equation_beautifully(kernel_expr, rhs_expr)
    
        # Единый callback валидации - показывает ошибку только в error-message
    @app.callback(
        [Output('solve-button', 'disabled'),
         Output('solve-button', 'title'),
         Output('error-message', 'children'),
         Output('error-message', 'style'),
         Output('volterra-graph', 'figure'),
         Output('error-plot', 'figure'),
         Output('kernel-sections-plot', 'figure'),
         Output('kernel-3d-plot', 'figure'),
         Output('difference-plot', 'figure'),
         Output('error-output', 'children')],
        [Input('kernel-input', 'value'),
         Input('rhs-input', 'value')],
        prevent_initial_call=False
    )
    def validate_inputs(kernel_expr, rhs_expr):
        """Единая валидация - ошибка только в error-message"""
        
        # Значения по умолчанию
        kernel_valid = True
        rhs_valid = True
        kernel_error = ""
        rhs_error = ""
        error_text = ""
        
        # Проверка ядра (только если есть значение)
        if kernel_expr and kernel_expr.strip():
            valid, msg = validate_expression_detailed(kernel_expr, ['x', 't'])
            if not valid:
                kernel_valid = False
                kernel_error = msg
        elif not kernel_expr or not kernel_expr.strip():
            kernel_valid = False
            kernel_error = "поле ядра пусто"
        
        # Проверка правой части (только если есть значение)
        if rhs_expr and rhs_expr.strip():
            valid, msg = validate_expression_detailed(rhs_expr, ['x'])
            if not valid:
                rhs_valid = False
                rhs_error = msg
        elif not rhs_expr or not rhs_expr.strip():
            rhs_valid = False
            rhs_error = "поле правой части пусто"
        
        # Формируем единое понятное сообщение об ошибке
        if not kernel_valid and not rhs_valid:
            error_text = f"Ошибки: в ядре - {kernel_error}, в правой части - {rhs_error}"
        elif not kernel_valid:
            error_text = f"Ошибка в ядре K(x,t): {kernel_error}"
        elif not rhs_valid:
            error_text = f"Ошибка в правой части f(x): {rhs_error}"
        
        button_disabled = not (kernel_valid and rhs_valid)
        
        if button_disabled:
            button_title = "Исправьте ошибки в выражениях"
        else:
            button_title = "Решить уравнение"
        
        if error_text:
            error_style = {
                'textAlign': 'center', 
                'color': '#c0392b', 
                'fontSize': '0.95em', 
                'margin': '15px auto',
                'padding': '12px',
                'backgroundColor': '#fce4ec',
                'borderRadius': '8px',
                'borderLeft': '4px solid #c0392b',
                'maxWidth': '80%'
            }
            empty_fig = create_empty_figure("Некорректное выражение")
            return (button_disabled, button_title, error_text, error_style,
                    empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "")
        else:
            waiting_fig = create_empty_figure("Введите выражения и нажмите 'Решить'")
            return (button_disabled, button_title, "", {"display": "none"},
                    waiting_fig, waiting_fig, waiting_fig, waiting_fig, waiting_fig, "")
    # Callback для решения уравнения
    @app.callback(
        [Output('volterra-graph', 'figure', allow_duplicate=True),
         Output('error-output', 'children', allow_duplicate=True),
         Output('error-plot', 'figure', allow_duplicate=True),
         Output('kernel-sections-plot', 'figure', allow_duplicate=True),
         Output('kernel-3d-plot', 'figure', allow_duplicate=True),
         Output('difference-plot', 'figure', allow_duplicate=True),
         Output('loading-indicator', 'style'),
         Output('status-message', 'children'),
         Output('status-message', 'style'),
         Output('computation-time', 'data'),
         Output('solutions-history', 'data')],
        [Input('solve-button', 'n_clicks')],
        [State('kernel-input', 'value'),
         State('rhs-input', 'value'),
         State('n-input', 'value'),
         State('solutions-history', 'data')],
        prevent_initial_call=True
    )
    def update_graph(n_clicks, kernel_expr, rhs_expr, N_points, history_data):
        if n_clicks is None:
            raise PreventUpdate
        
        if not kernel_expr or not kernel_expr.strip():
            raise PreventUpdate
        
        if not rhs_expr or not rhs_expr.strip():
            raise PreventUpdate
        
        kernel_valid, _ = validate_expression_detailed(kernel_expr, ['x', 't'])
        if not kernel_valid:
            raise PreventUpdate
        
        rhs_valid, _ = validate_expression_detailed(rhs_expr, ['x'])
        if not rhs_valid:
            raise PreventUpdate
        
        loading_style = {
            'display': 'block', 
            'marginTop': '20px',
            'padding': '15px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px'
        }
        
        status_msg = html.Div([
            html.Span("Вычисление... ", style={'fontWeight': 'bold'}),
            html.Span("Это может занять несколько секунд")
        ], style={'color': '#2980b9'})
        
        try:
            (fig_solution, error_text, fig_error, fig_kernel_sections, fig_kernel_3d, fig_diff,
             computation_time) = run_volterra_solution(kernel_expr, rhs_expr, N_points)
            
            success_status = html.Div([
                html.Span("Вычисление успешно завершено! ", style={'fontWeight': 'bold'}),
                html.Span(f"Время выполнения: {computation_time:.2f} секунд")
            ], style={'color': '#27ae60'})
            
            hist = []
            for r in (history_data if isinstance(history_data, list) else []):
                if not isinstance(r, dict):
                    continue
                slim = {
                    'id': r.get('id'),
                    'timestamp': r.get('timestamp', ''),
                    'date': r.get('date', ''),
                    'kernel': r.get('kernel'),
                    'rhs': r.get('rhs'),
                    'n_points': r.get('n_points'),
                    'computation_time': r.get('computation_time'),
                }
                if slim['id'] is None or slim['kernel'] is None or slim['rhs'] is None or slim['n_points'] is None:
                    continue
                hist.append(slim)
            solution_record = {
                'id': str(uuid.uuid4()),
                'timestamp': time.strftime("%H:%M:%S"),
                'date': time.strftime("%d.%m.%Y"),
                'kernel': kernel_expr,
                'rhs': rhs_expr,
                'n_points': N_points,
                'computation_time': computation_time,
            }
            new_history = [solution_record] + hist
            new_history = new_history[:20]
            
            return (fig_solution, error_text, fig_error, fig_kernel_sections, 
                    fig_kernel_3d, fig_diff,
                    {'display': 'none'}, success_status, {'textAlign': 'center', 'margin': '10px'}, 
                    computation_time, new_history)
            
        except Exception as e:
            error_msg = str(e)
            if "Ошибка при вычислении функции:" in error_msg:
                error_msg = error_msg.split("Ошибка при вычислении функции:")[-1].strip()
            elif "Ошибка при вычислении на шаге" in error_msg:
                parts = error_msg.split(":")
                if len(parts) > 1:
                    error_msg = parts[-1].strip()
            
            error_status = html.Div([
                html.Span("Ошибка! ", style={'fontWeight': 'bold'}),
                html.Div(error_msg, style={'fontSize': '0.9em', 'marginTop': '10px', 'color': '#c0392b'})
            ], style={'color': '#c0392b'})
            
            empty_fig = create_empty_figure("Ошибка вычислений")
            
            return (empty_fig, "Ошибка вычислений", empty_fig, empty_fig, empty_fig, empty_fig,
                    {'display': 'none'}, error_status, {'textAlign': 'center', 'margin': '10px'}, 
                    0, no_update)

    @app.callback(
        Output('history-list', 'children'),
        [Input('solutions-history', 'data'),
         Input('clear-history-btn', 'n_clicks')],
        prevent_initial_call=False
    )
    def update_history_list(history_data, clear_clicks):
        ctx = callback_context
        
        if clear_clicks and ctx.triggered and 'clear-history-btn' in ctx.triggered[0]['prop_id']:
            return html.Div("История пуста. Решите уравнение, чтобы оно появилось здесь.", 
                          style={'color': '#999', 'fontStyle': 'italic', 'textAlign': 'center', 'padding': '20px'})
        
        if not history_data or len(history_data) == 0:
            return html.Div("История пуста. Решите уравнение, чтобы оно появилось здесь.", 
                          style={'color': '#999', 'fontStyle': 'italic', 'textAlign': 'center', 'padding': '20px'})
        
        history_items = []
        for record in history_data:
            if not isinstance(record, dict) or 'id' not in record:
                continue
                
            kernel_preview = record['kernel'][:60] + '...' if len(record['kernel']) > 60 else record['kernel']
            rhs_preview = record['rhs'][:60] + '...' if len(record['rhs']) > 60 else record['rhs']
            
            history_item = html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Span(f"{record['timestamp']} | {record['date']}", 
                                             style={'fontWeight': 'bold', 'color': '#1a5276', 'fontSize': '0.9em'}),
                                    html.Span(f" | N={record['n_points']}", 
                                             style={'color': '#666', 'fontSize': '0.85em', 'marginLeft': '10px'}),
                                ]
                            ),
                            html.Div(
                                children=[
                                    html.Small(f"K(x,t) = {kernel_preview}", 
                                             style={'color': '#2980b9', 'fontFamily': 'monospace'}),
                                    html.Br(),
                                    html.Small(f"f(x) = {rhs_preview}", 
                                             style={'color': '#27ae60', 'fontFamily': 'monospace'}),
                                ], 
                                style={'marginLeft': '15px', 'marginTop': '5px', 'marginBottom': '5px'}
                            ),
                            html.Div(
                                children=[
                                    html.Button("Загрузить", 
                                               id={'type': 'load-solution', 'index': record['id']},
                                               style={'padding': '4px 12px', 'marginRight': '8px',
                                                      'backgroundColor': '#3498db', 'color': 'white',
                                                      'border': 'none', 'borderRadius': '3px',
                                                      'cursor': 'pointer', 'fontSize': '12px'}),
                                    html.Button("Удалить", 
                                               id={'type': 'delete-solution', 'index': record['id']},
                                               style={'padding': '4px 12px',
                                                      'backgroundColor': '#e74c3c', 'color': 'white',
                                                      'border': 'none', 'borderRadius': '3px',
                                                      'cursor': 'pointer', 'fontSize': '12px'}),
                                ], 
                                style={'marginTop': '8px', 'textAlign': 'right'}
                            )
                        ], 
                        style={'padding': '10px', 'borderBottom': '1px solid #ddd',
                               'marginBottom': '5px', 'borderRadius': '5px',
                               'backgroundColor': 'white'}
                    )
                ],
                id=f'history-item-{record["id"]}'
            )
            history_items.append(history_item)
        
        return history_items
    
    @app.callback(
        [Output('kernel-input', 'value', allow_duplicate=True),
         Output('rhs-input', 'value', allow_duplicate=True),
         Output('n-input', 'value', allow_duplicate=True),
         Output('volterra-graph', 'figure', allow_duplicate=True),
         Output('error-plot', 'figure', allow_duplicate=True),
         Output('kernel-sections-plot', 'figure', allow_duplicate=True),
         Output('kernel-3d-plot', 'figure', allow_duplicate=True),
         Output('difference-plot', 'figure', allow_duplicate=True),
         Output('error-output', 'children', allow_duplicate=True),
         Output('status-message', 'children', allow_duplicate=True),
         Output('status-message', 'style', allow_duplicate=True)],
        [Input({'type': 'load-solution', 'index': ALL}, 'n_clicks')],
        [State('solutions-history', 'data')],
        prevent_initial_call='initial_duplicate'
    )
    def load_solution(load_clicks, history_data):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if ctx.triggered[0].get('value') is None:
            raise PreventUpdate
        if not history_data:
            raise PreventUpdate
        solution_id = _pattern_button_index(ctx)
        if solution_id is None:
            raise PreventUpdate
        
        for record in history_data:
            if str(record.get('id')) != str(solution_id):
                continue
            if not all(k in record for k in ('kernel', 'rhs', 'n_points')):
                continue
            try:
                (fig_solution, err_text, fig_error, fig_sec, fig_3d, fig_diff, _t) = run_volterra_solution(
                    record['kernel'], record['rhs'], record['n_points']
                )
            except Exception as e:
                error_msg = str(e)
                if "Ошибка при вычислении функции:" in error_msg:
                    error_msg = error_msg.split("Ошибка при вычислении функции:")[-1].strip()
                elif "Ошибка при вычислении на шаге" in error_msg:
                    parts = error_msg.split(":")
                    if len(parts) > 1:
                        error_msg = parts[-1].strip()
                
                status_msg = html.Div([
                    html.Span("Ошибка! ", style={'fontWeight': 'bold'}),
                    html.Div(error_msg, style={'fontSize': '0.9em', 'marginTop': '10px', 'color': '#c0392b'})
                ], style={'color': '#c0392b', 'textAlign': 'center', 'padding': '10px'})
                empty_fig = create_empty_figure("Ошибка вычислений")
                return (
                    no_update, no_update, no_update,
                    empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
                    no_update,
                    status_msg,
                    {'textAlign': 'center', 'margin': '10px'},
                )
            status_msg = html.Div([
                html.Span("Загружено из истории! ", style={'fontWeight': 'bold'}),
                html.Span(f"Решение от {record.get('timestamp', '')} {record.get('date', '')}")
            ], style={'color': '#27ae60', 'textAlign': 'center', 'padding': '10px'})
            return (record['kernel'], record['rhs'], record['n_points'],
                    fig_solution, fig_error, fig_sec, fig_3d, fig_diff, err_text,
                    status_msg, {'textAlign': 'center', 'margin': '10px'})
        
        raise PreventUpdate
    
    @app.callback(
        Output('solutions-history', 'data', allow_duplicate=True),
        [Input({'type': 'delete-solution', 'index': ALL}, 'n_clicks')],
        [State('solutions-history', 'data')],
        prevent_initial_call='initial_duplicate'
    )
    def delete_solution(delete_clicks, history_data):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if ctx.triggered[0].get('value') is None:
            raise PreventUpdate
        if not history_data:
            raise PreventUpdate
        solution_id = _pattern_button_index(ctx)
        if solution_id is None:
            raise PreventUpdate
        
        new_history = [
            record for record in history_data
            if str(record.get('id')) != str(solution_id)
        ]
        
        return new_history
    
    @app.callback(
        Output('solutions-history', 'data', allow_duplicate=True),
        [Input('clear-history-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def clear_all_history(clear_clicks):
        if clear_clicks:
            return []
        raise PreventUpdate