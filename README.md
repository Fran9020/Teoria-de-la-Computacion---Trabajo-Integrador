# SART-V — Sistema Automatizado de Reconocimiento Topológico Vascular

## Descripción

**SART-V** es un analizador léxico y sintáctico diseñado para reconocer y validar cadenas que representan **redes vasculares** modeladas mediante **Gramáticas Libres de Contexto (GLC)**, inspiradas en los **L-Systems (Gramáticas de Lindenmayer)**.

El programa forma parte del trabajo integrador de la materia **Teoría de la Computación** y aborda el tema *"Modelado Fractal de Patologías Vasculares mediante Gramáticas de Lindenmayer"*. Su objetivo es demostrar cómo los conceptos formales de la teoría de lenguajes (alfabetos, gramáticas, autómatas) se pueden aplicar a un dominio biomédico concreto: la representación de estructuras vasculares sanas y patológicas (tumorales).

---

## ¿Para qué sirve?

El sistema permite:

1. **Validar** si una cadena de entrada pertenece al lenguaje formal definido por la gramática GLC del sistema vascular.
2. **Analizar léxicamente** la cadena, descomponiéndola en tokens según el alfabeto Σ.
3. **Analizar sintácticamente** la secuencia de tokens, construyendo un **Árbol Sintáctico Abstracto (AST)** que representa la estructura jerárquica del vaso sanguíneo.
4. **Visualizar** la red vascular como una imagen fractal en formato **SVG**, donde:
   - El color **verde** indica tejido sano (`V`).
   - El color **rojo** indica tejido patológico/cancerígeno (`C`).

---

## ¿Cómo funciona?

El programa sigue un pipeline de 3 etapas:

### 1. Análisis Léxico (`lexer.py`)

El **Lexer** recibe una cadena de texto y la recorre carácter por carácter, clasificando cada uno según el **alfabeto Σ** del lenguaje:

| Símbolo | Significado            |
|---------|------------------------|
| `F`     | Segmento vascular      |
| `V`     | Tejido sano            |
| `C`     | Tejido patológico      |
| `+`     | Giro a la derecha      |
| `-`     | Giro a la izquierda    |
| `[`     | Inicio de rama         |
| `]`     | Fin de rama            |

Los espacios en blanco son ignorados. Si se encuentra un carácter que no pertenece al alfabeto, se lanza un **error léxico** indicando la línea y columna del carácter inválido.

### 2. Análisis Sintáctico (`parser.py`)

El **Parser** toma la lista de tokens del Lexer y verifica que cumplan con la **Gramática Libre de Contexto** definida:

```
<vaso>   ::= <tronco> "[" <rama> "]" "[" <rama> "]"
<tronco> ::= "F" "F" "F"
<rama>   ::= <giro> "F" <tejido>
           | <giro> "F" <tejido> "[" <rama> "]" "[" <rama> "]"
<giro>   ::= "+" | "-"
<tejido> ::= "V" | "C"
```

Se utiliza la técnica de **Parser Recursivo Descendente** (Recursive Descent Parser), donde cada no-terminal de la gramática se traduce en un método. La gramática es **LL(1)**: las dos alternativas de `<rama>` comparten el prefijo `<giro> F <tejido>`, y la decisión de si hay sub-ramas se toma mirando si el siguiente token es `[` (lookahead de 1 token).

Si la cadena es válida, se construye un **AST** con nodos `Vaso`, `Tronco`, `Rama` y `Tejido`. Si no, se lanza un **error sintáctico** con información de posición.

### 3. Visualización Fractal (`fractal_viz.py`)

Si la cadena es aceptada, el módulo de visualización recorre el AST usando un modelo tipo **turtle graphics** para generar una imagen **SVG**:

- El **tronco** se dibuja como un segmento vertical.
- Cada **rama** gira respecto a la dirección heredada del padre.
- La **longitud** y el **grosor** se reducen en cada nivel de profundidad, generando el efecto de **auto-similitud fractal**.
- Las **hojas** (ramas terminales) se colorean según el tipo de tejido: verde para sano (`V`) y rojo para patológico (`C`).

