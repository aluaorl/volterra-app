# calculation_engine.py
import numpy as np
from scipy.interpolate import interp1d
from expression_parser import parse_user_input, safe_eval_with_checks

def safe_function_evaluation(func, *args):
    """Безопасное вычисление функции с проверкой ошибок"""
    try:
        result = func(*args)
        if isinstance(result, complex):
            raise ValueError("Выражение дает комплексное число")
        if isinstance(result, (int, float, np.number)):
            if np.isinf(result):
                raise ValueError("Обнаружена бесконечность")
            if np.isnan(result):
                raise ValueError("Обнаружена неопределенность")
        return result
    except Exception as e:
        error_msg = str(e).lower()
        if "division by zero" in error_msg:
            raise ValueError("Обнаружено деление на ноль")
        elif "invalid value" in error_msg:
            raise ValueError("Некорректное математическое выражение")
        elif "math domain error" in error_msg:
            raise ValueError("Ошибка области определения функции")
        elif "name" in error_msg and "is not defined" in error_msg:
            import re
            match = re.search(r"name '([^']+)' is not defined", error_msg)
            if match:
                func_name = match.group(1)
                raise ValueError(f"Неизвестная функция или переменная '{func_name}'")
            raise ValueError(str(e))
        else:
            raise ValueError(str(e))


def trap_sum(n, x, h, K, phi, f_value, current_x):
    """
    ВАШ МЕТОД ТРАПЕЦИЙ для вычисления интеграла и правой части
    Аналог MATLAB функции trap_sum
    
    Параметры:
    n - текущий индекс
    x - массив узлов
    h - шаг
    K - ядро
    phi - значения φ на предыдущих шагах
    f_value - значение f(x_n)
    current_x - текущее значение x_n
    
    Возвращает:
    s = f(x_n) + ∫₀ˣⁿ K(x_n,t)·φ(t) dt  (методом трапеций)
    """
    s = 0.0
    # Интеграл от 0 до x_{n-1} методом трапеций
    for i in range(n-1):  # от 0 до n-2 (индексы)
        s += (h / 2) * (
            safe_function_evaluation(K, current_x, x[i]) * phi[i] + 
            safe_function_evaluation(K, current_x, x[i+1]) * phi[i+1]
        )
    # Добавляем f(x_n)
    s += f_value
    return s


