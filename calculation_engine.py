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


def trapezoidal_sum(x_set, phi_set, n, target_x, K, h):
    """
    Квадратура трапеций по известным узлам
    ПОЛНЫЙ АНАЛОГ MATLAB функции trapezoidal_sum
    
    Параметры:
    x_set - массив узлов
    phi_set - значения φ в узлах
    n - текущий индекс (количество известных узлов)
    target_x - точка, в которой вычисляется интеграл
    K - ядро
    h - шаг
    """
    s = 0.0
    if n > 1:
        for j in range(n-1):  # от 0 до n-2 (индексы MATLAB: 1:n-1)
            val1 = safe_function_evaluation(K, target_x, x_set[j]) * phi_set[j]
            val2 = safe_function_evaluation(K, target_x, x_set[j+1]) * phi_set[j+1]
            s += (h / 2) * (val1 + val2)
    return s


def trapezoidal_sum_extended(x_set, phi_set, n, target_x, K, h, phi_val):
    """
    Расширенная квадратура трапеций с учетом промежуточной точки
    ПОЛНЫЙ АНАЛОГ MATLAB функции trapezoidal_sum_extended
    """
    # Базовый интеграл по известным узлам
    s = trapezoidal_sum(x_set, phi_set, n, target_x, K, h)
    
    # Добавляем последний интервал до target_x
    h_last = target_x - x_set[n-1]  # в MATLAB x_set(n)
    if h_last > 0:
        val1 = safe_function_evaluation(K, target_x, x_set[n-1]) * phi_set[n-1]
        val2 = safe_function_evaluation(K, target_x, target_x) * phi_val
        s += (h_last / 2) * (val1 + val2)
    
    return s


def solve_volterra_RK4_trapezoidal(x, h, K, f, phi0):
    """
    Комбинированный метод Рунге-Кутты 4-го порядка с квадратурой трапеций
    ПОЛНЫЙ АНАЛОГ MATLAB функции solve_volterra_RK4_trapezoidal
    """
    N = len(x) - 1
    phi = np.zeros(N + 1)
    phi[0] = phi0
    
    # Кеш для значений ядра (для ускорения)
    K_cache = {}
    
    def get_K(x_val, t_val):
        key = (round(x_val, 12), round(t_val, 12))
        if key not in K_cache:
            K_cache[key] = safe_function_evaluation(K, x_val, t_val)
        return K_cache[key]
    
    for i in range(N):
        xi = x[i]
        yi = phi[i]
        
        # Вычисляем f(xi) один раз
        f_xi = safe_function_evaluation(f, xi)
        
        # k1
        I1 = trapezoidal_sum(x, phi, i+1, xi, get_K, h)
        k1 = h * (f_xi + I1)
        
        # k2
        phi_mid1 = yi + k1 / 2
        x_mid = xi + h / 2
        f_mid = safe_function_evaluation(f, x_mid)
        I2 = trapezoidal_sum_extended(x, phi, i+1, x_mid, get_K, h, phi_mid1)
        k2 = h * (f_mid + I2)
        
        # k3
        phi_mid2 = yi + k2 / 2
        I3 = trapezoidal_sum_extended(x, phi, i+1, x_mid, get_K, h, phi_mid2)
        k3 = h * (f_mid + I3)
        
        # k4
        phi_next_est = yi + k3
        x_next = xi + h
        f_next = safe_function_evaluation(f, x_next)
        I4 = trapezoidal_sum_extended(x, phi, i+1, x_next, get_K, h, phi_next_est)
        k4 = h * (f_next + I4)
        
        # Итоговое значение
        phi[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6
    
    return phi


def get_reference_solution(x, K, f, phi0):
    """
    Эталонное решение для интегро-дифференциального уравнения
    ПОЛНЫЙ АНАЛОГ MATLAB функции get_reference_solution
    """
    N_ref = 300  # как в MATLAB: N_ref = 200? но для точности лучше 300
    h_ref = (x[-1] - x[0]) / N_ref
    x_ref = np.linspace(x[0], x[-1], N_ref + 1)
    
    # Решаем тем же методом, но с более мелкой сеткой
    phi_ref = solve_volterra_RK4_trapezoidal(x_ref, h_ref, K, f, phi0)
    
    # Интерполируем на исходную сетку (spline как в MATLAB)
    interp_func = interp1d(x_ref, phi_ref, kind='cubic')  # cubic = spline
    return interp_func(x)


# Основные экспортируемые функции для совместимости с вашим приложением
def solve_volterra_RK4(x, h, K, f, initial_condition=0.0):
    """
    Обертка для совместимости с существующим кодом
    """
    phi = solve_volterra_RK4_trapezoidal(x, h, K, f, initial_condition)
    
    # Для совместимости возвращаем также integral_values (хотя в MATLAB их нет)
    integral_values = np.zeros(len(x))
    return phi, integral_values


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