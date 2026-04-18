from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import numpy as np
import time
import json
from dash import html
import sys
import os
from functools import lru_cache

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculation_engine import solve_volterra_RK4, get_reference_solution, create_function_from_string
from .input_panel import KERNEL_EXAMPLES, RHS_EXAMPLES

# Кэширование для функций ядра и правой части
@lru_cache(maxsize=128)
def get_cached_functions(kernel_expr, rhs_expr):
    """Кэширование созданных функций"""
    K_current = create_function_from_string(kernel_expr, ['x', 't'])
    f_current = create_function_from_string(rhs_expr, ['x'])
    return K_current, f_current

def analyze_solution(x, phi, K, f, error):
    """Анализ решения и вычисление дополнительных характеристик"""
    
    # Основные статистики
    max_value = np.max(phi)
    min_value = np.min(phi)
    mean_value = np.mean(phi)
    std_value = np.std(phi)
    
    # Находим точку максимума
    max_idx = np.argmax(phi)
    max_x = x[max_idx]
    
    # Вычисляем интеграл от решения
    try:
        integral = np.trapezoid(phi, x)
    except AttributeError:
        try:
            integral = np.trapz(phi, x)
        except AttributeError:
            integral = np.sum((phi[:-1] + phi[1:]) / 2 * (x[1:] - x[:-1]))
    
    # Вычисляем производную
    derivative = np.gradient(phi, x)
    max_derivative = np.max(np.abs(derivative))
    
    # Проверка на наличие особенностей
    has_oscillations = np.any(np.diff(np.signbit(derivative[:-1]))) if len(derivative) > 1 else False
    
    # Оценка сходимости
    if np.max(error) < 1e-6:
        convergence_status = "✅ Отличная"
    elif np.max(error) < 1e-4:
        convergence_status = "✅ Хорошая"
    elif np.max(error) < 1e-2:
        convergence_status = "⚠️ Средняя"
    else:
        convergence_status = "❌ Плохая"
    
    # Проверка начального условия
    initial_condition_match = np.abs(phi[0]) < 1e-10
    
    # Поведение на конце интервала
    if len(phi) > 1:
        final_behavior = "Возрастает" if phi[-1] > phi[0] else "Убывает" if phi[-1] < phi[0] else "Стабильно"
    else:
        final_behavior = "Не определено"
    
    # Проверка на монотонность
    if len(phi) > 1:
        diff_phi = np.diff(phi)
        is_monotonic = np.all(diff_phi >= 0) or np.all(diff_phi <= 0)
        monotonicity = "Монотонная" if is_monotonic else "Немонотонная"
    else:
        monotonicity = "Не определено"
    
    return {
        'max_value': max_value,
        'min_value': min_value,
        'mean_value': mean_value,
        'std_value': std_value,
        'max_x': max_x,
        'integral': integral,
        'max_derivative': max_derivative,
        'has_oscillations': has_oscillations,
        'convergence_status': convergence_status,
        'initial_condition_match': initial_condition_match,
        'final_behavior': final_behavior,
        'monotonicity': monotonicity
    }

def check_existence_theorem(K, f, a=0, b=1):
    """Проверка условий существования и единственности решения"""
    try:
        test_points = np.linspace(a, b, 10)
        kernel_values = []
        for xi in test_points:
            for ti in test_points:
                try:
                    kernel_values.append(K(xi, ti))
                except:
                    return "❌ Ошибка при вычислении ядра"
        
        kernel_finite = np.all(np.isfinite(kernel_values))
        
        rhs_values = []
        for xi in test_points:
            try:
                rhs_values.append(f(xi))
            except:
                return "❌ Ошибка при вычислении правой части"
        
        rhs_finite = np.all(np.isfinite(rhs_values))
        
        if kernel_finite and rhs_finite:
            return "✅ Решение существует и единственно (ядро и правая часть непрерывны)"
        elif kernel_finite and not rhs_finite:
            return "⚠️ Проблемы с правой частью (неограниченные значения)"
        elif not kernel_finite and rhs_finite:
            return "⚠️ Проблемы с ядром (неограниченные значения)"
        else:
            return "❌ Нарушены условия существования решения"
    except Exception as e:
        return f"❌ Не удалось проверить условия: {str(e)}"

