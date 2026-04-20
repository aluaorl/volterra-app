import re
import numpy as np

# Словарь синонимов функций (в нижнем регистре)
FUNCTION_SYNONYMS = {
    # Обратные тригонометрические (арксинусы)
    'arcsin': 'np.arcsin',
    'asin': 'np.arcsin',
    'arsin': 'np.arcsin',
    
    'arccos': 'np.arccos',
    'acos': 'np.arccos',
    'arcos': 'np.arccos',
    
    'arctan': 'np.arctan',
    'atan': 'np.arctan',
    'arctg': 'np.arctan',
    'atg': 'np.arctan',
    
    'arccot': 'arccot',
    'arcctg': 'arccot',
    'acot': 'arccot',
    'actg': 'arccot',
    
    'arcsec': 'arcsec',
    'asec': 'arcsec',
    
    'arccsc': 'arccsc',
    'acsc': 'arccsc',
    'arccosec': 'arccsc',
    
    # Тригонометрические
    'sin': 'np.sin',
    'cos': 'np.cos',
    'tan': 'np.tan',
    'tg': 'np.tan',
    'cot': '1/np.tan',
    'ctg': '1/np.tan',
    'sec': '1/np.cos',
    'csc': '1/np.sin',
    'cosec': '1/np.sin',
    
    # Гиперболические
    'sinh': 'np.sinh',
    'sh': 'np.sinh',
    'cosh': 'np.cosh',
    'ch': 'np.cosh',
    'tanh': 'np.tanh',
    'th': 'np.tanh',
    'coth': '1/np.tanh',
    'cth': '1/np.tanh',
    'sech': '1/np.cosh',
    'sch': '1/np.cosh',
    'csch': '1/np.sinh',
    'cosech': '1/np.sinh',
    
    # Обратные гиперболические
    'arsinh': 'np.arcsinh',
    'asinh': 'np.arcsinh',
    'arsh': 'np.arcsinh',
    'arcsinh': 'np.arcsinh',
    
    'arcosh': 'np.arccosh',
    'acosh': 'np.arccosh',
    'arch': 'np.arccosh',
    'arccosh': 'np.arccosh',
    
    'artanh': 'np.arctanh',
    'atanh': 'np.arctanh',
    'arth': 'np.arctanh',
    'arctanh': 'np.arctanh',
    
    'arcoth': 'arcoth',
    'acoth': 'arcoth',
    'arcth': 'arcoth',
    
    'arsech': 'arsech',
    'asech': 'arsech',
    'arsch': 'arsech',
    
    'arcsch': 'arcsch',
    'acsch': 'arcsch',
    'arcosech': 'arcsch',
    
    # Логарифмы
    'ln': 'np.log',
    'lg': 'np.log10',
    'log2': 'np.log2',
    'log10': 'np.log10',
    'log': 'np.log',
    
    # Экспонента и корни
    'exp': 'np.exp',
    'sqrt': 'np.sqrt',
    'abs': 'np.abs',
}

# Константы (в нижнем регистре)
CONSTANTS = {
    'pi': 'np.pi',
    'π': 'np.pi',
    'e': 'np.e',
}

# Греческие буквы для отображения
GREEK_LETTERS = {
    'alpha': 'α',
    'beta': 'β',
    'gamma': 'γ',
    'delta': 'δ',
    'epsilon': 'ε',
    'zeta': 'ζ',
    'eta': 'η',
    'theta': 'θ',
    'iota': 'ι',
    'kappa': 'κ',
    'lambda': 'λ',
    'mu': 'μ',
    'nu': 'ν',
    'xi': 'ξ',
    'omicron': 'ο',
    'pi': 'π',
    'rho': 'ρ',
    'sigma': 'σ',
    'tau': 'τ',
    'upsilon': 'υ',
    'phi': 'φ',
    'chi': 'χ',
    'psi': 'ψ',
    'omega': 'ω',
}

