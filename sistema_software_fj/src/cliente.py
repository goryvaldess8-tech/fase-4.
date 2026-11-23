"""
Módulo que define la clase Cliente para el sistema de gestión de Software FJ.

Implementa herencia desde Entidad, encapsulación estricta de datos personales
mediante propiedades privadas y validaciones rigurosas de formato y dominio.
"""

import re
from typing import Any

from src.entidad import Entidad
from src.excepciones import DatosInvalidosError, ParametroFaltanteError

# Expresión regular estándar para validar correos electrónicos válidos
PATRON_CORREO = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
# Expresión regular para validar documentos de identidad numéricos (6 a 15 dígitos)
PATRON_DOCUMENTO = re.compile(r"^\d{6,15}$")
# Expresión regular para validar números telefónicos (7 a 15 dígitos, con '+' opcional)
PATRON_TELEFONO = re.compile(r"^\+?\d{7,15}$")


class Cliente(Entidad):
    """
    Representa a un cliente registrado en Software FJ.

    Encapsula su nombre completo, documento de identidad, correo electrónico,
    teléfono de contacto y estado de actividad, aplicando validaciones estrictas
    tanto al instanciar el objeto como al modificar cualquiera de sus atributos.
    """

    def __init__(
        self,
        id_entidad: str,
        nombre_completo: str,
        documento: str,
        correo: str,
        telefono: str,
        activo: bool = True,
    ) -> None:
        # Se invoca el constructor de la clase abstracta padre Entidad
        super().__init__(id_entidad)
        # Se inicializan los atributos privados usando sus setters para validar todo
        self.__nombre_completo: str = ""
        self.__documento: str = ""
        self.__correo: str = ""
        self.__telefono: str = ""
        self.__activo: bool = True

        # Asignación controlada a través de las propiedades encapsuladas
        self.nombre_completo = nombre_completo
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        self.activo = activo

        # Se ejecuta la validación integral del objeto recién construido
        self.validar()

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del cliente."""
        return self.__nombre_completo

    @nombre_completo.setter
    def nombre_completo(self, valor: str) -> None:
        """Valida y asigna el nombre completo del cliente."""
        # Se verifica que el nombre no sea nulo ni vacío
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                "El nombre completo del cliente es obligatorio.",
                detalles={"campo": "nombre_completo"},
            )
        # Se comprueba que sea una cadena de texto
        if not isinstance(valor, str):
            raise DatosInvalidosError(
                "El nombre completo debe ser una cadena de texto.",
                detalles={"campo": "nombre_completo", "tipo": type(valor).__name__},
            )
        # Se eliminan espacios redundantes entre palabras
        nombre_limpio = " ".join(valor.strip().split())
        # Se verifica longitud mínima y ausencia de dígitos numéricos en el nombre
        if len(nombre_limpio) < 3 or any(caracter.isdigit() for caracter in nombre_limpio):
            raise DatosInvalidosError(
                "El nombre completo debe tener al menos 3 caracteres y no contener números.",
                detalles={"campo": "nombre_completo", "valor": valor},
            )
        self.__nombre_completo = nombre_limpio

    @property
    def documento(self) -> str:
        """Retorna el número de documento de identidad del cliente."""
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        """Valida y asigna el documento de identidad."""
        # Se valida presencia del parámetro obligatorio
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                "El documento de identidad del cliente es obligatorio.",
                detalles={"campo": "documento"},
            )
        # Se verifica que el documento llegue como cadena de texto
        if not isinstance(valor, str):
            raise DatosInvalidosError(
                "El documento de identidad debe ingresarse como texto numérico.",
                detalles={"campo": "documento", "tipo": type(valor).__name__},
            )
        doc_limpio = valor.strip()
        # Se comprueba el patrón de 6 a 15 dígitos exactos
        if not PATRON_DOCUMENTO.match(doc_limpio):
            raise DatosInvalidosError(
                "El documento debe contener únicamente entre 6 y 15 dígitos.",
                detalles={"campo": "documento", "valor": doc_limpio},
            )
        self.__documento = doc_limpio

    @property
    def correo(self) -> str:
        """Retorna el correo electrónico encapsulado del cliente."""
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Valida el formato del correo electrónico y lo guarda en minúsculas."""
        # Se verifica que el correo no esté vacío o nulo
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                "El correo electrónico del cliente es obligatorio.",
                detalles={"campo": "correo"},
            )
        if not isinstance(valor, str):
            raise DatosInvalidosError(
                "El correo electrónico debe ser una cadena de texto.",
                detalles={"campo": "correo", "tipo": type(valor).__name__},
            )
        correo_limpio = valor.strip().lower()
        # Se aplica la expresión regular de correo electrónico válido
        if not PATRON_CORREO.match(correo_limpio):
            raise DatosInvalidosError(
                "El formato del correo electrónico no es válido.",
                detalles={"campo": "correo", "valor": correo_limpio},
            )
        self.__correo = correo_limpio

    @property
    def telefono(self) -> str:
        """Retorna el número telefónico de contacto del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Valida y almacena el número telefónico del cliente."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                "El número telefónico del cliente es obligatorio.",
                detalles={"campo": "telefono"},
            )
        if not isinstance(valor, str):
            raise DatosInvalidosError(
                "El número telefónico debe ser una cadena de texto.",
                detalles={"campo": "telefono", "tipo": type(valor).__name__},
            )
        # Se eliminan espacios y guiones para validar los dígitos puros
        tel_limpio = valor.strip().replace(" ", "").replace("-", "")
        if not PATRON_TELEFONO.match(tel_limpio):
            raise DatosInvalidosError(
                "El teléfono debe contener entre 7 y 15 dígitos (puede iniciar con '+').",
                detalles={"campo": "telefono", "valor": valor},
            )
        self.__telefono = tel_limpio

    @property
    def activo(self) -> bool:
        """Indica si el cliente se encuentra habilitado para realizar reservas."""
        return self.__activo

    @activo.setter
    def activo(self, valor: bool) -> None:
        """Asigna el estado booleano de actividad del cliente."""
        if not isinstance(valor, bool):
            raise DatosInvalidosError(
                "El estado 'activo' del cliente debe ser un valor booleano (True/False).",
                detalles={"campo": "activo", "valor": valor},
            )
        self.__activo = valor

    def validar(self) -> bool:
        """Verifica de manera integral que todos los datos del cliente sean válidos."""
        # Se confirma que todos los campos obligatorios tengan contenido íntegro
        if not all([self.__nombre_completo, self.__documento, self.__correo, self.__telefono]):
            raise ParametroFaltanteError(
                "El cliente contiene campos obligatorios incompletos.",
                detalles={"id_entidad": self.id_entidad},
            )
        return True

    def obtener_resumen(self) -> str:
        """Genera una línea descriptiva del cliente para reportes y consola."""
        estado = "ACTIVO" if self.__activo else "INACTIVO"
        return (
            f"Cliente [{self.id_entidad}] {self.__nombre_completo} | "
            f"Doc: {self.__documento} | Correo: {self.__correo} | "
            f"Tel: {self.__telefono} | Estado: {estado}"
        )

    def a_diccionario(self) -> dict[str, Any]:
        """Serializa los datos del cliente en un diccionario estructurado."""
        return {
            "id_entidad": self.id_entidad,
            "nombre_completo": self.__nombre_completo,
            "documento": self.__documento,
            "correo": self.__correo,
            "telefono": self.__telefono,
            "activo": self.__activo,
            "fecha_creacion": self.fecha_creacion.isoformat(timespec="seconds"),
        }
