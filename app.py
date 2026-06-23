from flask import Flask, request, jsonify, render_template
import Algoritmo

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/minimize', methods=['POST'])
def minimize():
    data = request.json
    minterms = data.get('minterms', [])
    num_vars = data.get('num_vars', 0)
    
    if not minterms:
        return jsonify({'error': 'No minterms provided', 'expression': '0'})
    
    try:
        minterms = [int(m) for m in minterms]
        expression = Algoritmo.solve_quine_mccluskey(minterms, num_vars)
        return jsonify({'expression': expression})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    expression = data.get('expression', '')
    num_vars = data.get('num_vars', 3)
    
    if not expression:
        return jsonify({'error': 'Expresión vacía'}), 400
        
    try:
        # Normalizar expresión
        expr = expression.upper()
        
        # 1. Convertir operadores en palabras a minúsculas para que no interfieran con las variables A-Z
        import re
        expr = re.sub(r'\bAND\b', ' and ', expr)
        expr = re.sub(r'\bOR\b', ' or ', expr)
        expr = re.sub(r'\bNOT\b', ' not ', expr)
        expr = re.sub(r'\bXOR\b', ' ^ ', expr)
        
        # 2. Manejar la yuxtaposición (ej: AB -> A and B, A(B) -> A and (B), A'B -> A' and B)
        # Inserta ' and ' entre [A-Z, ), '] y [A-Z, (, ~, !] ignorando espacios
        expr = re.sub(r'([A-Z\)\'])\s*(?=[A-Z\(~!])', r'\1 and ', expr)
        
        # 3. Símbolos matemáticos de álgebra booleana
        expr = expr.replace('*', ' and ')
        expr = expr.replace('·', ' and ')
        expr = expr.replace('+', ' or ')
        expr = expr.replace('⊕', ' ^ ')
        expr = expr.replace('~', ' not ')
        expr = expr.replace('!', ' not ')
        
        # 4. Reemplazar comillas simples (A') por not A
        expr = re.sub(r'([A-Z])\'', r'not \1', expr)
        
        # Para que 'and', 'or', 'not' funcionen bien en eval
        expr = expr.lower()
        
        minterms = []
        
        for i in range(2**num_vars):
            bin_str = bin(i)[2:].zfill(num_vars)
            env = {}
            for j in range(num_vars):
                var_name = chr(65 + j).lower()
                env[var_name] = bool(int(bin_str[j]))
                
            try:
                res = eval(expr, {"__builtins__": {}}, env)
            except SyntaxError:
                raise Exception("Sintaxis incorrecta. Revisa paréntesis sueltos, operadores incompletos o asegúrate de que el NOT (') solo esté después de letras como A' y no en paréntesis.")
            except NameError as name_err:
                raise Exception(f"Variable no reconocida: {name_err}")
            except Exception:
                raise Exception("Error evaluando la expresión. Verifica que los operadores como · o + estén colocados correctamente.")
                
            val = 1 if res else 0
            if val == 1:
                minterms.append(i)
                
        # También calculamos la minimización de una vez
        expression_min = Algoritmo.solve_quine_mccluskey(minterms, num_vars) if minterms else '0'
        
        return jsonify({
            'expression': expression_min
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