---

## Estructura del proyecto

```
Teoria-de-la-Computacion---Trabajo-Integrador/
├── README.md                          ← Este archivo
├── Lexer y Parser/
│   ├── lexer.py                       ← Analizador léxico
│   ├── parser.py                      ← Analizador sintáctico + AST
│   ├── fractal_viz.py                 ← Visualización fractal (SVG)
│   ├── main.py                        ← Punto de entrada principal
│   ├── test.py                        ← Suite de pruebas (10 válidos + 10 inválidos)
│   ├── Resultados.txt                 ← Salida de ejemplo del lexer y parser
│   └── salida_1.svg                   ← Ejemplo de visualización generada
├── TC-SMRLP-Modelado Fractal...       ← Documento del trabajo integrador
└── Bitacora de Aprendisaje...         ← Bitácora del proceso de aprendizaje
```

---

## Ejemplos de cadenas

| Cadena                                    | Resultado  | Descripción                                 |
|-------------------------------------------|------------|---------------------------------------------|
| `FFF[+FV][-FV]`                           | ✅ Aceptada | Vaso mínimo, dos ramas sanas                |
| `FFF[+FV][-FC]`                           | ✅ Aceptada | Una rama sana y una patológica              |
| `FFF[+FV[+FV][-FV]][-FC[-FC][+FC]]`      | ✅ Aceptada | Bifurcaciones anidadas (profundidad 2)      |
| `FF[+FV][-FV]`                            | ❌ Rechazada | Tronco incompleto (solo 2 F)               |
| `FFF[+FV]`                                | ❌ Rechazada | Falta la segunda rama                       |
| `FFF[+FX][-FV]`                           | ❌ Rechazada | 'X' no pertenece al alfabeto Σ (error léxico)|

---

## Manual de instalación y ejecución

### Requisitos previos

- **Python 3.10** o superior (se utilizan type hints modernos como `list[Token]`).
- No se requieren dependencias externas (el proyecto usa solo la biblioteca estándar de Python).

### Instalación

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/Fran9020/Teoria-de-la-Computacion---Trabajo-Integrador.git
   cd Teoria-de-la-Computacion---Trabajo-Integrador
   ```

2. **Verificar la versión de Python:**

   ```bash
   python --version
   ```

   Asegurarse de que sea 3.10 o superior.

### Ejecución

Todos los comandos se ejecutan desde la carpeta `Lexer y Parser/`:

```bash
cd "Lexer y Parser"
```

#### Modo interactivo

Ejecutar sin argumentos para ingresar cadenas por consola:

```bash
python main.py
```

Se mostrará un prompt `Cadena>` donde se pueden ingresar cadenas. Escribir `salir` para terminar.

#### Modo por argumento

Pasar la cadena directamente como argumento:

```bash
python main.py "FFF[+FV][-FC]"
```

Opcionalmente, se puede indicar el nombre del archivo SVG de salida:

```bash
python main.py "FFF[+FV][-FC]" mi_vaso.svg
```

#### Ejecutar la suite de pruebas

```bash
python test.py
```

Esto ejecuta 10 casos válidos y 10 casos inválidos, mostrando un resumen al final.

#### Ejecutar el lexer individualmente

```bash
python lexer.py
```

#### Ejecutar el parser individualmente

```bash
python parser.py
```

### Salida esperada

Para una cadena **aceptada**, el programa muestra:

1. Los **tokens** generados por el análisis léxico.
2. El **AST** en formato de árbol de texto con conectores `├──` y `└──`.
3. Un **archivo SVG** con la visualización fractal de la red vascular.

Para una cadena **rechazada**, muestra el tipo de error (léxico o sintáctico) con la línea y columna del problema.

---

## Autores

Trabajo Integrador — Teoría de la Computación  
*Modelado Fractal de Patologías Vasculares mediante Gramáticas de Lindenmayer*
