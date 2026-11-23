"""
Módulo coordinador SistemaGestionSoftwareFJ.

Administra en memoria las listas internas de clientes, servicios y reservas
sin utilizar ningún motor de base de datos. Cada operación relevante y cada
error detectado se registra automáticamente en el archivo de logs a través
de GestorLogs, manteniendo la aplicación estable en todo momento.
"""

from typing import Any, Optional

from src.cliente import Cliente
from src.excepciones import (
    EntidadNoEncontradaError,
    ErrorSistemaSoftwareFJ,
    RegistroDuplicadoError,
)
from src.gestor_logs import GestorLogs
from src.reserva import Reserva
from src.servicio import Servicio


class SistemaGestionSoftwareFJ:
    """
    Fachada central orientada a objetos para operar la plataforma Software FJ.

    Encapsula las listas internas de objetos (__clientes, __servicios y
    __reservas) y orquesta el manejo robusto de excepciones y auditoría.
    """

    def __init__(self, gestor_logs: Optional[GestorLogs] = None) -> None:
        # Listas internas en memoria (sin base de datos)
        self.__clientes: list[Cliente] = []
        self.__servicios: list[Servicio] = []
        self.__reservas: list[Reserva] = []
        # Se inyecta o crea el gestor de logs para registrar eventos y errores
        self.__logs: GestorLogs = gestor_logs or GestorLogs()
        self.__logs.registrar_info("SistemaGestionSoftwareFJ inicializado en memoria (sin base de datos).")

    @property
    def logs(self) -> GestorLogs:
        """Retorna el gestor de logs asociado al sistema."""
        return self.__logs

    @property
    def clientes(self) -> list[Cliente]:
        """Retorna una copia segura de la lista de clientes registrados."""
        return list(self.__clientes)

    @property
    def servicios(self) -> list[Servicio]:
        """Retorna una copia segura de la lista de servicios registrados."""
        return list(self.__servicios)

    @property
    def reservas(self) -> list[Reserva]:
        """Retorna una copia segura de la lista de reservas registradas."""
        return list(self.__reservas)

    # =========================================================================
    # GESTIÓN DE CLIENTES
    # =========================================================================

    def registrar_cliente(
        self,
        id_entidad: str,
        nombre_completo: str,
        documento: str,
        correo: str,
        telefono: str,
        activo: bool = True,
    ) -> Optional[Cliente]:
        """
        Crea y agrega un nuevo cliente a la lista interna usando try/except/else.

        Ante cualquier error de validación o duplicidad, registra el fallo en el
        log y retorna None sin detener el sistema.
        """
        try:
            # Se construye el objeto Cliente (dispara todas las validaciones del modelo)
            nuevo_cliente = Cliente(
                id_entidad=id_entidad,
                nombre_completo=nombre_completo,
                documento=documento,
                correo=correo,
                telefono=telefono,
                activo=activo,
            )
            # Se valida que no exista otro cliente con el mismo ID o documento
            for existente in self.__clientes:
                if existente.id_entidad == nuevo_cliente.id_entidad:
                    raise RegistroDuplicadoError(
                        f"Ya existe un cliente registrado con el ID '{nuevo_cliente.id_entidad}'.",
                        detalles={"id_entidad": nuevo_cliente.id_entidad},
                    )
                if existente.documento == nuevo_cliente.documento:
                    raise RegistroDuplicadoError(
                        f"Ya existe un cliente registrado con el documento '{nuevo_cliente.documento}'.",
                        detalles={"documento": nuevo_cliente.documento},
                    )
        except ErrorSistemaSoftwareFJ as error:
            # Registro estructurado del error sin interrumpir la ejecución global
            self.__logs.registrar_error(
                f"Fallo al registrar cliente (ID='{id_entidad}')",
                error,
            )
            return None
        else:
            # Bloque else: solo se inserta en la lista si no hubo ninguna excepción
            self.__clientes.append(nuevo_cliente)
            self.__logs.registrar_info(f"Cliente registrado exitosamente: {nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        """Busca un cliente por su identificador único o lanza EntidadNoEncontradaError."""
        id_norm = id_cliente.strip().upper() if isinstance(id_cliente, str) else ""
        for cliente in self.__clientes:
            if cliente.id_entidad == id_norm:
                return cliente
        raise EntidadNoEncontradaError(
            f"No se encontró ningún cliente con el identificador '{id_cliente}'.",
            detalles={"tipo_entidad": "Cliente", "id_buscado": id_cliente},
        )

    # =========================================================================
    # GESTIÓN DE SERVICIOS
    # =========================================================================

    def registrar_servicio(self, servicio: Servicio) -> Optional[Servicio]:
        """
        Registra cualquier servicio polimórfico que herede de Servicio.

        Aplica try/except/else y verifica que no exista un ID duplicado.
        """
        try:
            # Se comprueba que el objeto pertenezca a la jerarquía abstracta Servicio
            if not isinstance(servicio, Servicio):
                raise RegistroDuplicadoError(
                    "El objeto suministrado no es una instancia válida de Servicio.",
                    detalles={"tipo": type(servicio).__name__},
                )
            # Se valida unicidad del identificador del servicio
            for existente in self.__servicios:
                if existente.id_entidad == servicio.id_entidad:
                    raise RegistroDuplicadoError(
                        f"Ya existe un servicio registrado con el ID '{servicio.id_entidad}'.",
                        detalles={"id_entidad": servicio.id_entidad},
                    )
        except ErrorSistemaSoftwareFJ as error:
            self.__logs.registrar_error("Fallo al registrar servicio", error)
            return None
        else:
            self.__servicios.append(servicio)
            self.__logs.registrar_info(f"Servicio registrado: {servicio.obtener_resumen()}")
            return servicio

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        """Busca un servicio por su identificador o lanza EntidadNoEncontradaError."""
        id_norm = id_servicio.strip().upper() if isinstance(id_servicio, str) else ""
        for servicio in self.__servicios:
            if servicio.id_entidad == id_norm:
                return servicio
        raise EntidadNoEncontradaError(
            f"No se encontró ningún servicio con el identificador '{id_servicio}'.",
            detalles={"tipo_entidad": "Servicio", "id_buscado": id_servicio},
        )

    # =========================================================================
    # GESTIÓN DE RESERVAS
    # =========================================================================

    def crear_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion: float,
        parametros_adicionales: Optional[dict[str, Any]] = None,
    ) -> Optional[Reserva]:
        """
        Crea una nueva reserva integrando cliente y servicio mediante try/except/else/finally.

        Si falla la búsqueda, disponibilidad o validación de parámetros, captura la
        excepción (incluyendo su causa encadenada), la registra en el log y retorna None.
        """
        reserva_creada: Optional[Reserva] = None
        try:
            # Verificación de ID de reserva no duplicado
            id_norm = id_reserva.strip().upper() if isinstance(id_reserva, str) else ""
            if any(r.id_entidad == id_norm for r in self.__reservas):
                raise RegistroDuplicadoError(
                    f"Ya existe una reserva con el identificador '{id_norm}'.",
                    detalles={"id_reserva": id_norm},
                )
            # Localización del cliente y del servicio en las listas internas
            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(id_servicio)
            # Creación del objeto Reserva (valida estado, disponibilidad y parámetros)
            reserva_creada = Reserva(
                id_entidad=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                parametros_adicionales=parametros_adicionales,
            )
        except ErrorSistemaSoftwareFJ as error:
            self.__logs.registrar_error(
                f"Fallo al crear reserva (ID='{id_reserva}', Cliente='{id_cliente}', Servicio='{id_servicio}')",
                error,
            )
            return None
        else:
            # Solo se agrega a la lista de reservas si todo resultó exitoso
            self.__reservas.append(reserva_creada)
            self.__logs.registrar_info(f"Reserva creada: {reserva_creada.obtener_resumen()}")
            return reserva_creada
        finally:
            # Bloque finally: deja constancia del cierre de la transacción en memoria
            estado_final = "EXITOSA" if reserva_creada is not None else "FALLIDA (controlada)"
            self.__logs.registrar_info(
                f"Cierre de operación crear_reserva('{id_reserva}'): {estado_final}."
            )

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        """Busca una reserva por su identificador o lanza EntidadNoEncontradaError."""
        id_norm = id_reserva.strip().upper() if isinstance(id_reserva, str) else ""
        for reserva in self.__reservas:
            if reserva.id_entidad == id_norm:
                return reserva
        raise EntidadNoEncontradaError(
            f"No se encontró ninguna reserva con el identificador '{id_reserva}'.",
            detalles={"tipo_entidad": "Reserva", "id_buscado": id_reserva},
        )

    def confirmar_reserva(self, id_reserva: str) -> bool:
        """Confirma una reserva existente con manejo seguro de excepciones."""
        try:
            reserva = self.buscar_reserva(id_reserva)
            reserva.confirmar()
        except ErrorSistemaSoftwareFJ as error:
            self.__logs.registrar_error(f"Fallo al confirmar reserva '{id_reserva}'", error)
            return False
        else:
            self.__logs.registrar_info(f"Reserva confirmada: {reserva.obtener_resumen()}")
            return True

    def cancelar_reserva(self, id_reserva: str, motivo: str) -> bool:
        """Cancela una reserva existente registrando el motivo en el log."""
        try:
            reserva = self.buscar_reserva(id_reserva)
            reserva.cancelar(motivo)
        except ErrorSistemaSoftwareFJ as error:
            self.__logs.registrar_error(f"Fallo al cancelar reserva '{id_reserva}'", error)
            return False
        else:
            self.__logs.registrar_advertencia(
                f"Reserva cancelada [{reserva.id_entidad}] | Motivo: {reserva.motivo_cancelacion}"
            )
            return True

    def procesar_reserva(
        self,
        id_reserva: str,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        recargo_adicional: float = 0.0,
    ) -> Optional[float]:
        """Procesa una reserva confirmada y devuelve el costo total o None si falla."""
        try:
            reserva = self.buscar_reserva(id_reserva)
            total = reserva.procesar(
                impuesto=impuesto,
                descuento=descuento,
                recargo_adicional=recargo_adicional,
            )
        except ErrorSistemaSoftwareFJ as error:
            self.__logs.registrar_error(f"Fallo al procesar reserva '{id_reserva}'", error)
            return None
        else:
            self.__logs.registrar_info(
                f"Reserva procesada [{reserva.id_entidad}] | Total facturado: ${total:,.2f}"
            )
            return total

    def obtener_reporte_general(self) -> dict[str, Any]:
        """Genera un resumen consolidado del estado actual del sistema en memoria."""
        total_facturado = round(sum(r.costo_total for r in self.__reservas), 2)
        return {
            "total_clientes": len(self.__clientes),
            "total_servicios": len(self.__servicios),
            "total_reservas": len(self.__reservas),
            "total_facturado": total_facturado,
            "estadisticas_logs": self.__logs.estadisticas,
        }
