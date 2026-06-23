document.addEventListener('DOMContentLoaded', () => {
    const numVarsInput = document.getElementById('num-vars');
    const btnInc = document.getElementById('btn-inc');
    const btnDec = document.getElementById('btn-dec');
    const resultSection = document.getElementById('result-section');
    const expressionDisplay = document.getElementById('expression-display');
    const resultCard = document.querySelector('.result-card');
    const calcButtonsContainer = document.getElementById('calc-buttons');
    const boolExprInput = document.getElementById('bool-expr');
    const btnEvalExpr = document.getElementById('btn-eval-expr');

    let numVars = 3;

    function getVariableNames(n) {
        const vars = [];
        for (let i = 0; i < n; i++) {
            vars.push(String.fromCharCode(65 + i)); // A, B, C...
        }
        return vars;
    }

    function hideResult() {
        resultSection.classList.remove('show');
    }

    function showResult(expression) {
        expressionDisplay.innerHTML = expression;
        resultSection.classList.add('show');
        
        // Add flash animation
        resultCard.classList.remove('flash');
        void resultCard.offsetWidth; // trigger reflow
        resultCard.classList.add('flash');
    }

    // Keyboard navigation
    
    function initCalculator() {
        renderCalcButtons();
    }

    function renderCalcButtons() {
        calcButtonsContainer.innerHTML = '';
        const vars = getVariableNames(numVars);
        
        // Add variable buttons
        vars.forEach(v => {
            const btn = document.createElement('button');
            btn.className = 'btn-calc';
            btn.textContent = v;
            btn.addEventListener('click', () => { insertToExpr(v); });
            calcButtonsContainer.appendChild(btn);
        });

        // Add operator buttons
        const ops = ['+', '·', "'", '⊕', '(', ')'];
        ops.forEach(op => {
            const btn = document.createElement('button');
            btn.className = 'btn-calc op';
            btn.textContent = op;
            btn.addEventListener('click', () => { insertToExpr(op); });
            calcButtonsContainer.appendChild(btn);
        });
    }

    function insertToExpr(val) {
        const start = boolExprInput.selectionStart;
        const end = boolExprInput.selectionEnd;
        const text = boolExprInput.value;
        const before = text.substring(0, start);
        const after = text.substring(end, text.length);
        
        let spaceBefore = ' ';
        let spaceAfter = ' ';
        
        if (val === "'" || val === ')') {
            spaceBefore = '';
        }
        if (val === '(' || val === "'") {
            spaceAfter = '';
        }
        if (before.length === 0 || before.endsWith(' ') || before.endsWith('(')) {
            spaceBefore = '';
        }

        boolExprInput.value = before + spaceBefore + val + spaceAfter + after;
        boolExprInput.focus();
        // Adjust cursor
        const newPos = start + spaceBefore.length + val.length + spaceAfter.length;
        boolExprInput.setSelectionRange(newPos, newPos);
    }

    btnEvalExpr.addEventListener('click', async () => {
        const expression = boolExprInput.value.trim();
        if (!expression) return;

        const originalText = btnEvalExpr.innerHTML;
        btnEvalExpr.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
        btnEvalExpr.disabled = true;

        try {
            const response = await fetch('/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expression: expression, num_vars: numVars })
            });

            const data = await response.json();
            
            if (response.ok) {
                showResult(data.expression);
            } else {
                showResult(`<span style="color: var(--danger); font-size: 0.9rem; line-height: 1.2;">Error: ${data.error}</span>`);
            }
        } catch (error) {
            showResult(`<span style="color: var(--danger); font-size: 0.9rem;">Error de conexión</span>`);
        } finally {
            btnEvalExpr.innerHTML = '<i class="fa-solid fa-play"></i> Evaluar';
            btnEvalExpr.disabled = false;
        }
    });

    // Update btnInc and btnDec to re-render calc buttons
    btnInc.addEventListener('click', () => {
        if (numVars < 10) {
            numVars++;
            numVarsInput.value = numVars;
            initCalculator();
            hideResult();
        }
    });

    btnDec.addEventListener('click', () => {
        if (numVars > 2) {
            numVars--;
            numVarsInput.value = numVars;
            initCalculator();
            hideResult();
        }
    });

    // Initialize the app
    initCalculator();
});
