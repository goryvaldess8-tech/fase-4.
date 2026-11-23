"""
Módulo de excepciones personalizadas para el sistema de gestión de Software FJ.

Define una jerarquía clara de excepciones orientadas a objetos que permite
clasificar, capturar, encadenar y registrar todos los errores posibles sin
interrumpir la ejecución del sistema.
"""

from typing import Any, Optional


class ErrorSistemaSoftwareFJ(Exception):
    """
    Excepción base personalizada para todos los errores del sistema Software FJ.

    Permite almacenar un código identificador del error y detalles contextuales
    adicionales para facilitar el registro en logs y el diagnóstico técnico.
    """

    def __init__(
        self,
        mensaje: str,
        codigo: str = "ERR_SISTEMA",
        detalles: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se inicializa la clase base Exception con el mensaje descriptivo
        super().__init__(mensaje)
        # Se almacena el mensaje principal del error
        self.mensaje: str = mensaje
        # Se asigna un código único que categoriza el tipo de fallo
        self.codigo: str = codigo
        # Se guarda un diccionario opcional con datos de contexto para auditoría
        self.detalles: dict[str, Any] = detalles or {}

    def __str__(self) -> str:
        """Retorna una representación legible del error con su código y detalles."""
        # Si existen detalles adicionales, se anexan al texto formateado
        if self.detalles:
            return f"[{self.codigo}] {self.mensaje} | Detalles: {self.detalles}"
        # Si no hay detalles, se retorna únicamente el código y el mensaje
        return f"[{self.codigo}] {self.mensaje}"


class DatosInvalidosError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando un dato ingresado no cumple el tipo, formato o rango válido."""

    def __init__(
        self,
        mensaje: str,
        detalles: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se delega la construcción al padre con el código específico de datos inválidos
        super().__init__(mensaje, codigo="ERR_DATOS_INVALIDOS", detalles=detalles)


class ParametroFaltanteError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando falta un parámetro obligatorio o llega vacío/nulo."""

    def __init__(
        self,
        mensaje: str,
        detalles: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se asigna el código correspondiente a parámetros requeridos ausentes
        super().__init__(mensaje, codigo="ERR_PARAMETRO_FALTANTE", detalles=detalles)


class OperacionNoPermitidaError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando se intenta ejecutar una acción prohibida por el estado actual."""

    def __init__(
        self,
        mensaje: str,
        detalles: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se asigna el código de operación restringida por reglas de negocio
        super().__init__(mensaje, codigo="ERR_OPERACION_NO_PERMITIDA", detalles=detalles)


class ReservaInvalidaError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando una solicitud o transición de reserva resulta inconsistente."""

    def __init__(
        self,
        mensaje: str,
        detalles: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se asigna el código específico para fallos en la gestión de reservas
        super().__init__(mensaje, codigo="ERR_RESERVA_INVALIDA", detalles=detalles)


class ServicioNoDisponibleError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando el servicio solicitado está inactivo o sin disponibilidad."""

    def __init__(
        self,
        mensaje: str,
        detalles: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se asigna el código de indisponibilidad del servicio
        super().__init__(mensaje, codigo="ERR_SERVICIO_NO_DISPONIBLE", detalles=detalles)


class CalculoInconsistenteError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando un cálculo financiero arroja parámetros o resultados inválidos."""

    def __init__(
        self,
        mensaje: str,
        detalles: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se asigna el código de inconsistencia numérica o tarifaria
        super().__init__(mensaje, codigo="ERR_CALCULO_INCONSISTENTE", detalles=detalles)


class EntidadNoEncontradaError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando no se encuentra un cliente, servicio o reserva solicitada."""

    def __init__(
        self,
        mensaje: str,
        detalles: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se asigna el código de búsqueda sin resultados
        super().__init__(mensaje, codigo="ERR_ENTIDAD_NO_ENCONTRADA", detalles=detalles)


class RegistroDuplicadoError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando se intenta registrar una entidad con identificador único repetido."""

    def __init__(
        self,
        mensaje: str,
        detalles: Optional[dict[str, Any]] = None,
    ) -> None:
        # Se asigna el código de duplicidad en las listas internas del sistema
        super().__init__(mensaje, codigo="ERR_REGISTRO_DUPLICADO", detalles=detalles)
