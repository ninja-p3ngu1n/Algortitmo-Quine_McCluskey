def int_to_bin(n, num_vars):
    """Convierte un número entero a su cadena binaria rellenada con ceros."""
    return bin(n)[2:].zfill(num_vars)

def count_ones(binary_str):
    """Cuenta la cantidad de unos en una cadena binaria."""
    return binary_str.count('1')

def combine_terms(term1, term2):
    """
    Compara dos términos binarios. Si difieren en exactamente un bit,
    los combina colocando un '-' en esa posición. Si no, devuelve None.
    """
    diff_count = 0
    combined = []
    for b1, b2 in zip(term1, term2):
        if b1 != b2:
            diff_count += 1
            combined.append('-')
        else:
            combined.append(b1)
    return "".join(combined) if diff_count == 1 else None

def get_prime_implicants(minterms, num_vars):
    """Paso 1 y 2: Agrupación por número de unos y obtención de Implicantes Primos."""
    # Agrupar los minitérminos originales por su cantidad de '1s'
    current_groups = {}
    for m in minterms:
        b_str = int_to_bin(m, num_vars)
        ones = count_ones(b_str)
        if ones not in current_groups:
            current_groups[ones] = set()
        current_groups[ones].add(b_str)
    
    prime_implicants = set()
    
    while current_groups:
        next_groups = {}
        marked = set()
        keys = sorted(current_groups.keys())
        
        # Comparar grupos adyacentes para intentar combinarlos
        for i in range(len(keys) - 1):
            g1, g2 = keys[i], keys[i+1]
            if g2 - g1 == 1:
                for t1 in current_groups[g1]:
                    for t2 in current_groups[g2]:
                        combined = combine_terms(t1, t2)
                        if combined:
                            marked.add(t1)
                            marked.add(t2)
                            ones = count_ones(combined.replace('-', ''))
                            if ones not in next_groups:
                                next_groups[ones] = set()
                            next_groups[ones].add(combined)
                            
        # Los términos que NO se pudieron combinar se guardan como implicantes primos
        for g in current_groups.values():
            for term in g:
                if term not in marked:
                    prime_implicants.add(term)
                    
        current_groups = next_groups
        
    return list(prime_implicants)

def matches(minterm_bin, implicant):
    """Determina si un minitérmino en binario es cubierto por un implicante (ignorando los '-')."""
    for b, imp in zip(minterm_bin, implicant):
        if imp != '-' and b != imp:
            return False
    return True

def select_essential_prime_implicants(prime_implicants, minterms, num_vars):
    """Paso 3: Selección de Implicantes Primos Esenciales usando la tabla de cobertura."""
    minterms_bin = [int_to_bin(m, num_vars) for m in minterms]
    essential_pi = []
    remaining_minterms = list(minterms)
    
    while remaining_minterms:
        current_minterms_bin = [int_to_bin(m, num_vars) for m in remaining_minterms]
        
        # Contar cuántas veces es cubierto cada minitérmino restante por los implicantes
        cover_counts = [0] * len(remaining_minterms)
        for pi in prime_implicants:
            for idx, m_bin in enumerate(current_minterms_bin):
                if matches(m_bin, pi):
                    cover_counts[idx] += 1
                    
        essential_found = False
        # Buscar minitérminos que solo tengan una sola cobertura (esenciales puros)
        for idx, count in enumerate(cover_counts):
            if count == 1:
                m_bin = current_minterms_bin[idx]
                for pi in prime_implicants:
                    if matches(m_bin, pi) and pi not in essential_pi:
                        essential_pi.append(pi)
                        # Remover minitérminos ya cubiertos
                        remaining_minterms = [m for m in remaining_minterms if not matches(int_to_bin(m, num_vars), pi)]
                        essential_found = True
                        break
            if essential_found: 
                break
        
        # Si no quedan esenciales puros pero aún hay minitérminos por cubrir (Cíclico),
        # seleccionamos de forma codiciosa el implicante que cubra más cantidad de términos restantes.
        if not essential_found:
            if not prime_implicants:
                break
            best_pi = max(prime_implicants, key=lambda pi: sum(matches(int_to_bin(m, num_vars), pi) for m in remaining_minterms))
            essential_pi.append(best_pi)
            remaining_minterms = [m for m in remaining_minterms if not matches(int_to_bin(m, num_vars), best_pi)]
            if best_pi in prime_implicants:
                prime_implicants.remove(best_pi)

    return essential_pi

def format_expression(implicants):
    """Paso 4: Traduce la forma binaria con guiones a formato algebraico (A, B, C...)."""
    if not implicants:
        return "0"
    
    terms = []
    for imp in implicants:
        term_str = ""
        for i, char in enumerate(imp):
            var_name = chr(65 + i)
            if char == '1':
                term_str += var_name
            elif char == '0':
                term_str += var_name + "'"
        if term_str:
            terms.append(term_str)
    
    return " + ".join(terms) if terms else "1"

def solve_quine_mccluskey(minterms, num_vars):
    # Compatibilidad con la versión sin pasos
    expr, _ = solve_quine_mccluskey_with_steps(minterms, num_vars)
    return expr

def format_term_latex(term, num_vars):
    res = ""
    for i, char in enumerate(term):
        var_name = chr(65 + i)
        if char == '1':
            res += var_name
        elif char == '0':
            res += var_name + "'"
    return res if res else "1"

