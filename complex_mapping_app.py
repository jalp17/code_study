#!/usr/bin/env python3
"""
Aplicación de Escritorio Interactiva para Mapeo de Funciones Complejas
y Visualización de Superficies de Riemann

Características:
- Graficado del mapeo de funciones complejas como regiones del plano complejo
- Leyenda con: dominio, frontera, codominio, puntos de acumulación, 
  puntos de ramificación, singularidades
- Opción para cambiar a vista de superficie de Riemann equivalente
- Entrada interactiva de función compleja
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import sympy as sp
from sympy import symbols, I, exp, log, sqrt, sin, cos, tan, sec, csc, cot
from sympy import residue, limit, diff, solve, Eq, Abs, arg
import warnings
warnings.filterwarnings('ignore')

class ComplexFunctionMapper:
    """Clase principal para el mapeo de funciones complejas"""
    
    def __init__(self):
        self.z = symbols('z')
        self.function_expr = None
        self.function_lambda = None
        
    def parse_function(self, func_str):
        """Parsear la función ingresada por el usuario"""
        try:
            # Reemplazar notaciones comunes
            func_str = func_str.replace('^', '**')
            func_str = func_str.replace('j', 'I')
            func_str = func_str.replace('i', 'I')
            
            # Parsear la expresión
            self.function_expr = sp.sympify(func_str, locals={'z': self.z, 'I': I})
            
            # Crear función lambda para evaluación numérica
            self.function_lambda = sp.lambdify(self.z, self.function_expr, 'numpy')
            
            return True, "Función válida"
        except Exception as e:
            return False, f"Error al parsear función: {str(e)}"
    
    def evaluate_function(self, z_values):
        """Evaluar la función en valores del plano complejo"""
        if self.function_lambda is None:
            return None
        
        try:
            result = self.function_lambda(z_values)
            # Manejar casos donde hay errores numéricos
            result = np.nan_to_num(result, nan=np.inf, posinf=np.inf, neginf=-np.inf)
            return result
        except Exception as e:
            return None
    
    def find_singularities(self, domain_range=(-5, 5)):
        """Encontrar singularidades de la función"""
        singularities = []
        
        if self.function_expr is None:
            return singularities
        
        try:
            # Encontrar polos usando sympy
            # Analizar denominador si es una función racional
            numer, denom = sp.fraction(self.function_expr)
            
            if denom != 1:
                poles = solve(denom, self.z)
                for pole in poles:
                    try:
                        pole_val = complex(pole.evalf())
                        if domain_range[0] <= pole_val.real <= domain_range[1] and \
                           domain_range[0] <= pole_val.imag <= domain_range[1]:
                            singularities.append(('Polo', pole_val))
                    except:
                        pass
            
            # Buscar singularidades esenciales (puntos donde log, sqrt, etc tienen problemas)
            # Para log(z), singularidad en z=0
            if self.function_expr.has(log):
                singularities.append(('Singularidad Log', 0+0j))
            
            # Para sqrt(z), punto de ramificación en z=0
            if self.function_expr.has(sqrt):
                singularities.append(('Punto Ramificación', 0+0j))
                
        except Exception as e:
            pass
        
        return singularities
    
    def find_branch_points(self):
        """Encontrar puntos de ramificación"""
        branch_points = []
        
        if self.function_expr is None:
            return branch_points
        
        try:
            # Puntos de ramificación típicos para funciones multivaluadas
            if self.function_expr.has(log):
                branch_points.append((0+0j, 'Logaritmo'))
            
            if self.function_expr.has(sqrt):
                branch_points.append((0+0j, 'Raíz cuadrada'))
            
            # Para z^(1/n), punto de ramificación en 0 y posiblemente infinito
            powers = self.function_expr.atoms(sp.Pow)
            for p in powers:
                if p.exp.is_Rational and p.exp.q > 1:
                    branch_points.append((0+0j, f'Potencia {p.exp}'))
                    
        except Exception:
            pass
        
        return branch_points
    
    def compute_jacobian(self, z_val):
        """Calcular el Jacobiano del mapeo en un punto"""
        if self.function_expr is None:
            return None
        
        try:
            # Derivada compleja
            deriv = diff(self.function_expr, self.z)
            deriv_func = sp.lambdify(self.z, deriv, 'numpy')
            return deriv_func(z_val)
        except:
            return None


class ComplexMappingApp:
    """Aplicación GUI para visualización de mapeos complejos"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mapeo de Funciones Complejas - Superficies de Riemann")
        self.root.geometry("1400x900")
        
        self.mapper = ComplexFunctionMapper()
        self.current_view = "plano"  # "plano" o "riemann"
        self.domain_range = (-3, 3)
        self.resolution = 300
        
        # Colores para la leyenda
        self.colors = {
            'dominio': '#3498db',
            'frontera': '#e74c3c',
            'codominio': '#2ecc71',
            'acumulacion': '#f39c12',
            'ramificacion': '#9b59b6',
            'singularidad': '#1abc9c'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Frame superior para controles
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Entrada de función
        ttk.Label(control_frame, text="Función f(z):", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.func_entry = ttk.Entry(control_frame, width=40, font=('Arial', 11))
        self.func_entry.insert(0, "z**2")  # Valor por defecto
        self.func_entry.pack(side=tk.LEFT, padx=5)
        
        # Botón para graficar
        plot_btn = ttk.Button(control_frame, text="Graficar", command=self.plot_mapping)
        plot_btn.pack(side=tk.LEFT, padx=5)
        
        # Selector de vista
        ttk.Label(control_frame, text="Vista:", font=('Arial', 11)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.view_var = tk.StringVar(value="plano")
        view_combo = ttk.Combobox(control_frame, textvariable=self.view_var, 
                                   values=["plano_complejo", "superficie_riemann"], 
                                   state="readonly", width=20)
        view_combo.pack(side=tk.LEFT, padx=5)
        view_combo.bind('<<ComboboxSelected>>', self.on_view_change)
        
        # Controles de rango
        ttk.Label(control_frame, text="Rango:", font=('Arial', 11)).pack(side=tk.LEFT, padx=(20, 5))
        
        ttk.Label(control_frame, text="Min:").pack(side=tk.LEFT, padx=2)
        self.range_min = ttk.Entry(control_frame, width=6)
        self.range_min.insert(0, "-3")
        self.range_min.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(control_frame, text="Max:").pack(side=tk.LEFT, padx=2)
        self.range_max = ttk.Entry(control_frame, width=6)
        self.range_max.insert(0, "3")
        self.range_max.pack(side=tk.LEFT, padx=2)
        
        # Controles de resolución
        ttk.Label(control_frame, text="Resolución:", font=('Arial', 11)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.res_var = tk.IntVar(value=300)
        res_scale = ttk.Scale(control_frame, from_=100, to=500, variable=self.res_var, 
                              orient=tk.HORIZONTAL, length=150)
        res_scale.pack(side=tk.LEFT, padx=5)
        
        # Botones adicionales
        info_btn = ttk.Button(control_frame, text="Información", command=self.show_info)
        info_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttk.Button(control_frame, text="Limpiar", command=self.clear_plot)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Frame principal para gráficos
        main_frame = ttk.Frame(self.root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear figura de matplotlib
        self.fig = Figure(figsize=(12, 8), dpi=100)
        
        # Subplots
        self.ax_domain = self.fig.add_subplot(121)
        self.ax_codomain = self.fig.add_subplot(122)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Barra de herramientas
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        
        # Frame para leyenda
        legend_frame = ttk.LabelFrame(self.root, text="Leyenda", padding="10")
        legend_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.legend_labels = {}
        legend_items = [
            ('dominio', 'Dominio (Plano Z)'),
            ('frontera', 'Frontera'),
            ('codominio', 'Codominio (Plano W)'),
            ('acumulacion', 'Puntos de Acumulación'),
            ('ramificacion', 'Puntos de Ramificación'),
            ('singularidad', 'Singularidades')
        ]
        
        for i, (key, label) in enumerate(legend_items):
            color_box = tk.Canvas(legend_frame, width=20, height=20, bg=self.colors[key])
            color_box.grid(row=0, column=i*2, padx=10, pady=5)
            lbl = ttk.Label(legend_frame, text=label, font=('Arial', 10))
            lbl.grid(row=0, column=i*2+1, padx=5, pady=5, sticky='w')
            self.legend_labels[key] = lbl
        
        # Frame para información de puntos
        info_frame = ttk.LabelFrame(self.root, text="Análisis de la Función", padding="10")
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.info_text = tk.Text(info_frame, height=4, width=120, font=('Courier', 9))
        self.info_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
    def on_view_change(self, event=None):
        """Manejar cambio de vista"""
        self.current_view = self.view_var.get().replace('_', ' ')
        if 'riemann' in self.current_view.lower():
            self.current_view = "riemann"
        else:
            self.current_view = "plano"
        self.plot_mapping()
    
    def get_domain_grid(self):
        """Obtener grid del dominio"""
        try:
            min_val = float(self.range_min.get())
            max_val = float(self.range_max.get())
            self.domain_range = (min_val, max_val)
        except:
            self.domain_range = (-3, 3)
        
        self.resolution = self.res_var.get()
        
        x = np.linspace(self.domain_range[0], self.domain_range[1], self.resolution)
        y = np.linspace(self.domain_range[0], self.domain_range[1], self.resolution)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y
        
        return Z, X, Y
    
    def plot_mapping(self):
        """Graficar el mapeo de la función compleja"""
        # Limpiar ejes
        self.ax_domain.clear()
        self.ax_codomain.clear()
        
        # Parsear función
        func_str = self.func_entry.get()
        success, msg = self.mapper.parse_function(func_str)
        
        if not success:
            messagebox.showerror("Error", msg)
            return
        
        # Obtener grid del dominio
        Z, X, Y = self.get_domain_grid()
        
        # Evaluar función
        W = self.mapper.evaluate_function(Z)
        
        if W is None:
            messagebox.showerror("Error", "No se pudo evaluar la función")
            return
        
        if self.current_view == "riemann":
            self.plot_riemann_surface(Z, W, X, Y)
        else:
            self.plot_complex_plane(Z, W, X, Y)
        
        # Actualizar información
        self.update_function_info()
        
        self.canvas.draw()
    
    def plot_complex_plane(self, Z, W, X, Y):
        """Graficar en el plano complejo"""
        # Plot del dominio (plano Z)
        self.ax_domain.set_title('Dominio (Plano Z)', fontsize=12, fontweight='bold')
        
        # Colorear por argumento (fase)
        phase_Z = np.angle(Z)
        phase_Z = np.ma.masked_where(np.abs(Z) < 1e-10, phase_Z)
        
        domain_plot = self.ax_domain.imshow(phase_Z, extent=[self.domain_range[0], 
                                                              self.domain_range[1],
                                                              self.domain_range[0], 
                                                              self.domain_range[1]],
                                             origin='lower', cmap='hsv', alpha=0.7)
        
        # Dibujar grid
        self.ax_domain.contour(X, Y, np.abs(Z), levels=[0.5, 1, 2, 3], colors='white', 
                               linewidths=0.5, alpha=0.5)
        self.ax_domain.contour(X, Y, np.angle(Z), levels=np.linspace(-np.pi, np.pi, 12), 
                               colors='black', linewidths=0.3, alpha=0.3)
        
        # Marcar eje real e imaginario
        self.ax_domain.axhline(y=0, color='black', linewidth=1, linestyle='--', alpha=0.5)
        self.ax_domain.axvline(x=0, color='black', linewidth=1, linestyle='--', alpha=0.5)
        
        # Frontera
        self.ax_domain.plot([self.domain_range[0], self.domain_range[1]], 
                           [self.domain_range[0], self.domain_range[0]], 
                           color=self.colors['frontera'], linewidth=2, label='Frontera')
        self.ax_domain.plot([self.domain_range[0], self.domain_range[1]], 
                           [self.domain_range[1], self.domain_range[1]], 
                           color=self.colors['frontera'], linewidth=2)
        self.ax_domain.plot([self.domain_range[0], self.domain_range[0]], 
                           [self.domain_range[0], self.domain_range[1]], 
                           color=self.colors['frontera'], linewidth=2)
        self.ax_domain.plot([self.domain_range[1], self.domain_range[1]], 
                           [self.domain_range[0], self.domain_range[1]], 
                           color=self.colors['frontera'], linewidth=2)
        
        # Singularidades
        singularities = self.mapper.find_singularities(self.domain_range)
        for sing_type, sing_point in singularities:
            self.ax_domain.plot(sing_point.real, sing_point.imag, 'o', 
                               color=self.colors['singularidad'], markersize=10, 
                               markeredgecolor='black', markeredgewidth=1)
        
        # Puntos de ramificación
        branch_points = self.mapper.find_branch_points()
        for bp_point, bp_type in branch_points:
            if self.domain_range[0] <= bp_point.real <= self.domain_range[1] and \
               self.domain_range[0] <= bp_point.imag <= self.domain_range[1]:
                self.ax_domain.plot(bp_point.real, bp_point.imag, 's', 
                                   color=self.colors['ramificacion'], markersize=12,
                                   markeredgecolor='black', markeredgewidth=1)
        
        self.ax_domain.set_xlabel('Re(z)')
        self.ax_domain.set_ylabel('Im(z)')
        self.ax_domain.set_aspect('equal')
        self.ax_domain.grid(True, alpha=0.3)
        
        # Plot del codominio (plano W)
        self.ax_codomain.set_title('Codominio (Plano W = f(z))', fontsize=12, fontweight='bold')
        
        # Colorear por magnitud y fase
        abs_W = np.abs(W)
        phase_W = np.angle(W)
        
        # Máscara para valores infinitos
        mask = np.isfinite(abs_W) & (abs_W < 1e10)
        abs_W_masked = np.ma.masked_where(~mask, abs_W)
        phase_W_masked = np.ma.masked_where(~mask, phase_W)
        
        # Usar fase para colorear
        codomain_plot = self.ax_codomain.imshow(phase_W_masked, 
                                                 extent=[self.domain_range[0], 
                                                         self.domain_range[1],
                                                         self.domain_range[0], 
                                                         self.domain_range[1]],
                                                 origin='lower', cmap='hsv', alpha=0.7)
        
        # Grid de coordenadas en W
        try:
            W_X = np.real(W)
            W_Y = np.imag(W)
            
            # Contornos de nivel
            levels_abs = np.percentile(abs_W_masked[np.isfinite(abs_W_masked)], 
                                       [25, 50, 75]) if np.any(mask) else [1, 2, 3]
            self.ax_codomain.contour(W_X, W_Y, abs_W_masked, levels=levels_abs, 
                                     colors='white', linewidths=0.5, alpha=0.5)
        except:
            pass
        
        # Ejes
        self.ax_codomain.axhline(y=0, color='black', linewidth=1, linestyle='--', alpha=0.5)
        self.ax_codomain.axvline(x=0, color='black', linewidth=1, linestyle='--', alpha=0.5)
        
        # Frontera transformada
        try:
            boundary_x = np.concatenate([
                np.linspace(self.domain_range[0], self.domain_range[1], 100),
                [self.domain_range[1]] * 100,
                np.linspace(self.domain_range[1], self.domain_range[0], 100),
                [self.domain_range[0]] * 100
            ])
            boundary_y = np.concatenate([
                [self.domain_range[0]] * 100,
                np.linspace(self.domain_range[0], self.domain_range[1], 100),
                [self.domain_range[1]] * 100,
                np.linspace(self.domain_range[1], self.domain_range[0], 100)
            ])
            boundary_z = boundary_x + 1j * boundary_y
            boundary_w = self.mapper.evaluate_function(boundary_z)
            
            if boundary_w is not None:
                self.ax_codomain.plot(np.real(boundary_w), np.imag(boundary_w), 
                                     color=self.colors['frontera'], linewidth=2, 
                                     label='Frontera transformada')
        except:
            pass
        
        self.ax_codomain.set_xlabel('Re(w)')
        self.ax_codomain.set_ylabel('Im(w)')
        self.ax_codomain.set_aspect('equal')
        self.ax_codomain.grid(True, alpha=0.3)
        
        # Añadir colorbar para fase
        cbar = self.fig.colorbar(phase_W_masked if np.any(mask) else phase_W, 
                                 ax=self.ax_codomain, shrink=0.8)
        cbar.set_label('Fase (radianes)')
    
    def plot_riemann_surface(self, Z, W, X, Y):
        """Graficar superficie de Riemann"""
        # Configurar para proyección 3D
        from mpl_toolkits.mplot3d import Axes3D
        
        # Limpiar y recrear ejes para 3D
        self.fig.clf()
        
        # Dos subplots 3D
        self.ax_domain = self.fig.add_subplot(121, projection='3d')
        self.ax_codomain = self.fig.add_subplot(122, projection='3d')
        
        # Superficie de Riemann para el dominio (|z| como altura)
        abs_Z = np.abs(Z)
        phase_Z = np.angle(Z)
        
        # Dominio - superficie de Riemann
        surf1 = self.ax_domain.plot_surface(X, Y, abs_Z, facecolors=plt.cm.hsv((phase_Z + np.pi) / (2*np.pi)),
                                            rstride=1, cstride=1, linewidth=0, antialiased=True, alpha=0.8)
        
        self.ax_domain.set_title('Superficie de Riemann - Dominio', fontsize=11, fontweight='bold')
        self.ax_domain.set_xlabel('Re(z)')
        self.ax_domain.set_ylabel('Im(z)')
        self.ax_domain.set_zlabel('|z|')
        
        # Marcar punto de ramificación en origen
        self.ax_domain.scatter([0], [0], [0], color='red', s=100, label='Punto ramificación')
        
        # Codominio - superficie de Riemann
        abs_W = np.abs(W)
        phase_W = np.angle(W)
        
        # Máscara para valores válidos
        mask = np.isfinite(abs_W) & (abs_W < 1e10)
        
        if np.any(mask):
            X_masked = np.ma.masked_where(~mask, X)
            Y_masked = np.ma.masked_where(~mask, Y)
            abs_W_masked = np.ma.masked_where(~mask, abs_W)
            phase_W_masked = np.ma.masked_where(~mask, phase_W)
            
            colors = plt.cm.hsv((phase_W_masked + np.pi) / (2*np.pi))
            
            surf2 = self.ax_codomain.plot_surface(X_masked, Y_masked, abs_W_masked, 
                                                  facecolors=colors,
                                                  rstride=1, cstride=1, 
                                                  linewidth=0, antialiased=True, alpha=0.8)
        
        self.ax_codomain.set_title('Superficie de Riemann - Codominio', fontsize=11, fontweight='bold')
        self.ax_codomain.set_xlabel('Re(z)')
        self.ax_codomain.set_ylabel('Im(z)')
        self.ax_codomain.set_zlabel('|f(z)|')
        
        # Marcar singularidades
        singularities = self.mapper.find_singularities(self.domain_range)
        for sing_type, sing_point in singularities:
            try:
                w_val = self.mapper.evaluate_function(sing_point)
                if w_val is not None and np.isfinite(np.abs(w_val)):
                    self.ax_codomain.scatter([sing_point.real], [sing_point.imag], 
                                           [np.abs(w_val)], color='red', s=100)
            except:
                pass
        
        self.canvas.draw()
    
    def update_function_info(self):
        """Actualizar información de la función"""
        func_str = self.func_entry.get()
        
        info = f"Función: f(z) = {func_str}\n\n"
        
        # Singularidades
        singularities = self.mapper.find_singularities(self.domain_range)
        if singularities:
            info += "Singularidades encontradas:\n"
            for sing_type, sing_point in singularities:
                info += f"  - {sing_type}: z = {sing_point:.4f}\n"
        else:
            info += "No se detectaron singularidades obvias en el dominio.\n"
        
        # Puntos de ramificación
        branch_points = self.mapper.find_branch_points()
        if branch_points:
            info += "\nPuntos de ramificación:\n"
            for bp_point, bp_type in branch_points:
                info += f"  - {bp_type}: z = {bp_point:.4f}\n"
        
        # Información adicional
        info += f"\nDominio mostrado: [{self.domain_range[0]}, {self.domain_range[1]}] × [{self.domain_range[0]}, {self.domain_range[1]}]\n"
        info += f"Resolución: {self.resolution}×{self.resolution} puntos"
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
    
    def clear_plot(self):
        """Limpiar los gráficos"""
        self.ax_domain.clear()
        self.ax_codomain.clear()
        self.ax_domain.set_title('Dominio (Plano Z)')
        self.ax_codomain.set_title('Codominio (Plano W)')
        self.ax_domain.set_xlabel('Re(z)')
        self.ax_domain.set_ylabel('Im(z)')
        self.ax_codomain.set_xlabel('Re(w)')
        self.ax_codomain.set_ylabel('Im(w)')
        self.ax_domain.grid(True, alpha=0.3)
        self.ax_codomain.grid(True, alpha=0.3)
        self.info_text.delete(1.0, tk.END)
        self.canvas.draw()
    
    def show_info(self):
        """Mostrar información de ayuda"""
        info_text = """
        AYUDA - Mapeo de Funciones Complejas
        
        INSTRUCCIONES DE USO:
        1. Ingrese una función compleja en términos de z
           Ejemplos: z**2, 1/z, exp(z), sin(z), log(z), sqrt(z)
        
        2. Presione "Graficar" para visualizar el mapeo
        
        3. Use el selector "Vista" para cambiar entre:
           - plano_complejo: Muestra dominio y codominio en 2D
           - superficie_riemann: Muestra superficies de Riemann en 3D
        
        4. Ajuste el rango y resolución según necesite
        
        CARACTERÍSTICAS:
        • Dominio: Región del plano Z (azul en leyenda)
        • Frontera: Límite del dominio (rojo)
        • Codominio: Imagen en el plano W (verde)
        • Puntos de Acumulación: Donde la función tiende a infinito
        • Puntos de Ramificación: Para funciones multivaluadas (violeta)
        • Singularidades: Polos y singularidades esenciales (turquesa)
        
        NOTAS:
        - El color representa la fase (argumento) de los números complejos
        - Las líneas de contorno muestran magnitud constante
        - En vista 3D, la altura representa |f(z)|
        """
        
        messagebox.showinfo("Ayuda", info_text)


def main():
    """Función principal"""
    root = tk.Tk()
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')
    
    app = ComplexMappingApp(root)
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
