# Aplicación de Mapeo de Funciones Complejas

Una aplicación de escritorio interactiva para visualizar el mapeo de funciones complejas y sus superficies de Riemann equivalentes.

## Características

- **Visualización del plano complejo**: Muestra el dominio (plano Z) y codominio (plano W) de funciones complejas
- **Superficies de Riemann**: Visualización 3D de la superficie de Riemann equivalente
- **Leyenda completa** que incluye:
  - Dominio (Plano Z)
  - Frontera
  - Codominio (Plano W)
  - Puntos de Acumulación
  - Puntos de Ramificación
  - Singularidades
- **Detección automática** de singularidades y puntos de ramificación
- **Interfaz interactiva** con controles de rango y resolución

## Requisitos

- Python 3.8+
- numpy
- matplotlib
- sympy
- tkinter

### Instalación de dependencias

```bash
pip install numpy matplotlib sympy
```

Para tkinter (en Ubuntu/Debian):
```bash
sudo apt-get install python3-tk
```

## Uso

Ejecutar la aplicación:

```bash
python complex_mapping_app.py
```

### Funciones soportadas

La aplicación acepta funciones complejas en términos de `z`:

- **Polinómicas**: `z**2`, `z**3 + 2*z + 1`
- **Racionales**: `1/z`, `(z+1)/(z-1)`
- **Exponenciales**: `exp(z)`, `exp(I*z)`
- **Trigonométricas**: `sin(z)`, `cos(z)`, `tan(z)`
- **Logarítmicas**: `log(z)`
- **Raíces**: `sqrt(z)`, `z**(1/3)`

### Controles

1. **Función f(z)**: Campo de entrada para escribir la función compleja
2. **Graficar**: Botón para generar la visualización
3. **Vista**: Selector para cambiar entre:
   - `plano_complejo`: Vista 2D del dominio y codominio
   - `superficie_riemann`: Vista 3D de la superficie de Riemann
4. **Rango**: Controla los límites del plano complejo mostrado (Min y Max)
5. **Resolución**: Ajusta la densidad de puntos del grid (100-500)
6. **Información**: Muestra ayuda detallada
7. **Limpiar**: Limpia los gráficos actuales

## Interpretación de los gráficos

### Plano Complejo (2D)

- **Colores**: Representan la fase (argumento) del número complejo usando el mapa de colores HSV
  - Rojo: fase ≈ 0
  - Verde: fase ≈ 2π/3
  - Azul: fase ≈ 4π/3
- **Líneas de contorno blancas**: Magnitud constante
- **Líneas negras**: Fase constante
- **Marcadores**:
  - Círculos turquesa: Singularidades (polos)
  - Cuadrados violetas: Puntos de ramificación

### Superficie de Riemann (3D)

- **Ejes X, Y**: Parte real e imaginaria de z
- **Eje Z (altura)**: Magnitud |f(z)|
- **Colores**: Fase de f(z)

## Ejemplos de funciones para probar

1. **Función cuadrática**: `z**2`
   - Duplica ángulos, eleva al cuadrado magnitudes
   
2. **Función recíproca**: `1/z`
   - Invierte el plano, singularidad en z=0
   
3. **Exponencial**: `exp(z)`
   - Mapea líneas verticales a círculos
   
4. **Raíz cuadrada**: `sqrt(z)`
   - Función multivaluada, punto de ramificación en z=0
   
5. **Logaritmo**: `log(z)`
   - Inverso de la exponencial, corte de rama en eje real negativo
   
6. **Transformación de Möbius**: `(z-1)/(z+1)`
   - Transformación conformal del plano complejo

## Estructura del código

- `ComplexFunctionMapper`: Clase para análisis simbólico y numérico de funciones complejas
  - `parse_function()`: Parsea la expresión de la función
  - `evaluate_function()`: Evalúa numéricamente la función
  - `find_singularities()`: Detecta polos y singularidades
  - `find_branch_points()`: Detecta puntos de ramificación
  
- `ComplexMappingApp`: Clase principal de la interfaz gráfica
  - `setup_ui()`: Configura la interfaz de usuario
  - `plot_complex_plane()`: Grafica en 2D
  - `plot_riemann_surface()`: Grafica superficie de Riemann en 3D
  - `update_function_info()`: Actualiza panel de información

## Notas técnicas

- El código usa `sympy` para análisis simbólico y detección de singularidades
- `numpy` se utiliza para evaluación numérica eficiente en grids
- `matplotlib` con backend TkAgg para visualización interactiva
- La aplicación maneja automáticamente valores infinitos y NaN

## Autor

Generado como aplicación educativa para visualización de análisis complejo.

## Licencia

Código abierto para uso educativo.
