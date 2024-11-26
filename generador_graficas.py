import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, Point, GeometryCollection
from shapely.ops import split

def plot_feasible_region_step_by_step():
    # Definir los límites del gráfico
    x_min, x_max = -3, 7
    y_min, y_max = -5, 10

    # Definir el área de visualización como un polígono
    plotting_polygon = Polygon([
        (x_min, y_min),
        (x_min, y_max),
        (x_max, y_max),
        (x_max, y_min)
    ])

    # Definir las restricciones del problema
    # Cada restricción está representada como:
    # (Etiqueta, Coeficiente A, Coeficiente B, C, Tipo de desigualdad)
    constraints = [
        ("2x₁ + x₂ ≤ 8 \n(Almacenamiento)", 2, 1, 8, "<="),
        ("x₂ ≤ 5 \n(Disponibilidad)", 0, 1, 5, "<="),
        ("x₁ - x₂ ≤ 4 \n(Seguridad)", 1, -1, 4, "<="),
        ("x₁ ≥ 0", 1, 0, 0, ">="),
        ("x₂ ≥ 0", 0, 1, 0, ">="),
    ]

    # Inicializar la región factible como el área de visualización
    feasible_region = plotting_polygon

    # Iterar sobre cada restricción y actualizar la región factible
    for i, (label, A, B, C, inequality) in enumerate(constraints, 1):
        # Definir la línea de la restricción
        if A == 0 and B != 0:
            # Línea horizontal: y = C/B
            y = C / B
            line = LineString([(x_min, y), (x_max, y)])
        elif B == 0 and A != 0:
            # Línea vertical: x = C/A
            x = C / A
            line = LineString([(x, y_min), (x, y_max)])
        else:
            # Línea con pendiente: y = (-A/B)x + C/B
            x1 = x_min
            y1 = (-A / B) * x1 + C / B
            x2 = x_max
            y2 = (-A / B) * x2 + C / B
            line = LineString([(x1, y1), (x2, y2)])

        # Dividir la región factible actual con la nueva restricción
        splitted = split(feasible_region, line)

        # Determinar qué parte de la división cumple la desigualdad
        feasible_parts = []
        for geom in splitted.geoms:
            if not isinstance(geom, Polygon):
                continue  # Ignorar geometrías que no sean polígonos

            # Tomar un punto representativo dentro del polígono
            p = geom.representative_point()
            x_p, y_p = p.x, p.y

            # Evaluar la desigualdad en el punto
            lhs = A * x_p + B * y_p
            if inequality == "<=" and lhs <= C + 1e-6:
                feasible_parts.append(geom)
            elif inequality == ">=" and lhs >= C - 1e-6:
                feasible_parts.append(geom)

        # Actualizar la región factible
        if feasible_parts:
            feasible_region = feasible_region.intersection(GeometryCollection(feasible_parts))
        else:
            # Si no hay región factible, terminar el proceso
            feasible_region = Polygon()
            print(f"No hay región factible después de aplicar la restricción: {label}")

        # Graficar las restricciones hasta el paso actual
        plt.figure(figsize=(10, 8))
        plt.title(f"Región Factible después de {i} Restricción(es)", fontsize=16)
        plt.xlabel("$x_1$", fontsize=14)
        plt.ylabel("$x_2$", fontsize=14)
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        plt.grid(True, linestyle='--', linewidth=0.5)

        # Colores para las restricciones
        colors = ['blue', 'orange', 'green', 'red', 'purple']

        # Graficar todas las restricciones hasta el paso actual
        for j in range(i):
            clabel, A_j, B_j, C_j, ineq_j = constraints[j]
            if A_j == 0 and B_j != 0:
                # Línea horizontal
                y_val = C_j / B_j
                plt.axhline(y=y_val, color=colors[j], label=clabel)
                plt.text(x_min + 0.5, y_val + 0.2 + j*0.3, clabel, color=colors[j], fontsize=10)
            elif B_j == 0 and A_j != 0:
                # Línea vertical
                x_val = C_j / A_j
                plt.axvline(x=x_val, color=colors[j], label=clabel)
                plt.text(x_val + 0.2, y_min + 0.5 + j*0.3, clabel, color=colors[j], fontsize=10)
            else:
                # Línea con pendiente
                x_vals = np.linspace(x_min, x_max, 400)
                y_vals = (-A_j / B_j) * x_vals + C_j / B_j
                plt.plot(x_vals, y_vals, color=colors[j], label=clabel)
                # Anotar la ecuación de la restricción
                idx = (np.abs(x_vals - (x_min + 0.5))).argmin()
                plt.text(x_vals[idx], y_vals[idx] + j*0.3, clabel, color=colors[j], fontsize=10)

        # Graficar la región factible
        if not feasible_region.is_empty and feasible_region.geom_type in ['Polygon', 'MultiPolygon']:
            if feasible_region.geom_type == 'Polygon':
                polys = [feasible_region]
            else:
                polys = feasible_region.geoms
            for poly in polys:
                x_f, y_f = poly.exterior.xy
                plt.fill(x_f, y_f, color='green', alpha=0.3, label="Región Factible")
        else:
            pass  # No hay región factible para graficar

        plt.legend(loc='upper right')
        plt.show()

        # Esperar a que el usuario presione Enter para continuar
        if i < len(constraints):
            input("Presiona Enter para agregar la siguiente restricción...")

    # Graficar la región factible final con todas las restricciones
    if not feasible_region.is_empty:
        plt.figure(figsize=(10, 8))
        plt.title("Región Factible Final con todas las Restricciones", fontsize=16)
        plt.xlabel("$x_1$", fontsize=14)
        plt.ylabel("$x_2$", fontsize=14)
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        plt.grid(True, linestyle='--', linewidth=0.5)

        # Colores para las restricciones
        colors = ['blue', 'orange', 'green', 'red', 'purple']

        # Graficar todas las restricciones
        for j, (clabel, A_j, B_j, C_j, ineq_j) in enumerate(constraints):
            if A_j == 0 and B_j != 0:
                # Línea horizontal
                y_val = C_j / B_j
                plt.axhline(y=y_val, color=colors[j], label=clabel)
                plt.text(x_min + 0.5, y_val + 0.2 + j*0.3, clabel, color=colors[j], fontsize=10)
            elif B_j == 0 and A_j != 0:
                # Línea vertical
                x_val = C_j / A_j
                plt.axvline(x=x_val, color=colors[j], label=clabel)
                plt.text(x_val + 0.2, y_min + 0.5 + j*0.3, clabel, color=colors[j], fontsize=10)
            else:
                # Línea con pendiente
                x_vals = np.linspace(x_min, x_max, 400)
                y_vals = (-A_j / B_j) * x_vals + C_j / B_j
                plt.plot(x_vals, y_vals, color=colors[j], label=clabel)
                # Anotar la ecuación de la restricción
                idx = (np.abs(x_vals - (x_min + 0.5))).argmin()
                plt.text(x_vals[idx], y_vals[idx] + j*0.3, clabel, color=colors[j], fontsize=10)

        # Graficar la región factible final
        if feasible_region.geom_type == 'Polygon':
            polys = [feasible_region]
        else:
            polys = feasible_region.geoms
        for poly in polys:
            x_f, y_f = poly.exterior.xy
            plt.fill(x_f, y_f, color='green', alpha=0.3, label="Región Factible")

        plt.legend(loc='upper right')
        plt.show()
    else:
        print("No hay región factible.")

# Ejecutar la función
plot_feasible_region_step_by_step()