def solve_integro_differential_combined(x, h, K, f, initial_condition=0.0):
    """
    КОМБИНИРОВАННЫЙ МЕТОД для интегро-дифференциального уравнения:
    φ'(x) = f(x) + ∫₀ˣ K(x,t)·φ(t) dt
    
    КОМБИНАЦИЯ:
    1. ВАШ МЕТОД ТРАПЕЦИЙ (trap_sum) - для вычисления интеграла
    2. Метод Рунге-Кутты 4-го порядка - для решения ОДУ
    
    Алгоритм полностью соответствует вашему MATLAB коду,
    но адаптирован для ОДУ первого порядка.
    """
    N = len(x) - 1
    phi = np.zeros(N + 1)
    phi[0] = initial_condition  # φ(0) = заданное начальное условие
    
    # Предвычисление всех значений f(x)
    f_values = np.zeros(N + 1)
    for idx, xi in enumerate(x):
        f_values[idx] = safe_function_evaluation(f, xi)
    
    # Кеш для значений ядра (ускоряет повторные вызовы)
    K_cache = {}
    
    def get_K(x_val, t_val):
        key = (round(x_val, 10), round(t_val, 10))
        if key not in K_cache:
            K_cache[key] = safe_function_evaluation(K, x_val, t_val)
        return K_cache[key]
    
    integral_values = np.zeros(N + 1)
    integral_values[0] = 0.0
    
    for i in range(N):
        xi = x[i]
        yi = phi[i]
        
        # ========== ВАШ МЕТОД ТРАПЕЦИЙ для вычисления I(xi) ==========
        # Вычисляем S = f(xi) + интеграл методом трапеций
        S_i = 0.0
        for j in range(i):
            S_i += (h / 2) * (
                get_K(xi, x[j]) * phi[j] + 
                get_K(xi, x[j+1]) * phi[j+1]
            )
        S_i += f_values[i]
        
        # Интегральный член I(xi) = S_i - f(xi)
        I_xi = S_i - f_values[i]
        integral_values[i] = I_xi
        
        # Правая часть ОДУ: F = f(xi) + I(xi) = S_i
        F_current = S_i
        
        # ========== МЕТОД РУНГЕ-КУТТЫ 4-ГО ПОРЯДКА ==========
        k1 = h * F_current
        
        # k2: используем x_mid = xi + h/2
        x_mid = xi + h * 0.5
        
        # ВЫЧИСЛЯЕМ S в точке x_mid ВАШИМ МЕТОДОМ ТРАПЕЦИЙ
        S_mid = 0.0
        for j in range(i):
            S_mid += (h / 2) * (
                get_K(x_mid, x[j]) * phi[j] + 
                get_K(x_mid, x[j+1]) * phi[j+1]
            )
        
        # Добавляем вклад от отрезка [xi, x_mid] с прогнозом φ_mid
        phi_mid_guess = yi + k1 * 0.5
        S_mid += (h / 4) * (
            get_K(x_mid, xi) * yi + 
            get_K(x_mid, x_mid) * phi_mid_guess
        )
        S_mid += f_values[i]  # f(x_mid) ≈ f(xi) для простоты, или интерполировать
        
        k2 = h * S_mid
        
        # k3: снова в x_mid
        phi_mid_guess2 = yi + k2 * 0.5
        S_mid2 = 0.0
        for j in range(i):
            S_mid2 += (h / 2) * (
                get_K(x_mid, x[j]) * phi[j] + 
                get_K(x_mid, x[j+1]) * phi[j+1]
            )
        S_mid2 += (h / 4) * (
            get_K(x_mid, xi) * yi + 
            get_K(x_mid, x_mid) * phi_mid_guess2
        )
        S_mid2 += f_values[i]
        
        k3 = h * S_mid2
        
        # k4: в точке x_next = xi + h
        x_next = xi + h
        
        S_next = 0.0
        for j in range(i):
            S_next += (h / 2) * (
                get_K(x_next, x[j]) * phi[j] + 
                get_K(x_next, x[j+1]) * phi[j+1]
            )
        
        phi_next_guess = yi + k3
        S_next += (h / 2) * (
            get_K(x_next, xi) * yi + 
            get_K(x_next, x_next) * phi_next_guess
        )
        S_next += f_values[i+1]
        
        k4 = h * S_next
        
        # Вычисляем φ[i+1] по формуле Рунге-Кутты
        phi[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6.0
        
        # Сохраняем интегральное значение
        integral_values[i+1] = S_next - f_values[i+1]
    
    return phi, integral_values


def get_reference_solution(x, K, f, initial_condition=0.0):
    """
    Эталонное решение для интегро-дифференциального уравнения
    Использует более мелкую сетку для высокой точности
    """
    N_ref = 300  # Баланс скорости и точности
    h_ref = (x[-1] - x[0]) / N_ref
    x_ref = np.linspace(x[0], x[-1], N_ref + 1)
    
    f_ref = np.zeros(N_ref + 1)
    for idx, xi in enumerate(x_ref):
        f_ref[idx] = safe_function_evaluation(f, xi)
    
    phi_ref = np.zeros(N_ref + 1)
    phi_ref[0] = initial_condition
    
    # Кеш для значений ядра
    K_cache_ref = {}
    
    def get_K_ref(x_val, t_val):
        key = (round(x_val, 10), round(t_val, 10))
        if key not in K_cache_ref:
            K_cache_ref[key] = safe_function_evaluation(K, x_val, t_val)
        return K_cache_ref[key]
    
    for i in range(N_ref):
        xi = x_ref[i]
        yi = phi_ref[i]
        
        try:
            # Вычисляем S = f(xi) + интеграл методом трапеций
            S_i = 0.0
            for j in range(i):
                S_i += (h_ref / 2) * (
                    get_K_ref(xi, x_ref[j]) * phi_ref[j] + 
                    get_K_ref(xi, x_ref[j+1]) * phi_ref[j+1]
                )
            S_i += f_ref[i]
            
            k1 = h_ref * S_i
            
            # k2
            x_mid = xi + h_ref * 0.5
            S_mid = 0.0
            for j in range(i):
                S_mid += (h_ref / 2) * (
                    get_K_ref(x_mid, x_ref[j]) * phi_ref[j] + 
                    get_K_ref(x_mid, x_ref[j+1]) * phi_ref[j+1]
                )
            
            phi_mid_guess = yi + k1 * 0.5
            S_mid += (h_ref / 4) * (
                get_K_ref(x_mid, xi) * yi + 
                get_K_ref(x_mid, x_mid) * phi_mid_guess
            )
            S_mid += f_ref[i]
            k2 = h_ref * S_mid
            
            # k3
            phi_mid_guess2 = yi + k2 * 0.5
            S_mid2 = 0.0
            for j in range(i):
                S_mid2 += (h_ref / 2) * (
                    get_K_ref(x_mid, x_ref[j]) * phi_ref[j] + 
                    get_K_ref(x_mid, x_ref[j+1]) * phi_ref[j+1]
                )
            S_mid2 += (h_ref / 4) * (
                get_K_ref(x_mid, xi) * yi + 
                get_K_ref(x_mid, x_mid) * phi_mid_guess2
            )
            S_mid2 += f_ref[i]
            k3 = h_ref * S_mid2
            
            # k4
            x_next = xi + h_ref
            S_next = 0.0
            for j in range(i):
                S_next += (h_ref / 2) * (
                    get_K_ref(x_next, x_ref[j]) * phi_ref[j] + 
                    get_K_ref(x_next, x_ref[j+1]) * phi_ref[j+1]
                )
            
            phi_next_guess = yi + k3
            S_next += (h_ref / 2) * (
                get_K_ref(x_next, xi) * yi + 
                get_K_ref(x_next, x_next) * phi_next_guess
            )
            S_next += f_ref[i+1]
            k4 = h_ref * S_next
            
            phi_ref[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6.0
            
        except Exception as e:
            raise ValueError(str(e))
    
    interp_func = interp1d(x_ref, phi_ref, kind='linear')
    return interp_func(x)


# Основные экспортируемые функции
solve_volterra_RK4 = solve_integro_differential_combined


def create_function_from_string(expr_str, var_names):
    """Создает функцию из строки выражения"""
    parsed_expr = parse_user_input(expr_str, var_names)
    compiled = compile(parsed_expr, '<string>', 'eval')
    
    def func(*args):
        try:
            namespace = {'np': np}
            for var_name, var_value in zip(var_names, args):
                namespace[var_name] = var_value
            return safe_eval_with_checks(compiled, namespace)
        except Exception as e:
            error_msg = str(e)
            if error_msg.startswith("Ошибка вычисления:"):
                error_msg = error_msg.replace("Ошибка вычисления:", "").strip()
            raise ValueError(error_msg)
    return func