def normalize_case(expr):
    """Приводит выражение к нижнему регистру, но сохраняет переменные x и t в исходном виде"""
    expr = re.sub(r'\bx\b', '___VAR_X___', expr, flags=re.IGNORECASE)
    expr = re.sub(r'\bt\b', '___VAR_T___', expr, flags=re.IGNORECASE)
    expr = expr.lower()
    expr = expr.replace('___var_x___', 'x')
    expr = expr.replace('___var_t___', 't')
    return expr

def is_already_parsed(expr):
    """Проверяет, не было ли выражение уже в формате np.*"""
    if 'np.' not in expr:
        return False
    compact = re.sub(r'\s+', '', expr)
    compact_lower = compact.lower()
    for func in FUNCTION_SYNONYMS.keys():
        if re.search(r'(?<!np\.)\b' + re.escape(func) + r'\b', compact_lower):
            return False
    return True

def preprocess_expression(expr):
    """Предобработка выражения: удаление пробелов, добавление * где нужно"""
    expr = re.sub(r'\s+', '', expr)
    expr = re.sub(r'(\d+\.\d+)', r'__FLOAT_\1__', expr)
    expr = re.sub(r'(\d+)([a-zA-Zα-ω])', r'\1*\2', expr)
    expr = re.sub(r'([a-zA-Zα-ω])(\d+)', r'\1*\2', expr)
    expr = re.sub(r'(\d+)\(', r'\1*(', expr)
    expr = re.sub(r'([a-zA-Zα-ω])\(', lambda m: m.group(1) + '(', expr)
    expr = re.sub(r'\)\(', r')*(', expr)
    expr = re.sub(r'__FLOAT_(\d+\.\d+)__', r'\1', expr)
    return expr

def process_power_after_function(expr):
    """Обработка возведения функции в степень: sin(x)^2 -> (sin(x))**2"""
    # Ищем pattern: функция(аргумент)^степень
    # Например: sin(x)^2, cos(x)^3, exp(-x)^2 и т.д.
    pattern = r'([a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\))\s*\^\s*([0-9]+(?:\.[0-9]+)?)'
    
    def replace_power(match):
        func_call = match.group(1)
        power = match.group(2)
        return f'({func_call})**{power}'
    
    expr = re.sub(pattern, replace_power, expr)
    
    # Также обрабатываем случай, когда степень после скобок с выражением: (x+1)^2
    pattern2 = r'\(([^)]+)\)\s*\^\s*([0-9]+(?:\.[0-9]+)?)'
    
    def replace_power2(match):
        inner = match.group(1)
        power = match.group(2)
        return f'({inner})**{power}'
    
    expr = re.sub(pattern2, replace_power2, expr)
    
    return expr

def process_sqrt(expr):
    """Обработка sqrt(n, x) - корень n-ой степени"""
    # Обработка sqrt(3, x) или sqrt(3,x)
    pattern = r'sqrt\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)'
    
    def replace_sqrt(match):
        n = match.group(1)
        x = match.group(2)
        return f'(({x})**(1/({n})))'
    
    expr = re.sub(pattern, replace_sqrt, expr)
    
    # Обычный sqrt(x) - квадратный корень
    expr = re.sub(r'sqrt\s*\(\s*([^)]+)\s*\)', r'np.sqrt(\1)', expr)
    
    return expr

def safe_eval_with_checks(expr, namespace, test_value=0.5):
    """Безопасное вычисление выражения с проверкой на математические ошибки"""
    try:
        result = eval(expr, {"__builtins__": {}}, namespace)
        
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
        if "division by zero" in error_msg or "divide by zero" in error_msg:
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
                raise ValueError(f"Неизвестная функция '{func_name}'")
            raise ValueError("Неизвестная функция или переменная")
        else:
            raise ValueError("Некорректное математическое выражение")

