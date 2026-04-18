import numpy as np
from scipy.interpolate import interp1d

def solve_volterra_RK4_fast(x, h, K, f):
    """Максимально оптимизированное решение с кэшированием"""
    N = len(x) - 1
    phi = np.zeros(N + 1)
    phi[0] = 0.0
    
    # Предвычисление всех значений f(x)
    f_values = np.array([f(xi) for xi in x])
    
    for i in range(N):
        xi = x[i]
        yi = phi[i]
        
        # Предвычисляем значения ядра для всех target_x
        target_x1 = xi
        target_x2 = xi + h/2
        target_x3 = xi + h/2
        target_x4 = xi + h
        
        # Массивы для хранения значений ядра
        K1 = np.zeros(i + 2)
        K2 = np.zeros(i + 2)
        K3 = np.zeros(i + 2)
        K4 = np.zeros(i + 2)
        
        # Вычисляем все значения ядра за один проход с кэшированием
        for j in range(i + 1):
            xj = x[j]
            K1[j] = K(target_x1, xj)
            K2[j] = K(target_x2, xj)
            K3[j] = K(target_x3, xj)
            K4[j] = K(target_x4, xj)
        
        K1[i+1] = K(target_x1, target_x1)
        K2[i+1] = K(target_x2, target_x2)
        K3[i+1] = K(target_x3, target_x3)
        K4[i+1] = K(target_x4, target_x4)
        
        # Вычисление интегральных сумм векторизованно
        if i > 0:
            # Для k1
            sum1 = np.sum((K1[:i] * phi[:i] + K1[1:i+1] * phi[1:i+1])) * (h/2)
            k1 = h * (f_values[i] + sum1)
            
            # Для k2
            sum2 = np.sum((K2[:i] * phi[:i] + K2[1:i+1] * phi[1:i+1])) * (h/2)
            h_last = h/2
            sum2 += (h_last/2) * (K2[i] * phi[i] + K2[i+1] * (yi + k1/2))
            k2 = h * (f_values[i] + sum2)
            
            # Для k3
            sum3 = np.sum((K3[:i] * phi[:i] + K3[1:i+1] * phi[1:i+1])) * (h/2)
            sum3 += (h_last/2) * (K3[i] * phi[i] + K3[i+1] * (yi + k2/2))
            k3 = h * (f_values[i] + sum3)
            
            # Для k4
            sum4 = np.sum((K4[:i] * phi[:i] + K4[1:i+1] * phi[1:i+1])) * (h/2)
            h_last = h
            sum4 += (h_last/2) * (K4[i] * phi[i] + K4[i+1] * (yi + k3))
            k4 = h * (f_values[i+1] + sum4)
        else:
            # Первая итерация (i=0)
            k1 = h * f_values[0]
            k2 = h * f_values[0]
            k3 = h * f_values[0]
            k4 = h * f_values[1]
        
        phi[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6
    
    return phi

def get_reference_solution_fast(x, K, f):
    """Быстрое эталонное решение с кэшированием"""
    # Уменьшаем количество точек для эталона
    N_ref = 200
    h_ref = (x[-1] - x[0]) / N_ref
    x_ref = np.linspace(x[0], x[-1], N_ref + 1)
    
    # Предвычисление f
    f_ref = np.array([f(xi) for xi in x_ref])
    
    phi_ref = np.zeros(N_ref + 1)
    phi_ref[0] = 0
    
    for i in range(N_ref):
        xi = x_ref[i]
        yi = phi_ref[i]
        
        if i > 0:
            # Для k1
            K_vals = np.array([K(xi, x_ref[j]) for j in range(i+1)])
            K_diag = K(xi, xi)
            sum1 = np.sum(K_vals[:i] * phi_ref[:i] + K_vals[1:i+1] * phi_ref[1:i+1]) * (h_ref/2)
            k1 = h_ref * (f_ref[i] + sum1)
            
            # Для k2
            x_mid = xi + h_ref/2
            K_vals_mid = np.array([K(x_mid, x_ref[j]) for j in range(i+1)])
            K_diag_mid = K(x_mid, x_mid)
            sum2 = np.sum(K_vals_mid[:i] * phi_ref[:i] + K_vals_mid[1:i+1] * phi_ref[1:i+1]) * (h_ref/2)
            sum2 += (h_ref/2) * (K_vals_mid[i] * phi_ref[i] + K_diag_mid * (yi + k1/2))
            k2 = h_ref * (f_ref[i] + sum2)
            
            # Для k3
            sum3 = np.sum(K_vals_mid[:i] * phi_ref[:i] + K_vals_mid[1:i+1] * phi_ref[1:i+1]) * (h_ref/2)
            sum3 += (h_ref/2) * (K_vals_mid[i] * phi_ref[i] + K_diag_mid * (yi + k2/2))
            k3 = h_ref * (f_ref[i] + sum3)
            
            # Для k4
            x_next = xi + h_ref
            K_vals_next = np.array([K(x_next, x_ref[j]) for j in range(i+1)])
            K_diag_next = K(x_next, x_next)
            sum4 = np.sum(K_vals_next[:i] * phi_ref[:i] + K_vals_next[1:i+1] * phi_ref[1:i+1]) * (h_ref/2)
            sum4 += h_ref * (K_vals_next[i] * phi_ref[i] + K_diag_next * (yi + k3)) / 2
            k4 = h_ref * (f_ref[i+1] + sum4)
        else:
            k1 = h_ref * f_ref[0]
            k2 = h_ref * f_ref[0]
            k3 = h_ref * f_ref[0]
            k4 = h_ref * f_ref[1]
        
        phi_ref[i+1] = yi + (k1 + 2*k2 + 2*k3 + k4) / 6
    
    # Линейная интерполяция (быстрее)
    interp_func = interp1d(x_ref, phi_ref, kind='linear')
    return interp_func(x)

# Используем быстрые версии по умолчанию
solve_volterra_RK4 = solve_volterra_RK4_fast
get_reference_solution = get_reference_solution_fast

def safe_eval_function(expr_str, variables, variable_names):
    """Безопасное вычисление функции из строки"""
    try:
        namespace = {'np': np}
        for var_name, var_value in zip(variable_names, variables):
            namespace[var_name] = var_value
        
        result = eval(expr_str, {"__builtins__": {}}, namespace)
        return result
    except Exception as e:
        raise ValueError(f"Ошибка в выражении: {str(e)}")

def create_function_from_string(expr_str, var_names):
    """Создает функцию из строки выражения с кэшированием"""
    # Компилируем выражение для ускорения
    compiled = compile(expr_str, '<string>', 'eval')
    
    def func(*args):
        try:
            namespace = {'np': np}
            for var_name, var_value in zip(var_names, args):
                namespace[var_name] = var_value
            return eval(compiled, {"__builtins__": {}}, namespace)
        except Exception as e:
            raise ValueError(f"Ошибка в выражении: {str(e)}")
    return func