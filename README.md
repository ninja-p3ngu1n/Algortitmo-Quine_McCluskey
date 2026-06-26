# 🧮 Minimizador Lógico: Quine-McCluskey Avanzado

Una herramienta profesional, moderna e interactiva para simplificar funciones booleanas mediante el algoritmo de **Quine-McCluskey**. Diseñada con una interfaz "Aero-Glass" y potenciada por Flask en el backend, esta aplicación es capaz de resolver expresiones lógicas complejas, tablas de verdad y analizar circuitos exportados desde Logisim Evolution.

## ✨ Características Principales

- **Diseño Aero-Glass Moderno:** Interfaz intuitiva con modo oscuro, animaciones fluidas y diseño responsivo.
- **Múltiples Métodos de Entrada:**
  - *Calculadora Booleana:* Ingresa expresiones completas (ej: `(A⊕B)·(C+D)'`).
  - *Tabla de Verdad Interactiva:* Selecciona manualmente los minitérminos (1s y 0s) según tus variables.
  - *Soporte Logisim (`.circ`):* Sube tu archivo de circuito lógico de *Logisim Evolution* y la app extraerá la ecuación automáticamente usando un parser topológico interno.
- **Paso a Paso Detallado:** Muestra el proceso matemático completo que el algoritmo de Quine-McCluskey realiza por debajo, desde la obtención de implicantes primos hasta la expresión mínima final.
- **Sin Navegador Molesto:** La aplicación está configurada para abrirse automáticamente como una app nativa en tu navegador predeterminado para una experiencia rápida y sin distracciones.

---

## 🚀 Requisitos Previos

Asegúrate de tener instalado en tu sistema operativo:
- **Python 3.8 o superior**
- **Git** (opcional, para clonar el repositorio)

---

## 🛠️ Instalación y Configuración

El proyecto utiliza un Entorno Virtual (`venv`) para mantener las dependencias aisladas y limpias. Sigue las instrucciones correspondientes a tu sistema operativo.

### 🐧 En Linux / macOS

1. **Clonar o descargar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/Algoritmo-Quine_McCluskey.git
   cd Algoritmo-Quine_McCluskey
   ```

2. **Crear el Entorno Virtual:**
   ```bash
   python3 -m venv venv
   ```

3. **Activar el Entorno Virtual:**
   ```bash
   source venv/bin/activate
   ```

4. **Instalar Dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

### 🪟 En Windows

1. **Clonar o descargar el repositorio:**
   ```cmd
   git clone https://github.com/tu-usuario/Algoritmo-Quine_McCluskey.git
   cd Algoritmo-Quine_McCluskey
   ```

2. **Crear el Entorno Virtual:**
   ```cmd
   python -m venv venv
   ```

3. **Activar el Entorno Virtual:**
   ```cmd
   venv\Scripts\activate
   ```

4. **Instalar Dependencias:**
   ```cmd
   pip install -r requirements.txt
   ```

---

## 💻 Ejecución de la Aplicación

Una vez que tengas el entorno virtual activado y las dependencias instaladas, ejecutar la app es idéntico en cualquier sistema:

```bash
python app.py
```

Al ejecutar este comando:
1. El servidor Flask se iniciará internamente en el puerto `5000`.
2. Tu navegador web predeterminado se abrirá **automáticamente** en `http://127.0.0.1:5000/`.
3. ¡Disfruta minimizando circuitos!

*(Para detener el servidor, simplemente presiona `CTRL + C` en tu terminal).*

---

## 🧩 Notas sobre las Expresiones Booleanas

El motor lógico de la app es muy flexible. Puedes utilizar las siguientes nomenclaturas en la Calculadora Booleana:
- **Suma Lógica (OR):** `+` o `OR`
- **Producto Lógico (AND):** `·` , `*` o simplemente omitirlo (`AB` = `A AND B`)
- **Negación (NOT):** `'` (comilla simple), `~` o `NOT` (ej: `A'` o `~A`)
- **XOR:** `⊕` o `XOR`

*Se soportan operaciones anidadas completas como:* `~(A+B)C + AB'C'D`

---

## 📜 Licencia

Desarrollado para facilitar el aprendizaje y resolución de álgebra booleana en diseño de circuitos digitales. Siéntete libre de clonarlo, modificarlo y adaptarlo a tus necesidades.
