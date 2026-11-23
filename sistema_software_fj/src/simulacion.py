"""
Módulo de simulación integral de operaciones para Software FJ.

Ejecuta 14 operaciones completas (superando el mínimo de 10 exigido en el Anexo 3)
que incluyen:
- Registros válidos e inválidos de clientes (datos inválidos, faltantes y duplicados).
- Creación correcta e incorrecta de los 3 servicios especializados.
- Demostración explícita de polimorfismo y sobrecarga de métodos.
- Reservas exitosas (creación, confirmación y procesamiento completo).
- Reservas y operaciones fallidas (servicio no disponible, parámetros inválidos,
  cliente inactivo, transiciones prohibidas, cálculos financieros inconsistentes,
  entidades inexistentes) con encadenamiento de excepciones y registro en logs.
"""

from typing import Callable

from src.excepciones import ErrorSistemaSoftwareFJ
from src.gestor_logs import GestorLogs
from src.gestor_sistema import SistemaGestionSoftwareFJ
from src.servicio import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    ReservaSala,
    Servicio,
)


def _imprimir_titulo_operacion(numero: int, titulo: str) -> None:
    """Imprime un encabezado uniforme para identificar cada operación simulada."""
    print(f"\n{'=' * 78}")
    print(f"OPERACIÓN {numero:02d}: {titulo}")
    print(f"{'=' * 78}")


def _crear_servicio_seguro(
    sistema: SistemaGestionSoftwareFJ,
    fabrica: Callable[[], Servicio],
    descripcion_intento: str,
) -> Servicio | None:
    """
    Intenta instanciar y registrar un servicio capturando cualquier error de creación.

    Garantiza que una creación defectuosa de servicio se registre en el archivo
    de logs sin interrumpir el flujo general de la simulación.
    """
    try:
        # Se ejecuta la función constructora del servicio especializado
        servicio = fabrica()
    except ErrorSistemaSoftwareFJ as error:
        # Se registra el fallo de instanciación en el archivo de logs
        sistema.logs.registrar_error(
            f"Error al crear servicio ({descripcion_intento})",
            error,
        )
        print(f"  [ERROR CONTROLADO] {descripcion_intento} -> {error}")
        return None
    else:
        # Si el objeto se instanció correctamente, se registra en la lista interna
        registrado = sistema.registrar_servicio(servicio)
        if registrado is not None:
            print(f"  [OK] {registrado.obtener_resumen()}")
        return registrado


