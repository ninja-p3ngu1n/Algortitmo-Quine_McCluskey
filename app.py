from flask import Flask, request, jsonify, render_template
import os
import tempfile
import webbrowser
from threading import Timer
import Algoritmo
import circ_parser

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
        if minterms:
            expression_min, steps_html = Algoritmo.solve_quine_mccluskey_with_steps(minterms, num_vars)
        else:
            expression_min = '0'
            steps_html = '<p>No hay minitérminos que evaluar, por lo tanto la función es siempre <strong>0</strong>.</p>'
            
        return jsonify({
            'expression': expression_min,
            'steps_html': steps_html
        })
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
        
        # 5. Manejar negación de paréntesis con comilla simple ej: (A+B)'
        while re.search(r'\(([^()]*)\)\'', expr):
            expr = re.sub(r'\(([^()]*)\)\'', r'not (\1)', expr)
        
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
        if minterms:
            expression_min, alg_steps = Algoritmo.solve_quine_mccluskey_with_steps(minterms, num_vars)
            
            # Prepend expression evaluation explanation
            eval_steps = ["<h3>Paso 0: Evaluación de la Expresión Booleana</h3>"]
            eval_steps.append(f"<p>Para saber de dónde salen los números (minitérminos), evaluamos tu expresión <strong>{expression}</strong> usando todas las combinaciones posibles de 0s y 1s para las {num_vars} variables.</p>")
            eval_steps.append("<p>Cada combinación que da como resultado <strong>1 (Verdadero)</strong> se anota, y su valor en binario se convierte a un número decimal (el minitérmino).</p>")
            eval_steps.append("<ul>")
            for m in minterms:
                b_str = bin(m)[2:].zfill(num_vars)
                vars_str = ", ".join([f"{chr(65+i)}={b_str[i]}" for i in range(num_vars)])
                eval_steps.append(f"<li>Si {vars_str} \\(\\rightarrow\\) Combinación <strong>{b_str}</strong> en binario = <strong>{m}</strong> en decimal.</li>")
            eval_steps.append("</ul>")
            
            steps_html = "\n".join(eval_steps) + "\n<hr style='border-color: rgba(255,255,255,0.1); margin: 1.5rem 0;'>" + alg_steps
        else:
            expression_min = '0'
            steps_html = '<p>No hay minitérminos que evaluar, por lo tanto la función es siempre <strong>0</strong>.</p>'
        
        return jsonify({
            'expression': expression_min,
            'steps_html': steps_html
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/upload-circ', methods=['POST'])
def upload_circ():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró archivo'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Archivo no seleccionado'}), 400
    if not file.filename.endswith('.circ'):
        return jsonify({'error': 'Debe ser un archivo .circ'}), 400
        
    try:
        # Guardar en un temporal para parsear
        fd, temp_path = tempfile.mkstemp(suffix='.circ')
        os.close(fd)
        file.save(temp_path)
        
        # Parsear
        expr = circ_parser.parse_circ(temp_path)
        os.remove(temp_path)
        
        if not expr:
            return jsonify({'error': 'No se detectó salida o ecuación en el circuito'}), 400
            
        return jsonify({'expression': expr})
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': f'Error al leer el circuito: {str(e)}'}), 400

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Abrir el navegador automáticamente sin tener que copiar el link
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        Timer(1.25, open_browser).start()
        
    app.run(port=5000, debug=True)
