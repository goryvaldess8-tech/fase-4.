"""
Paquete principal del Sistema Integral de Gestión de Clientes, Servicios y Reservas
de la empresa Software FJ.

Curso: Programación (Código: 213023) - UNAD
Fase 4: Componente Práctico - Prácticas Simuladas
Autor: Rodrigo Valdés Vásquez
"""

# Se exponen las clases principales del paquete para facilitar su importación
from src.cliente import Cliente
from src.entidad import Entidad
from src.excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    EntidadNoEncontradaError,
    ErrorSistemaSoftwareFJ,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    RegistroDuplicadoError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from src.gestor_logs import GestorLogs
from src.gestor_sistema import SistemaGestionSoftwareFJ
from src.reserva import EstadoReserva, Reserva
from src.servicio import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    ReservaSala,
    Servicio,
)

# Lista explícita de símbolos exportados por el paquete src
__all__ = [
    "Entidad",
    "Cliente",
    "Servicio",
    "ReservaSala",
    "AlquilerEquipo",
    "AsesoriaEspecializada",
    "Reserva",
    "EstadoReserva",
    "GestorLogs",
    "SistemaGestionSoftwareFJ",
    "ErrorSistemaSoftwareFJ",
    "DatosInvalidosError",
    "ParametroFaltanteError",
    "OperacionNoPermitidaError",
    "ReservaInvalidaError",
    "ServicioNoDisponibleError",
    "CalculoInconsistenteError",
    "EntidadNoEncontradaError",
    "RegistroDuplicadoError",
]
