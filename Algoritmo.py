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