def solve_quine_mccluskey_with_steps(minterms, num_vars):
    if not minterms:
        return "0", "<p>No hay minitérminos que evaluar, por lo tanto la función es siempre <strong>0</strong>.</p>"
        
    steps = []
    steps.append("<h3>Paso 1: Minitérminos Identificados</h3>")
    steps.append("<p>Se evalúa la expresión para encontrar los casos donde la función es verdadera (1). Los minitérminos encontrados son:</p>")
    m_list = ", ".join([f"m_{{{m}}}" for m in minterms])
    steps.append(f"\\[ \\sum m({m_list}) \\]")
    
    # Agrupar
    current_groups = {}
    for m in minterms:
        b_str = int_to_bin(m, num_vars)
        ones = count_ones(b_str)
        if ones not in current_groups:
            current_groups[ones] = set()
        current_groups[ones].add(b_str)
        
    steps.append("<h3>Paso 2: Agrupación por cantidad de unos</h3>")
    steps.append("<p>Se agrupan los minitérminos según la cantidad de bits '1' que contienen:</p>")
    steps.append("<ul>")
    for k in sorted(current_groups.keys()):
        terms = ", ".join(current_groups[k])
        steps.append(f"<li>Grupo con {k} unos: \\( \\{{ {terms} \\}} \\)</li>")
    steps.append("</ul>")
    
    prime_implicants = set()
    step_num = 1
    
    while current_groups:
        next_groups = {}
        marked = set()
        keys = sorted(current_groups.keys())
        combined_any = False
        
        for i in range(len(keys) - 1):
            g1, g2 = keys[i], keys[i+1]
            if g2 - g1 == 1:
                for t1 in current_groups[g1]:
                    for t2 in current_groups[g2]:
                        combined = combine_terms(t1, t2)
                        if combined:
                            marked.add(t1)
                            marked.add(t2)
                            ones = count_ones(combined.replace('-', ''))
                            if ones not in next_groups:
                                next_groups[ones] = set()
                            next_groups[ones].add(combined)
                            combined_any = True
                            
        for g in current_groups.values():
            for term in g:
                if term not in marked:
                    prime_implicants.add(term)
                    
        if combined_any:
            steps.append(f"<h3>Paso 2.{step_num}: Combinación de grupos adyacentes</h3>")
            steps.append("<p>Se combinan los términos que difieren en un solo bit (se reemplaza por '-'):</p>")
            steps.append("<ul>")
            for k in sorted(next_groups.keys()):
                terms = ", ".join(next_groups[k])
                steps.append(f"<li>Grupo con {k} unos: \\( \\{{ {terms} \\}} \\)</li>")
            steps.append("</ul>")
            
        current_groups = next_groups
        step_num += 1
        
    steps.append("<h3>Paso 3: Implicantes Primos</h3>")
    pi_list = ", ".join(prime_implicants)
    steps.append(f"<p>Los implicantes primos que no se pudieron combinar más son:</p>\\[ \\{{ {pi_list} \\}} \\]")
    
    # Essential PI
    essential_pi = []
    remaining_minterms = list(minterms)
    
    steps.append("<h3>Paso 4: Tabla de Implicantes Primos Esenciales</h3>")
    steps.append("<p>Buscamos qué implicantes cubren minitérminos que ningún otro cubre.</p>")
    
    while remaining_minterms:
        current_minterms_bin = [int_to_bin(m, num_vars) for m in remaining_minterms]
        cover_counts = [0] * len(remaining_minterms)
        for pi in prime_implicants:
            for idx, m_bin in enumerate(current_minterms_bin):
                if matches(m_bin, pi):
                    cover_counts[idx] += 1
                    
        essential_found = False
        for idx, count in enumerate(cover_counts):
            if count == 1:
                m_bin = current_minterms_bin[idx]
                for pi in prime_implicants:
                    if matches(m_bin, pi) and pi not in essential_pi:
                        essential_pi.append(pi)
                        steps.append(f"<p>Minitérmino \\( m_{{{int(m_bin, 2)}}} \\) ({m_bin}) solo es cubierto por <strong>{pi}</strong>. Se selecciona como esencial.</p>")
                        remaining_minterms = [m for m in remaining_minterms if not matches(int_to_bin(m, num_vars), pi)]
                        essential_found = True
                        break
            if essential_found: 
                break
                
        if not essential_found:
            if not prime_implicants:
                break
            best_pi = max(prime_implicants, key=lambda pi: sum(matches(int_to_bin(m, num_vars), pi) for m in remaining_minterms))
            essential_pi.append(best_pi)
            steps.append(f"<p>Por cobertura cíclica, se selecciona el implicante <strong>{best_pi}</strong> porque cubre más minitérminos restantes.</p>")
            remaining_minterms = [m for m in remaining_minterms if not matches(int_to_bin(m, num_vars), best_pi)]
            if best_pi in prime_implicants:
                prime_implicants.remove(best_pi)
                
    steps.append("<h3>Paso 5: Traducción a Álgebra Booleana</h3>")
    steps.append("<p>Convertimos los implicantes seleccionados de vuelta a variables:</p>")
    steps.append("<ul>")
    for epi in essential_pi:
        latex_term = format_term_latex(epi, num_vars)
        steps.append(f"<li>{epi} \\(\\rightarrow {latex_term}\\)</li>")
    steps.append("</ul>")
    
    final_expr = format_expression(essential_pi)
    steps.append(f"<h3>Resultado Final</h3>\\[ F = {final_expr.replace('+', ' + ')} \\]")
    
    return final_expr, "\n".join(steps)