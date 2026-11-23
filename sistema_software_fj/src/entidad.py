"""
Módulo que define la clase abstracta base Entidad para el sistema Software FJ.

Aplica los principios de abstracción y encapsulación al establecer atributos
y contratos comunes que todas las entidades del dominio (Cliente, Servicio,
Reserva) deben heredar e implementar obligatoriamente.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from src.excepciones import DatosInvalidosError, ParametroFaltanteError


class Entidad(ABC):
    """
    Clase abstracta que representa cualquier entidad general del sistema.

    Obliga a las clases hijas a implementar validación interna, generación
    de resúmenes legibles y serialización a diccionario.
    """

    def __init__(self, id_entidad: str) -> None:
        # Se valida el identificador antes de almacenarlo en el atributo privado
        self.__id_entidad: str = self.__validar_id(id_entidad)
        # Se registra automáticamente la fecha y hora exacta de creación
        self.__fecha_creacion: datetime = datetime.now()

    @staticmethod
    def __validar_id(id_entidad: str) -> str:
        """Valida que el identificador de la entidad sea una cadena no vacía."""
        # Se verifica si el parámetro es nulo o está completamente vacío
        if id_entidad is None or (isinstance(id_entidad, str) and not id_entidad.strip()):
            raise ParametroFaltanteError(
                "El identificador de la entidad es obligatorio y no puede estar vacío.",
                detalles={"campo": "id_entidad"},
            )
        # Se comprueba que el tipo recibido corresponda estrictamente a texto (str)
        if not isinstance(id_entidad, str):
            raise DatosInvalidosError(
                "El identificador de la entidad debe ser una cadena de texto.",
                detalles={"campo": "id_entidad", "tipo_recibido": type(id_entidad).__name__},
            )
        # Se limpia de espacios laterales y se estandariza en mayúsculas
        id_limpio = id_entidad.strip().upper()
        # Se verifica una longitud mínima razonable para el identificador
        if len(id_limpio) < 3:
            raise DatosInvalidosError(
                "El identificador de la entidad debe tener al menos 3 caracteres.",
                detalles={"campo": "id_entidad", "valor": id_limpio},
            )
        return id_limpio

    @property
    def id_entidad(self) -> str:
        """Retorna el identificador único e inmutable de la entidad."""
        return self.__id_entidad

    @property
    def fecha_creacion(self) -> datetime:
        """Retorna la marca temporal en la que fue instanciada la entidad."""
        return self.__fecha_creacion

    @abstractmethod
    def validar(self) -> bool:
        """
        Ejecuta todas las reglas de validación propias de cada entidad hija.

        Debe retornar True si el estado de la entidad es íntegro o lanzar una
        excepción personalizada si detecta inconsistencias.
        """

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Retorna una cadena descriptiva y legible del estado de la entidad."""

    @abstractmethod
    def a_diccionario(self) -> dict[str, Any]:
        """Convierte los atributos principales de la entidad en un diccionario."""

    def __repr__(self) -> str:
        """Representación técnica útil para depuración y trazas de error."""
        return f"{self.__class__.__name__}(id_entidad='{self.__id_entidad}')"
