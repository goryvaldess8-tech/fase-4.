"""
Punto de entrada principal del Sistema Integral de Gestión de Clientes,
Servicios y Reservas para Software FJ.

Universidad Nacional Abierta y a Distancia (UNAD)
Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI)
Programa: Ingeniería de Sistemas | Curso: Programación (213023)
Fase 4 - Componente Práctico: Prácticas Simuladas
Autor: Rodrigo Valdés Vásquez

Ejecución:
    python main.py
"""

import sys

from src.simulacion import ejecutar_simulacion


def main() -> int:
    """
    Configura la salida estándar en UTF-8 y ejecuta la simulación principal.

    Retorna el código de salida 0 cuando el sistema finaliza de manera estable.
    """
    # En sistemas Windows, se asegura codificación UTF-8 para imprimir acentos y símbolos
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # Bloque try/except/finally de nivel superior como última barrera de estabilidad
    sistema = None
    try:
        sistema = ejecutar_simulacion(ruta_log="logs/sistema_software_fj.log")
    except Exception as error_inesperado:
        # Ante cualquier eventualidad crítica no prevista, se informa sin traza abrupta
        print(f"\n[ERROR CRÍTICO NO PREVISTO] {error_inesperado}")
        return 1
    else:
        print("\nEjecución completada exitosamente. El sistema permaneció estable en todo momento.")
        return 0
    finally:
        # Se garantiza el cierre limpio del manejador de archivo de logs
        if sistema is not None:
            sistema.logs.cerrar()


if __name__ == "__main__":
    raise SystemExit(main())
