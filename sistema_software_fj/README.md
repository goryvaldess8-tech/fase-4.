# Sistema Integral de Gestión de Clientes, Servicios y Reservas — Software FJ

Proyecto desarrollado en **Python 3** para el curso **Programación (Código: 213023)** de la **Universidad Nacional Abierta y a Distancia (UNAD)** — Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI), **Fase 4: Componente Práctico (Prácticas Simuladas)**.

- **Autor:** Rodrigo Valdés Vásquez
- **Programa:** Ingeniería de Sistemas
- **Empresa simulada:** Software FJ

---

## Descripción General

Aplicación modular orientada a objetos **sin uso de bases de datos** (toda la gestión de entidades se realiza mediante objetos y listas internas en memoria, utilizando manejo de archivos únicamente para el registro estructurado de eventos y errores en `logs/sistema_software_fj.log`).

Implementa de manera rigurosa los principios de:
1. **Abstracción:** Clases abstractas `Entidad(ABC)` y `Servicio(Entidad, ABC)` con contratos obligatorios (`@abstractmethod`).
2. **Herencia:** `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`; los servicios especializados `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada` heredan de `Servicio`; las excepciones personalizadas heredan de `ErrorSistemaSoftwareFJ(Exception)`.
3. **Polimorfismo:** Sobrescritura especializada de `calcular_costo()`, `describir_servicio()` y `validar_parametros()` en los tres tipos de servicios.
4. **Encapsulación:** Atributos privados (`__atributo`) protegidos mediante propiedades (`@property` y `@setter`) con validaciones estrictas de tipo, formato y rango.
5. **Sobrecarga de métodos:** Implementada en `calcular_costo()` mediante variantes tipadas con `@overload` y parámetros opcionales (impuesto, descuento, recargo adicional), y en `cotizar()` mediante despacho múltiple dinámico con `@singledispatchmethod` (`int`/`float`, `tuple`, `dict`).
6. **Manejo avanzado de excepciones:** Excepciones personalizadas, bloques `try/except`, `try/except/else`, `try/except/finally`, encadenamiento de excepciones (`raise ... from ...`) y auditoría automática en archivo de logs.

---

## Estructura del Proyecto

```text
sistema_software_fj/
├── main.py                       # Punto de entrada principal del sistema
├── README.md                     # Documentación general del repositorio
├── .gitignore                    # Reglas de exclusión para Git
├── src/
│   ├── __init__.py               # Exportación de símbolos del paquete
│   ├── excepciones.py            # Jerarquía de excepciones personalizadas
│   ├── gestor_logs.py            # Registro de eventos y errores en archivo UTF-8
│   ├── entidad.py                # Clase abstracta base Entidad
│   ├── cliente.py                # Clase Cliente con encapsulación y validaciones
│   ├── servicio.py               # Clase abstracta Servicio + 3 servicios especializados
│   ├── reserva.py                # Clase Reserva + EstadoReserva (confirmar, cancelar, procesar)
│   ├── gestor_sistema.py         # Coordinador en memoria SistemaGestionSoftwareFJ
│   └── simulacion.py             # Simulación completa de 14 operaciones válidas y fallidas
├── tests/
│   ├── __init__.py
│   └── test_sistema.py           # Pruebas unitarias y de integración (unittest)
└── logs/
    └── sistema_software_fj.log   # Archivo de auditoría generado durante la ejecución
```

---

## Requisitos y Ejecución

No requiere dependencias externas ni motores de base de datos; funciona únicamente con la **biblioteca estándar de Python 3.10+**.

### 1. Ejecutar la simulación completa (14 operaciones)

```bash
python main.py
```

Al ejecutarse, el sistema realiza 14 operaciones completas (registros válidos e inválidos de clientes, creación correcta e incorrecta de servicios, demostración polimórfica y sobrecargada, reservas exitosas y fallidas, cancelaciones, operaciones no permitidas y cálculos inconsistentes), manteniéndose estable sin interrupciones y registrando cada evento y error en `logs/sistema_software_fj.log`.

### 2. Ejecutar las pruebas unitarias

```bash
python -m unittest discover -s tests -v
```

---

## Licencia y Uso Académico

Proyecto elaborado con fines académicos para el curso **Programación (213023)** de la UNAD.