def validate_expression_detailed(expr_str, variables=['x', 't']):
    """Подробная валидация выражения с возвратом понятного сообщения"""
    if not expr_str or expr_str.strip() == '':
        return False, "Поле не может быть пустым"
    
    try:
        expr = normalize_case(expr_str)
        
        # Если выражение уже в формате np.*
        if is_already_parsed(expr):
            test_namespace = {'np': np}
            for var in variables:
                test_namespace[var] = 0.5
            for test_val in [0.1, 0.3, 0.5, 0.7, 0.9]:
                for var in variables:
                    test_namespace[var] = test_val
                safe_eval_with_checks(expr, test_namespace, test_val)
            return True, ""
        
        # Предобработка
        expr = preprocess_expression(expr)
        
        # Обработка степени после функций (ДО замены функций)
        expr = process_power_after_function(expr)
        
        # Обработка e^
        expr = re.sub(r'e\^\(([^)]+)\)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^([a-zA-Z0-9α-ω]+)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^\(-([^)]+)\)', r'np.exp(-\1)', expr)
        
        # Обработка sqrt (должна быть до замены функций)
        expr = process_sqrt(expr)
        
        # Замена функций
        for func_name, np_func in FUNCTION_SYNONYMS.items():
            pattern = r'(?<!np\.)\b' + re.escape(func_name) + r'\s*\('
            
            if np_func in ['1/np.tan', '1/np.cosh', '1/np.sinh', '1/np.tanh']:
                expr = re.sub(pattern, np_func + '(', expr)
            elif func_name in ['arcsec', 'asec']:
                expr = re.sub(pattern, r'np.arccos(1/', expr)
            elif func_name in ['arccsc', 'acsc', 'arccosec']:
                expr = re.sub(pattern, r'np.arcsin(1/', expr)
            elif func_name in ['arccot', 'arcctg', 'acot', 'actg']:
                expr = re.sub(pattern, r'np.arctan(1/', expr)
            elif func_name in ['arcoth', 'acoth', 'arcth']:
                expr = re.sub(pattern, r'np.arctanh(1/', expr)
            elif func_name in ['arsech', 'asech', 'arsch']:
                expr = re.sub(pattern, r'np.arccosh(1/', expr)
            elif func_name in ['arcsch', 'acsch', 'arcosech']:
                expr = re.sub(pattern, r'np.arcsinh(1/', expr)
            else:
                expr = re.sub(pattern, np_func + '(', expr)
        
        # Замена констант
        for const, replacement in CONSTANTS.items():
            expr = re.sub(r'\b' + re.escape(const) + r'\b', replacement, expr)
        
        # Обработка степени
        expr = re.sub(r'([a-zA-Z0-9α-ω\(\)]+)\^([a-zA-Z0-9α-ω\(\)]+)', r'(\1)**(\2)', expr)
        
        expr = re.sub(r'\s+', '', expr)
        
        # Проверка скобок
        if expr.count('(') != expr.count(')'):
            return False, "Несбалансированные скобки"
        
        # Пробуем скомпилировать
        try:
            compile(expr, '<string>', 'eval')
        except SyntaxError as e:
            error_msg = str(e)
            if "unexpected EOF" in error_msg:
                return False, "Незавершенное выражение"
            elif "invalid syntax" in error_msg:
                return False, "Некорректный синтаксис выражения"
            else:
                return False, "Ошибка в синтаксисе выражения"
        
        # Тестируем вычисление в нескольких точках
        test_namespace = {'np': np}
        test_points = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for test_val in test_points:
            for var in variables:
                test_namespace[var] = test_val
            try:
                safe_eval_with_checks(expr, test_namespace, test_val)
            except ValueError as e:
                return False, str(e)
        
        return True, ""
        
    except SyntaxError as e:
        error_msg = str(e)
        if "unexpected EOF" in error_msg:
            return False, "Незавершенное выражение"
        elif "invalid syntax" in error_msg:
            return False, "Некорректный синтаксис выражения"
        else:
            return False, "Ошибка в синтаксисе выражения"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        error_msg = str(e).lower()
        if "division by zero" in error_msg:
            return False, "Обнаружено деление на ноль"
        elif "name" in error_msg and "is not defined" in error_msg:
            return False, "Неизвестная функция или переменная"
        else:
            return False, "Некорректное математическое выражение"