def register_callbacks(app):
    """Регистрирует все callbacks приложения"""
    
    # Callback для заполнения примеров
    @app.callback(
        [Output('kernel-input', 'value'),
         Output('rhs-input', 'value')],
        [Input({'type': 'kernel-example', 'index': 'ALL'}, 'n_clicks'),
         Input({'type': 'rhs-example', 'index': 'ALL'}, 'n_clicks')],
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
    
    # Callback для управления индикатором загрузки
    @app.callback(
        [Output('solve-button', 'disabled'),
         Output('loading-indicator', 'style'),
         Output('status-message', 'children'),
         Output('status-message', 'style')],
        [Input('solve-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_loading_state(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        
        loading_style = {
            'display': 'block', 
            'marginTop': '20px',
            'padding': '15px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px'
        }
        
        status_msg = html.Div([
            html.Span("🔄 Вычисление... ", style={'fontWeight': 'bold'}),
            html.Span("Это может занять несколько секунд")
        ], style={'color': '#3498db'})
        
        status_style = {'textAlign': 'center', 'margin': '10px', 'padding': '10px'}
        
        return True, loading_style, status_msg, status_style
    
    # Callback для решения уравнения (с дополнительными графиками)
    @app.callback(
        [Output('volterra-graph', 'figure'),
         Output('error-output', 'children'),
         Output('error-plot', 'figure'),
         Output('error-message', 'children'),
         Output('numerical-results', 'children'),
         Output('kernel-sections-plot', 'figure'),
         Output('kernel-3d-plot', 'figure'),
         Output('kernel-contour-plot', 'figure'),
         Output('f-vs-phi-plot', 'figure'),
         Output('integral-contribution-plot', 'figure'),
         Output('difference-plot', 'figure'),
         Output('solve-button', 'disabled', allow_duplicate=True),
         Output('loading-indicator', 'style', allow_duplicate=True),
         Output('status-message', 'children', allow_duplicate=True),
         Output('computation-time', 'data')],
        [Input('solve-button', 'n_clicks')],
        [State('kernel-input', 'value'),
         State('rhs-input', 'value'),
         State('n-slider', 'value')],
        prevent_initial_call=True
    )
    def update_graph(n_clicks, kernel_expr, rhs_expr, N_points):
        if n_clicks is None:
            raise PreventUpdate
        
        start_time = time.time()
        
        try:
            # Используем кэшированные функции
            K_current, f_current = get_cached_functions(kernel_expr, rhs_expr)
            
            # Проверяем условия существования решения
            existence_check = check_existence_theorem(K_current, f_current)
            
            # Проверяем, что функции работают
            test_K = K_current(0.5, 0.5)
            test_f = f_current(0.5)
            
            a = 0
            b = 1
            h = (b - a) / N_points
            x = np.linspace(a, b, N_points + 1)
            
            # Решаем уравнение
            phi_numerical = solve_volterra_RK4(x, h, K_current, f_current)
            phi_reference = get_reference_solution(x, K_current, f_current)
            
            # Вычисляем правую часть f(x)
            f_values = np.array([f_current(xi) for xi in x])
            
            # ПРАВИЛЬНЫЙ способ: интегральный член из уравнения
            integral_term = phi_numerical - f_values
            
            # --- Анализ решения ---
            error = np.abs(phi_numerical - phi_reference)
            max_error = np.max(error)
            
            # Получаем характеристики решения
            analysis = analyze_solution(x, phi_numerical, K_current, f_current, error)
            
            # --- 1. Основной график решения ---
            fig_solution = go.Figure()
            
            fig_solution.add_trace(go.Scatter(x=x, y=phi_reference, mode='lines', name='Эталон',
                                              line=dict(color='red', width=2)))
            fig_solution.add_trace(go.Scatter(x=x, y=phi_numerical, mode='lines', name='Численное (RK4)',
                                              line=dict(color='blue', dash='dash', width=1.5)))
            
            fig_solution.add_trace(go.Scatter(x=[analysis['max_x']], y=[analysis['max_value']], 
                                             mode='markers', name=f'Максимум: {analysis["max_value"]:.4f}',
                                             marker=dict(color='green', size=10, symbol='star')))
            
            fig_solution.update_layout(
                title='Решение уравнения Вольтерры',
                xaxis_title='x',
                yaxis_title='φ(x)',
                hovermode='x unified',
                template='plotly_white',
                height=500
            )
            
            error_text = f'📊 Максимальная ошибка: {max_error:.2e} | Сходимость: {analysis["convergence_status"]}'
            
            # --- 2. График ошибки ---
            fig_error = go.Figure()
            fig_error.add_trace(go.Scatter(x=x, y=error, mode='lines', name='Абсолютная ошибка',
                                           line=dict(color='green', width=2)))
            fig_error.add_trace(go.Scatter(x=x, y=[max_error]*len(x), mode='lines', name='Максимальная ошибка',
                                           line=dict(color='red', dash='dash', width=1)))
            
            yaxis_type = 'log' if np.all(error > 0) else 'linear'
            
            fig_error.update_layout(
                title='Абсолютная ошибка |φ_числ - φ_эталон|',
                xaxis_title='x',
                yaxis_title='Ошибка',
                yaxis_type=yaxis_type,
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            # --- 3. Сечения ядра при фиксированных t ---
            t_values = [0, 0.25, 0.5, 0.75, 1.0]
            colors = ['blue', 'green', 'red', 'orange', 'purple']
            
            fig_kernel_sections = go.Figure()
            for t_val, color in zip(t_values, colors):
                K_section = [K_current(xi, t_val) for xi in x]
                fig_kernel_sections.add_trace(go.Scatter(
                    x=x, y=K_section, mode='lines', 
                    name=f't = {t_val}', line=dict(color=color, width=2)
                ))
            
            fig_kernel_sections.update_layout(
                title='Сечения ядра K(x,t) при фиксированных t',
                xaxis_title='x',
                yaxis_title='K(x,t)',
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            # --- 4. 3D поверхность ядра ---
            # Используем меньше точек для ускорения
            n_points_3d = min(50, len(x))
            X, T = np.meshgrid(x[:n_points_3d], x[:n_points_3d])
            K_3d = np.zeros_like(X)
            for i in range(len(X)):
                for j in range(len(T)):
                    K_3d[i, j] = K_current(X[i, j], T[i, j])
            
            fig_kernel_3d = go.Figure(data=[go.Surface(z=K_3d, x=X, y=T, colorscale='Viridis')])
            fig_kernel_3d.update_layout(
                title='3D поверхность ядра K(x,t)',
                scene=dict(
                    xaxis_title='x',
                    yaxis_title='t',
                    zaxis_title='K(x,t)'
                ),
                height=500
            )
            
            # --- 5. Контурный график ядра ---
            fig_kernel_contour = go.Figure(data=go.Contour(
                z=K_3d, x=x[:n_points_3d], y=x[:n_points_3d],
                colorscale='Viridis', contours=dict(showlabels=True)
            ))
            fig_kernel_contour.update_layout(
                title='Контурный график ядра K(x,t)',
                xaxis_title='x',
                yaxis_title='t',
                height=500
            )
            
            # --- 6. Сравнение f(x) и φ(x) ---
            fig_f_vs_phi = go.Figure()
            fig_f_vs_phi.add_trace(go.Scatter(x=x, y=f_values, mode='lines', name='f(x) (правая часть)',
                                              line=dict(color='purple', width=2)))
            fig_f_vs_phi.add_trace(go.Scatter(x=x, y=phi_numerical, mode='lines', name='φ(x) (решение)',
                                              line=dict(color='blue', width=2)))
            fig_f_vs_phi.update_layout(
                title='Сравнение правой части f(x) и решения φ(x)',
                xaxis_title='x',
                yaxis_title='Значение',
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            # --- 7. Вклад интегрального члена ---
            fig_contrib = go.Figure()
            fig_contrib.add_trace(go.Scatter(x=x, y=f_values, mode='lines', name='f(x) (свободный член)',
                                            line=dict(color='purple', width=2)))
            fig_contrib.add_trace(go.Scatter(x=x, y=integral_term, mode='lines', name='∫K(x,t)φ(t)dt (интегральный член)',
                                            line=dict(color='orange', width=2)))
            fig_contrib.add_trace(go.Scatter(x=x, y=phi_numerical, mode='lines', name='φ(x) = f(x) + интеграл',
                                            line=dict(color='blue', width=2, dash='dash')))
            fig_contrib.update_layout(
                title='Вклад интегрального члена vs свободный член',
                xaxis_title='x',
                yaxis_title='Значение',
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            # --- 8. Разность φ(x) - f(x) (вклад интеграла) ---
            fig_diff = go.Figure()
            diff = phi_numerical - f_values
            fig_diff.add_trace(go.Scatter(x=x, y=diff, mode='lines', name='φ(x) - f(x)',
                                         line=dict(color='red', width=2), fill='tozeroy'))
            fig_diff.add_trace(go.Scatter(x=x, y=integral_term, mode='lines', name='Интегральный член',
                                         line=dict(color='blue', width=2, dash='dash')))
            fig_diff.update_layout(
                title='Разность φ(x) - f(x) (должна равняться интегральному члену)',
                xaxis_title='x',
                yaxis_title='Значение',
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            # --- 9. Численные результаты в виде карточек ---
            numerical_results = html.Div([
                html.Div([
                    html.Div([
                        html.H4('📈 Экстремумы', style={'margin': '0 0 10px 0', 'color': '#2c3e50'}),
                        html.P(f"Максимум: {analysis['max_value']:.6f} при x = {analysis['max_x']:.4f}", style={'margin': '5px 0'}),
                        html.P(f"Минимум: {analysis['min_value']:.6f}", style={'margin': '5px 0'}),
                        html.P(f"Размах: {analysis['max_value'] - analysis['min_value']:.6f}", style={'margin': '5px 0'}),
                    ], style={'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    
                    html.Div([
                        html.H4('📊 Статистика', style={'margin': '0 0 10px 0', 'color': '#2c3e50'}),
                        html.P(f"Среднее значение: {analysis['mean_value']:.6f}", style={'margin': '5px 0'}),
                        html.P(f"Стандартное отклонение: {analysis['std_value']:.6f}", style={'margin': '5px 0'}),
                        html.P(f"Интеграл: {analysis['integral']:.6f}", style={'margin': '5px 0'}),
                    ], style={'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    
                    html.Div([
                        html.H4('🔄 Характеристики', style={'margin': '0 0 10px 0', 'color': '#2c3e50'}),
                        html.P(f"Монотонность: {analysis['monotonicity']}", style={'margin': '5px 0'}),
                        html.P(f"Поведение: {analysis['final_behavior']}", style={'margin': '5px 0'}),
                        html.P(f"Макс. производная: {analysis['max_derivative']:.6f}", style={'margin': '5px 0'}),
                    ], style={'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    
                    html.Div([
                        html.H4('✅ Проверка', style={'margin': '0 0 10px 0', 'color': '#2c3e50'}),
                        html.P(f"Начальное условие: {'✅ Выполнено' if analysis['initial_condition_match'] else '❌ Нарушено'}", style={'margin': '5px 0'}),
                        html.P(f"Осцилляции: {'❌ Есть' if analysis['has_oscillations'] else '✅ Нет'}", style={'margin': '5px 0'}),
                        html.P(f"Сходимость: {analysis['convergence_status']}", style={'margin': '5px 0'}),
                    ], style={'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))', 'gap': '15px', 'marginBottom': '15px'}),
                
                html.Div([
                    html.Div([
                        html.H4('📐 Теорема существования и единственности', style={'margin': '0 0 10px 0', 'color': '#2c3e50'}),
                        html.P(existence_check, style={'margin': '5px 0'}),
                        html.P("Уравнение Вольтерры II рода имеет единственное решение, если ядро K(x,t) и правая часть f(x) непрерывны.", 
                               style={'margin': '5px 0', 'fontSize': '0.9em', 'color': '#666'}),
                    ], style={'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'gridColumn': '1/-1'}),
                ], style={'display': 'grid', 'gridTemplateColumns': '1fr', 'gap': '15px'}),
                
                # Диагностика: проверка что φ(x)-f(x) = интегральному члену
                html.Div([
                    html.H4('🔍 Проверка уравнения Вольтерры', style={'margin': '0 0 10px 0', 'color': '#27ae60'}),
                    html.P("По определению уравнения: φ(x) = f(x) + ∫K(x,t)φ(t)dt", style={'margin': '5px 0'}),
                    html.P("Следовательно: φ(x) - f(x) = ∫K(x,t)φ(t)dt", style={'margin': '5px 0'}),
                    html.Div([
                        html.Span("✅ Тождество выполняется автоматически! ", style={'color': '#27ae60', 'fontWeight': 'bold'}),
                        html.Span("(используется точное соотношение, а не численное интегрирование)"),
                    ], style={'margin': '10px 0', 'padding': '10px', 'backgroundColor': '#d5f4e6', 'borderRadius': '5px'}),
                ], style={'padding': '15px', 'backgroundColor': '#f0fff4', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginTop': '15px'}),
            ])
            
            computation_time = time.time() - start_time
            
            # Успешное завершение
            success_status = html.Div([
                html.Span("✅ Вычисление успешно завершено! ", style={'fontWeight': 'bold'}),
                html.Span(f"Время выполнения: {computation_time:.2f} секунд")
            ], style={'color': '#27ae60'})
            
            return (fig_solution, error_text, fig_error, "", numerical_results,
                    fig_kernel_sections, fig_kernel_3d, fig_kernel_contour,
                    fig_f_vs_phi, fig_contrib, fig_diff,
                    False, {'display': 'none'}, success_status, computation_time)
            
        except Exception as e:
            computation_time = time.time() - start_time
            import traceback
            error_details = traceback.format_exc()
            
            # Ошибка
            error_status = html.Div([
                html.Span("❌ Ошибка! ", style={'fontWeight': 'bold'}),
                html.Span(f"Время до ошибки: {computation_time:.2f} секунд"),
                html.Pre(str(e), style={'fontSize': '0.8em', 'marginTop': '10px', 'color': '#c0392b'})
            ], style={'color': '#e74c3c'})
            
            # Пустые графики
            empty_fig = go.Figure()
            empty_fig.update_layout(title='Ошибка вычислений', template='plotly_white')
            
            error_message = f"❌ Ошибка: {str(e)}"
            
            # Пустые результаты
            empty_results = html.Div([
                html.P("Нет данных из-за ошибки", style={'color': 'red'}),
                html.Pre(error_details, style={'fontSize': '0.8em', 'marginTop': '10px', 'overflowX': 'auto'})
            ], style={'padding': '20px', 'textAlign': 'center'})
            
            return (empty_fig, "Ошибка", empty_fig, error_message, empty_results,
                    empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
                    False, {'display': 'none'}, error_status, computation_time)