def ejecutar_simulacion(ruta_log: str = "logs/sistema_software_fj.log") -> SistemaGestionSoftwareFJ:
    """
    Ejecuta la simulación completa de 14 operaciones sobre Software FJ.

    Retorna la instancia del sistema al finalizar para permitir auditoría
    adicional o validaciones automáticas en pruebas unitarias.
    """
    # Se prepara el gestor de logs limpiando ejecuciones anteriores para trazabilidad clara
    gestor_logs = GestorLogs(ruta_archivo=ruta_log)
    gestor_logs.reiniciar_archivo()
    sistema = SistemaGestionSoftwareFJ(gestor_logs=gestor_logs)

    print("*" * 78)
    print("  SOFTWARE FJ - SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS")
    print("  Simulación sin base de datos | POO Avanzada + Manejo Robusto de Excepciones")
    print("*" * 78)

    # -------------------------------------------------------------------------
    # OPERACIÓN 01: Registro válido de clientes
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(1, "Registro válido de clientes en memoria")
    c1 = sistema.registrar_cliente(
        id_entidad="CLI-001",
        nombre_completo="Rodrigo Valdés Vásquez",
        documento="1045678901",
        correo="rodrigo.valdes@softwarefj.co",
        telefono="+573001234567",
        activo=True,
    )
    c2 = sistema.registrar_cliente(
        id_entidad="CLI-002",
        nombre_completo="Laura Martínez Gómez",
        documento="1098765432",
        correo="laura.martinez@empresa.com",
        telefono="3109876543",
        activo=True,
    )
    c3 = sistema.registrar_cliente(
        id_entidad="CLI-003",
        nombre_completo="Carlos Pérez Ríos",
        documento="79543210",
        correo="carlos.perez@correo.net",
        telefono="3204567890",
        activo=False,  # Cliente inactivo para probar restricción de negocio luego
    )
    for cliente in (c1, c2, c3):
        if cliente:
            print(f"  [OK] {cliente.obtener_resumen()}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 02: Registro inválido de cliente (correo y teléfono mal formados)
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(2, "Registro inválido de clientes (datos mal formados)")
    fallo_correo = sistema.registrar_cliente(
        id_entidad="CLI-004",
        nombre_completo="Ana Torres",
        documento="1020304050",
        correo="correo-invalido-sin-arroba",
        telefono="3112223344",
    )
    print(f"  [ERROR CONTROLADO] Registro con correo inválido retornó: {fallo_correo}")

    fallo_tel = sistema.registrar_cliente(
        id_entidad="CLI-005",
        nombre_completo="Pedro Ramírez",
        documento="1020304099",
        correo="pedro.ramirez@correo.com",
        telefono="123",  # Teléfono demasiado corto
    )
    print(f"  [ERROR CONTROLADO] Registro con teléfono inválido retornó: {fallo_tel}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 03: Registro inválido por parámetro faltante y documento duplicado
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(3, "Registro inválido de clientes (parámetro faltante y duplicado)")
    fallo_faltante = sistema.registrar_cliente(
        id_entidad="CLI-006",
        nombre_completo="",  # Parámetro obligatorio vacío
        documento="55443322",
        correo="vacio@empresa.com",
        telefono="3150001122",
    )
    print(f"  [ERROR CONTROLADO] Registro con nombre faltante retornó: {fallo_faltante}")

    fallo_duplicado = sistema.registrar_cliente(
        id_entidad="CLI-007",
        nombre_completo="Homónimo Duplicado",
        documento="1045678901",  # Documento ya registrado en CLI-001
        correo="duplicado@empresa.com",
        telefono="3169998877",
    )
    print(f"  [ERROR CONTROLADO] Registro con documento duplicado retornó: {fallo_duplicado}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 04: Creación válida de los 3 servicios especializados
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(4, "Creación válida de los tres servicios especializados")
    _crear_servicio_seguro(
        sistema,
        lambda: ReservaSala(
            id_entidad="SRV-SAL-01",
            nombre="Sala Ejecutiva Innovación",
            tarifa_base=90000.0,
            capacidad_maxima=25,
            incluye_audiovisual=True,
            disponible=True,
        ),
        "Sala Ejecutiva Innovación",
    )
    _crear_servicio_seguro(
        sistema,
        lambda: AlquilerEquipo(
            id_entidad="SRV-EQU-01",
            nombre="Estación de Trabajo Workstation Pro",
            tarifa_base=45000.0,
            categoria_equipo="Computador Portátil Alto Rendimiento",
            unidades_disponibles=5,
            seguro_obligatorio=True,
            disponible=True,
        ),
        "Workstation Pro",
    )
    _crear_servicio_seguro(
        sistema,
        lambda: AsesoriaEspecializada(
            id_entidad="SRV-ASE-01",
            nombre="Consultoría Arquitectura Cloud & Python",
            tarifa_base=120000.0,
            area_especialidad="Arquitectura de Software",
            nivel_consultor="senior",
            modalidad="presencial",
            disponible=True,
        ),
        "Consultoría Arquitectura Cloud",
    )
    _crear_servicio_seguro(
        sistema,
        lambda: ReservaSala(
            id_entidad="SRV-SAL-02",
            nombre="Auditorio Principal (En Mantenimiento)",
            tarifa_base=180000.0,
            capacidad_maxima=100,
            incluye_audiovisual=True,
            disponible=False,  # Servicio intencionalmente no disponible
        ),
        "Auditorio Principal No Disponible",
    )

    # -------------------------------------------------------------------------
    # OPERACIÓN 05: Creación incorrecta de servicios (tarifa, capacidad, modalidad)
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(5, "Creación incorrecta de servicios (validaciones estrictas)")
    _crear_servicio_seguro(
        sistema,
        lambda: ReservaSala(
            id_entidad="SRV-ERR-01",
            nombre="Sala Tarifa Negativa",
            tarifa_base=-50000.0,  # Tarifa negativa inválida
            capacidad_maxima=15,
        ),
        "Sala con tarifa negativa",
    )
    _crear_servicio_seguro(
        sistema,
        lambda: AlquilerEquipo(
            id_entidad="SRV-ERR-02",
            nombre="Proyector 4K",
            tarifa_base=30000.0,
            categoria_equipo="",  # Parámetro obligatorio faltante
            unidades_disponibles=3,
        ),
        "Equipo sin categoría",
    )
    _crear_servicio_seguro(
        sistema,
        lambda: AsesoriaEspecializada(
            id_entidad="SRV-ERR-03",
            nombre="Asesoría Modalidad Inválida",
            tarifa_base=95000.0,
            area_especialidad="Seguridad Informática",
            nivel_consultor="senior",
            modalidad="telepatica",  # Modalidad no permitida
        ),
        "Asesoría con modalidad inválida",
    )

    # -------------------------------------------------------------------------
    # OPERACIÓN 06: Polimorfismo y métodos sobrecargados (calcular_costo y cotizar)
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(6, "Demostración de polimorfismo y sobrecarga de métodos")
    for servicio in sistema.servicios[:3]:
        # Polimorfismo: cada servicio responde según su propia implementación sobrescrita
        print(f"  -> {servicio.describir_servicio()}")
        # Sobrecarga de calcular_costo con diferentes combinaciones de parámetros
        costo_base = servicio.calcular_costo(3)
        costo_iva = servicio.calcular_costo(3, 0.19)
        costo_desc_iva = servicio.calcular_costo(3, 0.19, 0.10)
        # Sobrecarga dinámica con @singledispatchmethod en cotizar()
        cot_tupla = servicio.cotizar((3, 0.15))
        cot_dicc = servicio.cotizar(
            {"duracion": 3, "impuesto": 0.19, "descuento": 0.10, "recargo_adicional": 15000.0}
        )
        print(
            f"     calcular_costo(3h)={costo_base:,.2f} | con IVA(19%)={costo_iva:,.2f} | "
            f"IVA+Desc(10%)={costo_desc_iva:,.2f}"
        )
        print(
            f"     cotizar((3, 0.15))={cot_tupla:,.2f} | cotizar(dict completo)={cot_dicc:,.2f}"
        )
        sistema.logs.registrar_info(
            f"Cotización polimórfica ejecutada para {servicio.id_entidad}: "
            f"base=${costo_base:,.2f}, completa=${cot_dicc:,.2f}"
        )

    # -------------------------------------------------------------------------
    # OPERACIÓN 07: Reserva exitosa de sala (creación -> confirmación -> procesamiento)
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(7, "Reserva exitosa de sala con confirmación y procesamiento")
    res_sala = sistema.crear_reserva(
        id_reserva="RES-001",
        id_cliente="CLI-001",
        id_servicio="SRV-SAL-01",
        duracion=4,
        parametros_adicionales={"asistentes": 18},
    )
    if res_sala:
        sistema.confirmar_reserva("RES-001")
        total_sala = sistema.procesar_reserva("RES-001", impuesto=0.19, descuento=0.05)
        print(f"  [OK] {res_sala.obtener_resumen()} (Procesada: ${total_sala:,.2f})")

    # -------------------------------------------------------------------------
    # OPERACIÓN 08: Reserva exitosa de alquiler de equipos con descuento corporativo
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(8, "Reserva exitosa de alquiler de equipos con descuento")
    res_equipo = sistema.crear_reserva(
        id_reserva="RES-002",
        id_cliente="CLI-002",
        id_servicio="SRV-EQU-01",
        duracion=10,
        parametros_adicionales={"cantidad": 2},
    )
    if res_equipo:
        sistema.confirmar_reserva("RES-002")
        total_equipo = sistema.procesar_reserva("RES-002", impuesto=0.19, descuento=0.10)
        print(f"  [OK] {res_equipo.obtener_resumen()} (Procesada: ${total_equipo:,.2f})")

    # -------------------------------------------------------------------------
    # OPERACIÓN 09: Reserva exitosa de asesoría especializada
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(9, "Reserva exitosa de asesoría especializada presencial")
    res_asesoria = sistema.crear_reserva(
        id_reserva="RES-003",
        id_cliente="CLI-001",
        id_servicio="SRV-ASE-01",
        duracion=6,
    )
    if res_asesoria:
        sistema.confirmar_reserva("RES-003")
        total_asesoria = sistema.procesar_reserva(
            "RES-003",
            impuesto=0.19,
            descuento=0.0,
            recargo_adicional=20000.0,
        )
        print(f"  [OK] {res_asesoria.obtener_resumen()} (Procesada: ${total_asesoria:,.2f})")

    # -------------------------------------------------------------------------
    # OPERACIÓN 10: Intento de reserva fallido (servicio no disponible y cliente inactivo)
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(10, "Reservas fallidas por servicio no disponible y cliente inactivo")
    res_no_disp = sistema.crear_reserva(
        id_reserva="RES-004",
        id_cliente="CLI-001",
        id_servicio="SRV-SAL-02",  # Auditorio marcado como disponible=False
        duracion=3,
    )
    print(f"  [ERROR CONTROLADO] Reserva en servicio no disponible retornó: {res_no_disp}")

    res_cli_inactivo = sistema.crear_reserva(
        id_reserva="RES-005",
        id_cliente="CLI-003",  # Cliente marcado como activo=False
        id_servicio="SRV-SAL-01",
        duracion=2,
    )
    print(f"  [ERROR CONTROLADO] Reserva de cliente inactivo retornó: {res_cli_inactivo}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 11: Intento de reserva fallido con encadenamiento de excepciones
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(11, "Reserva fallida por parámetros inválidos (excepción encadenada)")
    res_aforo_excedido = sistema.crear_reserva(
        id_reserva="RES-006",
        id_cliente="CLI-002",
        id_servicio="SRV-SAL-01",
        duracion=4,
        parametros_adicionales={"asistentes": 60},  # Supera capacidad máxima de 25
    )
    print(f"  [ERROR CONTROLADO] Reserva con aforo excedido retornó: {res_aforo_excedido}")

    res_duracion_invalida = sistema.crear_reserva(
        id_reserva="RES-007",
        id_cliente="CLI-002",
        id_servicio="SRV-ASE-01",
        duracion=99,  # Supera el máximo de 40 horas para asesorías
    )
    print(f"  [ERROR CONTROLADO] Reserva con duración fuera de rango retornó: {res_duracion_invalida}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 12: Cancelación válida y operaciones no permitidas sobre estados
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(12, "Cancelación controlada y operaciones no permitidas por estado")
    res_cancelable = sistema.crear_reserva(
        id_reserva="RES-008",
        id_cliente="CLI-002",
        id_servicio="SRV-SAL-01",
        duracion=2,
    )
    if res_cancelable:
        cancelada = sistema.cancelar_reserva("RES-008", "Cambio de agenda del comité directivo")
        print(f"  [OK] Cancelación de RES-008: {cancelada} -> {res_cancelable.obtener_resumen()}")
        # Intento prohibido: confirmar una reserva que ya está CANCELADA
        reconfirmar = sistema.confirmar_reserva("RES-008")
        print(f"  [ERROR CONTROLADO] Intentar confirmar reserva CANCELADA retornó: {reconfirmar}")

    # Intento prohibido: cancelar una reserva ya PROCESADA (RES-001)
    cancelar_procesada = sistema.cancelar_reserva("RES-001", "Intento tardío de anulación")
    print(f"  [ERROR CONTROLADO] Intentar cancelar reserva PROCESADA retornó: {cancelar_procesada}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 13: Error de cálculo inconsistente encadenado durante el procesamiento
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(13, "Error de cálculo financiero inconsistente (descuento >= 100%)")
    res_calc = sistema.crear_reserva(
        id_reserva="RES-009",
        id_cliente="CLI-001",
        id_servicio="SRV-EQU-01",
        duracion=5,
    )
    if res_calc:
        sistema.confirmar_reserva("RES-009")
        # Descuento del 120% (1.20) dispara CalculoInconsistenteError encadenado
        resultado_inconsistente = sistema.procesar_reserva("RES-009", impuesto=0.19, descuento=1.20)
        print(
            f"  [ERROR CONTROLADO] Procesamiento con descuento 120% retornó: {resultado_inconsistente}"
        )
        # Se demuestra recuperación inmediata procesando correctamente la misma reserva
        resultado_recuperado = sistema.procesar_reserva("RES-009", impuesto=0.19, descuento=0.15)
        print(
            f"  [RECUPERACIÓN OK] RES-009 reprocesada válidamente con 15% desc: "
            f"${resultado_recuperado:,.2f}"
        )

    # -------------------------------------------------------------------------
    # OPERACIÓN 14: Consulta de entidad inexistente y reporte final consolidado
    # -------------------------------------------------------------------------
    _imprimir_titulo_operacion(14, "Manejo de entidad inexistente y reporte final del sistema")
    try:
        # Intento explícito de búsqueda con try/except para evidenciar estabilidad
        sistema.buscar_cliente("CLI-999")
    except ErrorSistemaSoftwareFJ as error:
        sistema.logs.registrar_error("Consulta directa de cliente inexistente", error)
        print(f"  [ERROR CONTROLADO] Búsqueda CLI-999 capturada sin fallo: {error}")

    # Se imprime el resumen consolidado demostrando que la aplicación terminó intacta
    reporte = sistema.obtener_reporte_general()
    print("\n" + "-" * 78)
    print("RESUMEN FINAL DE EJECUCIÓN - SOFTWARE FJ")
    print("-" * 78)
    print(f"  Clientes válidos en memoria : {reporte['total_clientes']}")
    print(f"  Servicios válidos en memoria: {reporte['total_servicios']}")
    print(f"  Reservas creadas en memoria : {reporte['total_reservas']}")
    print(f"  Total facturado acumulado   : ${reporte['total_facturado']:,.2f} COP")
    print(
        f"  Eventos registrados en log  : {reporte['estadisticas_logs']['total']} "
        f"(INFO={reporte['estadisticas_logs']['info']}, "
        f"WARN={reporte['estadisticas_logs']['advertencias']}, "
        f"ERROR={reporte['estadisticas_logs']['errores']})"
    )
    print(f"  Archivo de logs generado    : {sistema.logs.ruta_archivo.resolve()}")
    print("-" * 78)
    sistema.logs.registrar_info("Simulación de 14 operaciones finalizada sin interrupciones.")
    return sistema
