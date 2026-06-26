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
    const btnToggleSteps = document.getElementById('btn-toggle-steps');
    const stepsSidebar = document.getElementById('steps-sidebar');
    const stepsContent = document.getElementById('steps-content');
    const btnCloseSidebar = document.getElementById('btn-close-sidebar');
    
    const circFileInput = document.getElementById('circ-file');
    const btnUploadCirc = document.getElementById('btn-upload-circ');

    const btnModeCalc = document.getElementById('btn-mode-calc');
    const btnModeTable = document.getElementById('btn-mode-table');
    const calcMode = document.getElementById('calculator-mode');
    const tableMode = document.getElementById('table-mode');

    const tableHead = document.getElementById('table-head');
    const tableBody = document.getElementById('table-body');
    const btnClear = document.getElementById('btn-clear');
    const btnMinimizeTable = document.getElementById('btn-minimize-table');

    let numVars = 3;
    let truthTable = [];

    function getVariableNames(n) {
        const vars = [];
        for (let i = 0; i < n; i++) {
            vars.push(String.fromCharCode(65 + i)); // A, B, C...
        }
        return vars;
    }

    function hideResult() {
        resultSection.classList.remove('show');
        btnToggleSteps.style.display = 'none';
        stepsSidebar.classList.remove('open');
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
    
    // Mode switching
    btnModeCalc.addEventListener('click', () => {
        btnModeCalc.classList.add('active');
        btnModeTable.classList.remove('active');
        calcMode.style.display = 'block';
        tableMode.style.display = 'none';
        hideResult();
    });

    btnModeTable.addEventListener('click', () => {
        btnModeTable.classList.add('active');
        btnModeCalc.classList.remove('active');
        calcMode.style.display = 'none';
        tableMode.style.display = 'block';
        hideResult();
    });

    function initTable() {
        const rows = Math.pow(2, numVars);
        truthTable = new Array(rows).fill(0);
        renderTable();
    }

    function renderTable() {
        // Render Header
        tableHead.innerHTML = '';
        const vars = getVariableNames(numVars);
        vars.forEach(v => {
            const th = document.createElement('th');
            th.textContent = v;
            tableHead.appendChild(th);
        });
        const outTh = document.createElement('th');
        outTh.textContent = 'F';
        tableHead.appendChild(outTh);

        // Render Body
        tableBody.innerHTML = '';
        const rows = Math.pow(2, numVars);
        for (let i = 0; i < rows; i++) {
            const tr = document.createElement('tr');
            
            // Binary representation
            const binStr = i.toString(2).padStart(numVars, '0');
            for (let j = 0; j < numVars; j++) {
                const td = document.createElement('td');
                td.textContent = binStr[j];
                tr.appendChild(td);
            }

            // Output
            const outTd = document.createElement('td');
            const outSpan = document.createElement('span');
            outSpan.className = `output-cell ${truthTable[i] === 1 ? 'active' : ''}`;
            outSpan.textContent = truthTable[i];
            
            // Interaction to toggle output
            outSpan.addEventListener('click', () => {
                truthTable[i] = truthTable[i] === 1 ? 0 : 1;
                outSpan.textContent = truthTable[i];
                if(truthTable[i] === 1) {
                    outSpan.classList.add('active');
                } else {
                    outSpan.classList.remove('active');
                }
                hideResult();
            });

            outTd.appendChild(outSpan);
            tr.appendChild(outTd);
            tableBody.appendChild(tr);
        }
    }

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

    btnToggleSteps.addEventListener('click', () => {
        stepsSidebar.classList.add('open');
    });

    btnCloseSidebar.addEventListener('click', () => {
        stepsSidebar.classList.remove('open');
    });
    
    btnUploadCirc.addEventListener('click', () => {
        circFileInput.click();
    });
    
    circFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        btnUploadCirc.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
        btnUploadCirc.disabled = true;
        
        try {
            const response = await fetch('/api/upload-circ', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (response.ok) {
                boolExprInput.value = data.expression;
                // Opcional: autoevaluar
                // btnEvalExpr.click();
            } else {
                showResult(`<span style="color: var(--danger); font-size: 0.9rem; line-height: 1.2;">Error: ${data.error}</span>`);
            }
        } catch (error) {
            showResult(`<span style="color: var(--danger); font-size: 0.9rem;">Error de conexión al procesar el archivo.</span>`);
        } finally {
            btnUploadCirc.innerHTML = '<i class="fa-solid fa-file-import"></i>';
            btnUploadCirc.disabled = false;
            circFileInput.value = '';
        }
    });

    btnEvalExpr.addEventListener('click', async () => {
        const expression = boolExprInput.value.trim();
        if (!expression) return;

        const originalText = btnEvalExpr.innerHTML;
        btnEvalExpr.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
        btnEvalExpr.disabled = true;
        hideResult();

        try {
            const response = await fetch('/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expression: expression, num_vars: numVars })
            });

            const data = await response.json();
            
            if (response.ok) {
                showResult(data.expression);
                stepsContent.innerHTML = data.steps_html;
                btnToggleSteps.style.display = 'block';
                
                // Trigger MathJax to typeset the new content
                if (window.MathJax) {
                    MathJax.typesetPromise([stepsContent]).catch(function (err) {
                        console.error('MathJax error: ', err.message);
                    });
                }
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

    btnClear.addEventListener('click', () => {
        truthTable.fill(0);
        const cells = document.querySelectorAll('.output-cell');
        cells.forEach(cell => {
            cell.textContent = '0';
            cell.classList.remove('active');
        });
        hideResult();
    });

    btnMinimizeTable.addEventListener('click', async () => {
        const minterms = [];
        for (let i = 0; i < truthTable.length; i++) {
            if (truthTable[i] === 1) {
                minterms.push(i);
            }
        }

        const originalText = btnMinimizeTable.innerHTML;
        btnMinimizeTable.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Minimizando...';
        btnMinimizeTable.disabled = true;
        hideResult();

        try {
            const response = await fetch('/api/minimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ minterms: minterms, num_vars: numVars })
            });

            const data = await response.json();
            
            if (response.ok) {
                showResult(data.expression);
                stepsContent.innerHTML = data.steps_html;
                btnToggleSteps.style.display = 'block';
                
                if (window.MathJax) {
                    MathJax.typesetPromise([stepsContent]).catch(function (err) {
                        console.error('MathJax error: ', err.message);
                    });
                }
            } else {
                showResult(`<span style="color: var(--danger); font-size: 0.9rem; line-height: 1.2;">Error: ${data.error}</span>`);
            }
        } catch (error) {
            showResult(`<span style="color: var(--danger); font-size: 0.9rem;">Error de conexión</span>`);
        } finally {
            btnMinimizeTable.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Minimizar';
            btnMinimizeTable.disabled = false;
        }
    });

    // Update btnInc and btnDec to re-render calc buttons
    btnInc.addEventListener('click', () => {
        if (numVars < 10) {
            numVars++;
            numVarsInput.value = numVars;
            initTable();
            initCalculator();
            hideResult();
        }
    });

    btnDec.addEventListener('click', () => {
        if (numVars > 2) {
            numVars--;
            numVarsInput.value = numVars;
            initTable();
            initCalculator();
            hideResult();
        }
    });

    // Initialize the app
    initTable();
    initCalculator();
});