def parse_user_input(expr_str, variables=['x', 't']):
    """Основная функция парсинга пользовательского ввода"""
    if not expr_str or expr_str.strip() == '':
        raise ValueError("Выражение не может быть пустым")
    
    expr = normalize_case(expr_str)
    
    if is_already_parsed(expr):
        test_namespace = {'np': np}
        for var in variables:
            test_namespace[var] = 0.5
        test_points = [0.1, 0.3, 0.5, 0.7, 0.9]
        for test_val in test_points:
            for var in variables:
                test_namespace[var] = test_val
            safe_eval_with_checks(expr, test_namespace, test_val)
        return expr
    
    try:
        expr = preprocess_expression(expr)
        
        # Обработка степени после функций (ДО замены функций)
        expr = process_power_after_function(expr)
        
        expr = re.sub(r'e\^\(([^)]+)\)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^([a-zA-Z0-9α-ω]+)', r'np.exp(\1)', expr)
        expr = re.sub(r'e\^\(-([^)]+)\)', r'np.exp(-\1)', expr)
        
        # Обработка sqrt (должна быть до замены функций)
        expr = process_sqrt(expr)
        
        # Замена функций
        for func_name, np_func in FUNCTION_SYNONYMS.items():
            pattern = r'(?<!np\.)\b' + re.escape(func_name) + r'\s*\('
            
            if np_func in ['1/np.tan', '1/np.cosh', '1/np.sinh', '1/np.tanh']:
                expr = re.sub(pattern, np_func + '(', expr)
            elif func_name in ['arcsec', 'asec']:
                expr = re.sub(pattern, r'np.arccos(1/', expr)
            elif func_name in ['arccsc', 'acsc', 'arccosec']:
                expr = re.sub(pattern, r'np.arcsin(1/', expr)
            elif func_name in ['arccot', 'arcctg', 'acot', 'actg']:
                expr = re.sub(pattern, r'np.arctan(1/', expr)
            elif func_name in ['arcoth', 'acoth', 'arcth']:
                expr = re.sub(pattern, r'np.arctanh(1/', expr)
            elif func_name in ['arsech', 'asech', 'arsch']:
                expr = re.sub(pattern, r'np.arccosh(1/', expr)
            elif func_name in ['arcsch', 'acsch', 'arcosech']:
                expr = re.sub(pattern, r'np.arcsinh(1/', expr)
            else:
                expr = re.sub(pattern, np_func + '(', expr)
        
        # Замена констант
        for const, replacement in CONSTANTS.items():
            expr = re.sub(r'\b' + re.escape(const) + r'\b', replacement, expr)
        
        expr = re.sub(r'([a-zA-Z0-9α-ω\(\)]+)\^([a-zA-Z0-9α-ω\(\)]+)', r'(\1)**(\2)', expr)
        expr = re.sub(r'np\.arctan\(1/([^)]+)\)', r'np.arctan(1/\1)', expr)
        expr = re.sub(r'1/np\.tan\(', r'np.tan(', expr)
        expr = re.sub(r'\s+', '', expr)
        
        if expr.count('(') != expr.count(')'):
            raise ValueError("Несбалансированные скобки")
        
        test_namespace = {'np': np}
        for var in variables:
            test_namespace[var] = 0.5
        
        compile(expr, '<string>', 'eval')
        
        test_points = [0.1, 0.3, 0.5, 0.7, 0.9]
        for test_val in test_points:
            for var in variables:
                test_namespace[var] = test_val
            safe_eval_with_checks(expr, test_namespace, test_val)
        
        return expr
        
    except Exception as e:
        raise ValueError(str(e))

def format_for_display(expr, is_kernel=True):
    """Форматирование выражения для красивого отображения"""
    result = expr.replace('np.', '')
    result = result.replace('**', '^')
    result = re.sub(r'exp\(([^)]+)\)', r'e^{\1}', result)
    
    for eng, gr in GREEK_LETTERS.items():
        result = result.replace(eng, gr)
    
    result = result.replace('1/tan', 'cot')
    result = result.replace('arctan(1/', 'arcctg(')
    
    if is_kernel:
        return f"K(x,t) = {result}"
    else:
        return f"f(x) = {result}"

def validate_expression(expr_str, variables=['x', 't']):
    """Валидация выражения"""
    try:
        parse_user_input(expr_str, variables)
        return True, "Выражение корректно"
    except ValueError as e:
        return False, str(e)