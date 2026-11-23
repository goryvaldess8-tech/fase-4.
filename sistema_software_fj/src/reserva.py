"""
Módulo que define la clase Reserva y la enumeración EstadoReserva.

Integra un objeto Cliente, un objeto Servicio polimórfico, la duración y el
estado del ciclo de vida, implementando confirmación, cancelación y
procesamiento con bloques try/except, try/except/else, try/except/finally y
encadenamiento de excepciones.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from src.cliente import Cliente
from src.entidad import Entidad
from src.excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from src.servicio import Servicio


class EstadoReserva(Enum):
    """Estados posibles del ciclo de vida de una reserva en Software FJ."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"


class Reserva(Entidad):
    """
    Representa una reserva que integra cliente, servicio, duración y estado.

    Garantiza reglas estrictas de negocio: solo clientes activos pueden reservar
    servicios disponibles, y las transiciones de estado están protegidas frente
    a operaciones inválidas o cálculos inconsistentes.
    """

    def __init__(
        self,
        id_entidad: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        parametros_adicionales: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se invoca el constructor padre Entidad para validar el ID de la reserva
        super().__init__(id_entidad)
        # Se valida que el cliente recibido sea una instancia válida de Cliente
        if cliente is None:
            raise ParametroFaltanteError(
                "Toda reserva requiere un cliente asociado.",
                detalles={"campo": "cliente"},
            )
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError(
                "El parámetro 'cliente' debe ser una instancia de la clase Cliente.",
                detalles={"tipo_recibido": type(cliente).__name__},
            )
        # Se verifica que el cliente esté activo antes de permitirle reservar
        if not cliente.activo:
            raise OperacionNoPermitidaError(
                f"El cliente '{cliente.nombre_completo}' se encuentra inactivo y no puede reservar.",
                detalles={"cliente_id": cliente.id_entidad},
            )

        # Se valida que el servicio recibido herede de la clase abstracta Servicio
        if servicio is None:
            raise ParametroFaltanteError(
                "Toda reserva requiere un servicio asociado.",
                detalles={"campo": "servicio"},
            )
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError(
                "El parámetro 'servicio' debe heredar de la clase abstracta Servicio.",
                detalles={"tipo_recibido": type(servicio).__name__},
            )
        # Se comprueba la disponibilidad del servicio usando excepción específica
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' ({servicio.id_entidad}) no está disponible actualmente.",
                detalles={"servicio_id": servicio.id_entidad},
            )

        # Se guardan los parámetros opcionales para la validación polimórfica
        self.__parametros_adicionales: dict[str, Any] = parametros_adicionales or {}

        # Se validan duración y parámetros específicos encadenando la excepción si falla
        try:
            servicio.validar_parametros(duracion, **self.__parametros_adicionales)
        except DatosInvalidosError as error_param:
            # Encadenamiento explícito: el error de dominio se envuelve en ReservaInvalidaError
            raise ReservaInvalidaError(
                f"Parámetros inválidos al crear la reserva '{self.id_entidad}' para '{servicio.nombre}'.",
                detalles={"duracion": duracion, "servicio_id": servicio.id_entidad},
            ) from error_param

        # Asignación de atributos privados encapsulados
        self.__cliente: Cliente = cliente
        self.__servicio: Servicio = servicio
        self.__duracion: float = float(duracion)
        self.__estado: EstadoReserva = EstadoReserva.PENDIENTE
        self.__costo_total: float = 0.0
        self.__motivo_cancelacion: Optional[str] = None
        self.__fecha_actualizacion: datetime = self.fecha_creacion
        self.__historial_eventos: list[str] = [
            f"Reserva creada en estado {self.__estado.value}."
        ]

        # Validación integral del objeto construido
        self.validar()

    @property
    def cliente(self) -> Cliente:
        """Retorna el cliente titular de la reserva."""
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        """Retorna el servicio polimórfico reservado."""
        return self.__servicio

    @property
    def duracion(self) -> float:
        """Retorna la duración contratada en horas."""
        return self.__duracion

    @property
    def estado(self) -> EstadoReserva:
        """Retorna el estado actual del ciclo de vida de la reserva."""
        return self.__estado

    @property
    def costo_total(self) -> float:
        """Retorna el costo total calculado tras procesar la reserva."""
        return self.__costo_total

    @property
    def motivo_cancelacion(self) -> Optional[str]:
        """Retorna el motivo registrado si la reserva fue cancelada."""
        return self.__motivo_cancelacion

    @property
    def historial_eventos(self) -> list[str]:
        """Retorna una copia segura del historial interno de cambios de estado."""
        return list(self.__historial_eventos)

    def confirmar(self) -> EstadoReserva:
        """
        Confirma una reserva que se encuentra en estado PENDIENTE.

        Utiliza un bloque try/except/else para garantizar que el cambio de estado
        y la auditoría se ejecuten únicamente si todas las validaciones pasan.
        """
        try:
            # Solo una reserva PENDIENTE puede pasar a estado CONFIRMADA
            if self.__estado != EstadoReserva.PENDIENTE:
                raise OperacionNoPermitidaError(
                    f"No se puede confirmar la reserva '{self.id_entidad}' desde el estado {self.__estado.value}.",
                    detalles={"reserva_id": self.id_entidad, "estado_actual": self.__estado.value},
                )
            # Se revalida la disponibilidad del servicio justo antes de confirmar
            if not self.__servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.__servicio.nombre}' dejó de estar disponible antes de confirmar.",
                    detalles={"servicio_id": self.__servicio.id_entidad},
                )
        except ServicioNoDisponibleError as error_disp:
            # Se encadena el error de disponibilidad como falla de reserva
            raise ReservaInvalidaError(
                f"Falló la confirmación de la reserva '{self.id_entidad}' por indisponibilidad.",
                detalles={"reserva_id": self.id_entidad},
            ) from error_disp
        else:
            # El bloque else solo corre si no ocurrió ninguna excepción en el try
            self.__estado = EstadoReserva.CONFIRMADA
            self.__fecha_actualizacion = datetime.now()
            self.__historial_eventos.append("Reserva confirmada correctamente.")
            return self.__estado

    def cancelar(self, motivo: str = "Cancelación solicitada por el cliente") -> EstadoReserva:
        """
        Cancela una reserva si todavía no ha sido procesada ni cancelada previamente.
        """
        # Se valida que el motivo de cancelación no llegue vacío
        if motivo is None or not isinstance(motivo, str) or not motivo.strip():
            raise ParametroFaltanteError(
                "Debe especificarse un motivo válido para cancelar la reserva.",
                detalles={"reserva_id": self.id_entidad},
            )
        # No se permite cancelar una reserva que ya fue procesada/facturada
        if self.__estado == EstadoReserva.PROCESADA:
            raise OperacionNoPermitidaError(
                f"No es posible cancelar la reserva '{self.id_entidad}' porque ya fue PROCESADA.",
                detalles={"reserva_id": self.id_entidad, "estado_actual": self.__estado.value},
            )
        # No se permite cancelar dos veces la misma reserva
        if self.__estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError(
                f"La reserva '{self.id_entidad}' ya se encuentra CANCELADA.",
                detalles={"reserva_id": self.id_entidad, "estado_actual": self.__estado.value},
            )

        # Se actualiza el estado y se registra el motivo de la cancelación
        self.__estado = EstadoReserva.CANCELADA
        self.__motivo_cancelacion = motivo.strip()
        self.__fecha_actualizacion = datetime.now()
        self.__historial_eventos.append(f"Reserva cancelada. Motivo: {self.__motivo_cancelacion}")
        return self.__estado

    def procesar(
        self,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """
        Procesa la reserva confirmada, calculando su costo final de forma polimórfica.

        Implementa try/except/finally y encadenamiento de excepciones para asegurar
        que el historial de auditoría siempre registre el resultado del intento.
        """
        procesamiento_exitoso = False
        try:
            # Regla de negocio: una reserva debe estar CONFIRMADA antes de procesarse
            if self.__estado != EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"La reserva '{self.id_entidad}' debe estar CONFIRMADA para procesarse "
                    f"(estado actual: {self.__estado.value}).",
                    detalles={"reserva_id": self.id_entidad, "estado_actual": self.__estado.value},
                )
            # Se invoca el método polimórfico y sobrecargado calcular_costo del servicio
            costo_calculado = self.__servicio.calcular_costo(
                duracion=self.__duracion,
                impuesto=impuesto,
                descuento=descuento,
                recargo_adicional=recargo_adicional,
            )
            # Se asigna el costo final y se transita al estado PROCESADA
            self.__costo_total = costo_calculado
            self.__estado = EstadoReserva.PROCESADA
            procesamiento_exitoso = True
            return self.__costo_total
        except CalculoInconsistenteError as error_calc:
            # Encadenamiento de excepción ante error financiero durante el procesamiento
            raise CalculoInconsistenteError(
                f"Error financiero al procesar la reserva '{self.id_entidad}'.",
                detalles={
                    "reserva_id": self.id_entidad,
                    "impuesto": impuesto,
                    "descuento": descuento,
                    "recargo_adicional": recargo_adicional,
                },
            ) from error_calc
        finally:
            # El bloque finally siempre deja constancia del intento de procesamiento
            self.__fecha_actualizacion = datetime.now()
            if procesamiento_exitoso:
                self.__historial_eventos.append(
                    f"Reserva procesada exitosamente. Total: ${self.__costo_total:,.2f}"
                )
            else:
                self.__historial_eventos.append(
                    f"Intento fallido de procesamiento (estado mantenido: {self.__estado.value})."
                )

    def validar(self) -> bool:
        """Valida la coherencia general de la reserva y sus referencias internas."""
        if self.__duracion <= 0:
            raise ReservaInvalidaError(
                "La duración de la reserva debe ser mayor que cero.",
                detalles={"reserva_id": self.id_entidad, "duracion": self.__duracion},
            )
        return True

    def obtener_resumen(self) -> str:
        """Retorna un resumen legible del estado actual y monto de la reserva."""
        monto = f"${self.__costo_total:,.2f}" if self.__costo_total > 0 else "Pendiente de cálculo"
        return (
            f"Reserva [{self.id_entidad}] Cliente: {self.__cliente.nombre_completo} | "
            f"Servicio: {self.__servicio.nombre} | Duración: {self.__duracion:g}h | "
            f"Estado: {self.__estado.value} | Total: {monto}"
        )

    def a_diccionario(self) -> dict[str, Any]:
        """Serializa los atributos de la reserva en un diccionario estructurado."""
        return {
            "id_entidad": self.id_entidad,
            "cliente_id": self.__cliente.id_entidad,
            "servicio_id": self.__servicio.id_entidad,
            "duracion": self.__duracion,
            "estado": self.__estado.value,
            "costo_total": self.__costo_total,
            "motivo_cancelacion": self.__motivo_cancelacion,
            "fecha_creacion": self.fecha_creacion.isoformat(timespec="seconds"),
            "fecha_actualizacion": self.__fecha_actualizacion.isoformat(timespec="seconds"),
        }
