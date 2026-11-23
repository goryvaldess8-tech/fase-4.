"""
Módulo de servicios de Software FJ: clase abstracta Servicio y servicios especializados.

Implementa:
- Abstracción mediante la clase abstracta Servicio(Entidad, ABC).
- Herencia y polimorfismo en tres servicios especializados:
  1. ReservaSala
  2. AlquilerEquipo
  3. AsesoriaEspecializada
- Sobrecarga de métodos mediante parámetros opcionales tipados con @overload
  en calcular_costo() y despacho múltiple en tiempo de ejecución con
  @singledispatchmethod en cotizar().
"""

from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Any, Optional, overload

from src.entidad import Entidad
from src.excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ParametroFaltanteError,
)


class Servicio(Entidad, ABC):
    """
    Clase abstracta base para todos los servicios ofrecidos por Software FJ.

    Define la interfaz polimórfica que cada tipo de servicio debe sobrescribir
    para calcular costos, describir sus características y validar parámetros.
    """

    def __init__(
        self,
        id_entidad: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        # Se inicializa la clase padre Entidad con el identificador único
        super().__init__(id_entidad)
        # Atributos privados encapsulados
        self.__nombre: str = ""
        self.__tarifa_base: float = 0.0
        self.__disponible: bool = True

        # Se asignan usando los setters con validación estricta
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    @property
    def nombre(self) -> str:
        """Retorna el nombre comercial del servicio."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y asigna el nombre del servicio."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                "El nombre del servicio es obligatorio.",
                detalles={"campo": "nombre"},
            )
        if not isinstance(valor, str):
            raise DatosInvalidosError(
                "El nombre del servicio debe ser una cadena de texto.",
                detalles={"campo": "nombre", "tipo": type(valor).__name__},
            )
        nombre_limpio = valor.strip()
        if len(nombre_limpio) < 3:
            raise DatosInvalidosError(
                "El nombre del servicio debe contener al menos 3 caracteres.",
                detalles={"campo": "nombre", "valor": nombre_limpio},
            )
        self.__nombre = nombre_limpio

    @property
    def tarifa_base(self) -> float:
        """Retorna la tarifa base por hora del servicio en pesos colombianos (COP)."""
        return self.__tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float) -> None:
        """Valida que la tarifa base sea un número estrictamente positivo."""
        if valor is None:
            raise ParametroFaltanteError(
                "La tarifa base del servicio es obligatoria.",
                detalles={"campo": "tarifa_base"},
            )
        # Se excluye bool explícitamente porque en Python bool hereda de int
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatosInvalidosError(
                "La tarifa base debe ser un valor numérico.",
                detalles={"campo": "tarifa_base", "valor": valor},
            )
        if valor <= 0:
            raise DatosInvalidosError(
                "La tarifa base del servicio debe ser mayor que cero.",
                detalles={"campo": "tarifa_base", "valor": valor},
            )
        self.__tarifa_base = round(float(valor), 2)

    @property
    def disponible(self) -> bool:
        """Indica si el servicio está actualmente disponible para reservar."""
        return self.__disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        """Actualiza la disponibilidad booleana del servicio."""
        if not isinstance(valor, bool):
            raise DatosInvalidosError(
                "La disponibilidad del servicio debe ser booleana (True/False).",
                detalles={"campo": "disponible", "valor": valor},
            )
        self.__disponible = valor

    def _aplicar_ajustes_financieros(
        self,
        subtotal: float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """
        Aplica descuentos, recargos e impuestos validando la consistencia matemática.

        Centraliza la verificación financiera para evitar totales negativos,
        descuentos fuera de rango o impuestos inválidos.
        """
        # Se valida que los parámetros financieros sean numéricos y no booleanos
        for nombre_param, val in [
            ("impuesto", impuesto),
            ("descuento", descuento),
            ("recargo_adicional", recargo_adicional),
        ]:
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                raise CalculoInconsistenteError(
                    f"El parámetro financiero '{nombre_param}' debe ser numérico.",
                    detalles={"parametro": nombre_param, "valor": val},
                )

        # El subtotal debe ser positivo para que el cálculo tenga sentido de negocio
        if subtotal <= 0:
            raise CalculoInconsistenteError(
                "El subtotal calculado debe ser mayor que cero.",
                detalles={"subtotal": subtotal},
            )
        # El impuesto no puede ser negativo ni superar el 100%
        if impuesto < 0 or impuesto > 1:
            raise CalculoInconsistenteError(
                "El porcentaje de impuesto debe estar entre 0.0 y 1.0 (0% a 100%).",
                detalles={"impuesto": impuesto},
            )
        # El descuento no puede ser negativo ni igual o superior al 100%
        if descuento < 0 or descuento >= 1:
            raise CalculoInconsistenteError(
                "El porcentaje de descuento debe estar entre 0.0 y 0.99 (0% a 99%).",
                detalles={"descuento": descuento},
            )
        # El recargo adicional no puede ser negativo
        if recargo_adicional < 0:
            raise CalculoInconsistenteError(
                "El recargo adicional no puede ser un valor negativo.",
                detalles={"recargo_adicional": recargo_adicional},
            )

        # Se calcula el monto neto aplicando primero descuento, luego recargo y finalmente IVA
        base_con_descuento = subtotal * (1 - descuento) + recargo_adicional
        total_final = round(base_con_descuento * (1 + impuesto), 2)

        # Verificación final de integridad del resultado
        if total_final <= 0:
            raise CalculoInconsistenteError(
                "El costo final resultante es inconsistente (menor o igual a cero).",
                detalles={"total_final": total_final},
            )
        return total_final

    # --- Declaraciones @overload que documentan las variantes sobrecargadas de calcular_costo ---
    @overload
    def calcular_costo(self, duracion: float) -> float: ...

    @overload
    def calcular_costo(self, duracion: float, impuesto: float) -> float: ...

    @overload
    def calcular_costo(
        self,
        duracion: float,
        impuesto: float,
        descuento: float,
    ) -> float: ...

    @overload
    def calcular_costo(
        self,
        duracion: float,
        impuesto: float,
        descuento: float,
        recargo_adicional: float,
    ) -> float: ...

    @abstractmethod
    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """
        Calcula el costo total del servicio de forma polimórfica y sobrecargada.

        Admite invocaciones con solo duración, o combinando impuesto, descuento
        y recargos adicionales.
        """

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna una descripción detallada y especializada del servicio."""

    @abstractmethod
    def validar_parametros(self, duracion: float, **kwargs: Any) -> bool:
        """Valida la duración y parámetros específicos requeridos por cada servicio."""

    # --- Sobrecarga dinámica de métodos mediante @singledispatchmethod ---
    @singledispatchmethod
    def cotizar(self, configuracion: Any) -> float:
        """
        Método sobrecargado que genera una cotización según el tipo de argumento recibido.

        Soporta:
        - int / float: calcula costo solo con duración.
        - tuple (duracion, descuento): calcula costo con duración y descuento.
        - dict: calcula costo usando claves 'duracion', 'impuesto', 'descuento', 'recargo'.
        """
        raise DatosInvalidosError(
            f"Tipo no soportado para cotizar el servicio: {type(configuracion).__name__}.",
            detalles={"servicio": self.id_entidad, "tipo": type(configuracion).__name__},
        )

    @cotizar.register(int)
    @cotizar.register(float)
    def _(self, configuracion: float) -> float:
        """Sobrecarga 1: cotización simple recibiendo únicamente la duración en horas."""
        if isinstance(configuracion, bool):
            raise DatosInvalidosError(
                "La duración para cotizar no puede ser un valor booleano.",
                detalles={"valor": configuracion},
            )
        return self.calcular_costo(float(configuracion))

    @cotizar.register(tuple)
    def _(self, configuracion: tuple) -> float:
        """Sobrecarga 2: cotización recibiendo tupla (duracion, descuento)."""
        if len(configuracion) != 2:
            raise DatosInvalidosError(
                "La tupla de cotización debe tener exactamente 2 elementos: (duracion, descuento).",
                detalles={"tupla_recibida": configuracion},
            )
        duracion, descuento = configuracion
        return self.calcular_costo(duracion=duracion, descuento=descuento)

    @cotizar.register(dict)
    def _(self, configuracion: dict) -> float:
        """Sobrecarga 3: cotización completa a partir de un diccionario de parámetros."""
        if "duracion" not in configuracion:
            raise ParametroFaltanteError(
                "El diccionario de cotización debe incluir obligatoriamente la clave 'duracion'.",
                detalles={"claves_recibidas": list(configuracion.keys())},
            )
        return self.calcular_costo(
            duracion=configuracion["duracion"],
            impuesto=configuracion.get("impuesto", 0.0),
            descuento=configuracion.get("descuento", 0.0),
            recargo_adicional=configuracion.get("recargo_adicional", 0.0),
        )

    def validar(self) -> bool:
        """Valida los atributos comunes de todo servicio."""
        if not self.__nombre or self.__tarifa_base <= 0:
            raise DatosInvalidosError(
                "El servicio presenta nombre o tarifa base inválidos.",
                detalles={"id_entidad": self.id_entidad},
            )
        return True

    def obtener_resumen(self) -> str:
        """Retorna el resumen general delegando la descripción al método polimórfico."""
        estado = "DISPONIBLE" if self.__disponible else "NO DISPONIBLE"
        return f"[{self.id_entidad}] {self.describir_servicio()} | Estado: {estado}"

    def a_diccionario(self) -> dict[str, Any]:
        """Convierte los atributos comunes del servicio en un diccionario."""
        return {
            "id_entidad": self.id_entidad,
            "tipo_servicio": self.__class__.__name__,
            "nombre": self.__nombre,
            "tarifa_base": self.__tarifa_base,
            "disponible": self.__disponible,
            "fecha_creacion": self.fecha_creacion.isoformat(timespec="seconds"),
        }


class ReservaSala(Servicio):
    """
    Servicio especializado para el alquiler de salas de reuniones y auditorios.

    Incorpora capacidad máxima de asistentes y recargo por equipamiento audiovisual.
    """

    # Constante de recargo fijo cuando la sala incluye kit audiovisual completo
    RECARGO_AUDIOVISUAL: float = 35000.0

    def __init__(
        self,
        id_entidad: str,
        nombre: str,
        tarifa_base: float,
        capacidad_maxima: int,
        incluye_audiovisual: bool = True,
        disponible: bool = True,
    ) -> None:
        # Se invoca el constructor de la clase abstracta Servicio
        super().__init__(id_entidad, nombre, tarifa_base, disponible)
        self.__capacidad_maxima: int = 1
        self.__incluye_audiovisual: bool = True
        # Asignación mediante propiedades encapsuladas con validación
        self.capacidad_maxima = capacidad_maxima
        self.incluye_audiovisual = incluye_audiovisual
        self.validar()

    @property
    def capacidad_maxima(self) -> int:
        """Retorna el aforo máximo permitido en la sala."""
        return self.__capacidad_maxima

    @capacidad_maxima.setter
    def capacidad_maxima(self, valor: int) -> None:
        """Valida que la capacidad máxima sea un entero entre 2 y 200 personas."""
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise DatosInvalidosError(
                "La capacidad máxima de la sala debe ser un número entero.",
                detalles={"campo": "capacidad_maxima", "valor": valor},
            )
        if valor < 2 or valor > 200:
            raise DatosInvalidosError(
                "La capacidad de la sala debe estar entre 2 y 200 personas.",
                detalles={"campo": "capacidad_maxima", "valor": valor},
            )
        self.__capacidad_maxima = valor

    @property
    def incluye_audiovisual(self) -> bool:
        """Indica si la sala dispone de proyector, sonido y videoconferencia."""
        return self.__incluye_audiovisual

    @incluye_audiovisual.setter
    def incluye_audiovisual(self, valor: bool) -> None:
        """Valida y asigna si la sala incluye equipamiento audiovisual."""
        if not isinstance(valor, bool):
            raise DatosInvalidosError(
                "El indicador 'incluye_audiovisual' debe ser booleano.",
                detalles={"campo": "incluye_audiovisual", "valor": valor},
            )
        self.__incluye_audiovisual = valor

    def validar_parametros(self, duracion: float, **kwargs: Any) -> bool:
        """Valida duración (1 a 12 horas) y número opcional de asistentes."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)):
            raise DatosInvalidosError(
                "La duración de reserva de sala debe ser un valor numérico.",
                detalles={"duracion": duracion},
            )
        if duracion < 1 or duracion > 12:
            raise DatosInvalidosError(
                "Una sala solo puede reservarse entre 1 y 12 horas continuas.",
                detalles={"duracion": duracion, "min": 1, "max": 12},
            )
        # Validación opcional del número de asistentes frente al aforo de la sala
        asistentes: Optional[int] = kwargs.get("asistentes")
        if asistentes is not None:
            if isinstance(asistentes, bool) or not isinstance(asistentes, int) or asistentes <= 0:
                raise DatosInvalidosError(
                    "El número de asistentes debe ser un entero positivo.",
                    detalles={"asistentes": asistentes},
                )
            if asistentes > self.__capacidad_maxima:
                raise DatosInvalidosError(
                    f"Los asistentes ({asistentes}) superan la capacidad máxima ({self.__capacidad_maxima}).",
                    detalles={"asistentes": asistentes, "capacidad": self.__capacidad_maxima},
                )
        return True

    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """Calcula el costo total de la sala sumando el equipo audiovisual si aplica."""
        # Primero se validan los parámetros propios de la sala
        self.validar_parametros(duracion)
        # Se calcula el subtotal por horas más el costo de kit audiovisual si está habilitado
        subtotal = self.tarifa_base * float(duracion)
        if self.__incluye_audiovisual:
            subtotal += self.RECARGO_AUDIOVISUAL
        # Se aplican impuestos, descuentos y recargos con validación consistente
        return self._aplicar_ajustes_financieros(
            subtotal=subtotal,
            impuesto=impuesto,
            descuento=descuento,
            recargo_adicional=recargo_adicional,
        )

    def describir_servicio(self) -> str:
        """Describe la sala con su tarifa, aforo y disponibilidad audiovisual."""
        av = "con equipo audiovisual" if self.__incluye_audiovisual else "sin equipo audiovisual"
        return (
            f"Sala '{self.nombre}' | Capacidad: {self.__capacidad_maxima} personas ({av}) | "
            f"Tarifa base: ${self.tarifa_base:,.2f}/h"
        )

    def a_diccionario(self) -> dict[str, Any]:
        """Extiende el diccionario base añadiendo los atributos de sala."""
        datos = super().a_diccionario()
        datos.update(
            {
                "capacidad_maxima": self.__capacidad_maxima,
                "incluye_audiovisual": self.__incluye_audiovisual,
            }
        )
        return datos


class AlquilerEquipo(Servicio):
    """
    Servicio especializado para el alquiler de equipos tecnológicos de Software FJ.

    Gestiona tipo de equipo, inventario disponible y porcentaje de seguro obligatorio.
    """

    # Porcentaje de seguro contra daños por cada unidad alquilada (8%)
    PORCENTAJE_SEGURO: float = 0.08

    def __init__(
        self,
        id_entidad: str,
        nombre: str,
        tarifa_base: float,
        categoria_equipo: str,
        unidades_disponibles: int,
        seguro_obligatorio: bool = True,
        disponible: bool = True,
    ) -> None:
        # Se invoca el constructor padre Servicio
        super().__init__(id_entidad, nombre, tarifa_base, disponible)
        self.__categoria_equipo: str = ""
        self.__unidades_disponibles: int = 0
        self.__seguro_obligatorio: bool = True
        # Asignación controlada por propiedades encapsuladas
        self.categoria_equipo = categoria_equipo
        self.unidades_disponibles = unidades_disponibles
        self.seguro_obligatorio = seguro_obligatorio
        self.validar()

    @property
    def categoria_equipo(self) -> str:
        """Retorna la categoría tecnológica del equipo (Portátil, Proyector, Servidor, etc.)."""
        return self.__categoria_equipo

    @categoria_equipo.setter
    def categoria_equipo(self, valor: str) -> None:
        """Valida que la categoría del equipo no esté vacía."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                "La categoría del equipo es obligatoria.",
                detalles={"campo": "categoria_equipo"},
            )
        if not isinstance(valor, str):
            raise DatosInvalidosError(
                "La categoría del equipo debe ser una cadena de texto.",
                detalles={"campo": "categoria_equipo", "tipo": type(valor).__name__},
            )
        self.__categoria_equipo = valor.strip()

    @property
    def unidades_disponibles(self) -> int:
        """Retorna el número actual de unidades en inventario."""
        return self.__unidades_disponibles

    @unidades_disponibles.setter
    def unidades_disponibles(self, valor: int) -> None:
        """Valida que el inventario sea un entero mayor o igual a cero."""
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise DatosInvalidosError(
                "Las unidades disponibles deben ser un número entero.",
                detalles={"campo": "unidades_disponibles", "valor": valor},
            )
        if valor < 0:
            raise DatosInvalidosError(
                "Las unidades disponibles no pueden ser negativas.",
                detalles={"campo": "unidades_disponibles", "valor": valor},
            )
        self.__unidades_disponibles = valor
        # Si el inventario llega a cero, se marca automáticamente como no disponible
        if valor == 0:
            self.disponible = False

    @property
    def seguro_obligatorio(self) -> bool:
        """Indica si el alquiler incluye prima de seguro contra daños."""
        return self.__seguro_obligatorio

    @seguro_obligatorio.setter
    def seguro_obligatorio(self, valor: bool) -> None:
        """Valida el indicador booleano de seguro obligatorio."""
        if not isinstance(valor, bool):
            raise DatosInvalidosError(
                "El campo 'seguro_obligatorio' debe ser booleano.",
                detalles={"campo": "seguro_obligatorio", "valor": valor},
            )
        self.__seguro_obligatorio = valor

    def validar_parametros(self, duracion: float, **kwargs: Any) -> bool:
        """Valida duración (1 a 72 horas) y la cantidad solicitada frente al stock."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)):
            raise DatosInvalidosError(
                "La duración del alquiler debe ser un número válido.",
                detalles={"duracion": duracion},
            )
        if duracion < 1 or duracion > 72:
            raise DatosInvalidosError(
                "El alquiler de equipos debe durar entre 1 y 72 horas.",
                detalles={"duracion": duracion, "min": 1, "max": 72},
            )
        # Se valida la cantidad de equipos solicitada (por defecto 1 unidad)
        cantidad: int = kwargs.get("cantidad", 1)
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise DatosInvalidosError(
                "La cantidad de equipos a alquilar debe ser un entero positivo.",
                detalles={"cantidad": cantidad},
            )
        if cantidad > self.__unidades_disponibles:
            raise DatosInvalidosError(
                f"Stock insuficiente: se solicitaron {cantidad} unidades y solo hay {self.__unidades_disponibles}.",
                detalles={"cantidad": cantidad, "disponibles": self.__unidades_disponibles},
            )
        return True

    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """Calcula el costo del alquiler incluyendo el 8% de seguro si corresponde."""
        # Validación de reglas de duración del servicio de equipos
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * float(duracion)
        if self.__seguro_obligatorio:
            subtotal += subtotal * self.PORCENTAJE_SEGURO
        return self._aplicar_ajustes_financieros(
            subtotal=subtotal,
            impuesto=impuesto,
            descuento=descuento,
            recargo_adicional=recargo_adicional,
        )

    def describir_servicio(self) -> str:
        """Retorna la descripción detallada del equipo y su disponibilidad."""
        seguro = "con seguro (8%)" if self.__seguro_obligatorio else "sin seguro"
        return (
            f"Equipo '{self.nombre}' [{self.__categoria_equipo}] | "
            f"Stock: {self.__unidades_disponibles} uds ({seguro}) | "
            f"Tarifa base: ${self.tarifa_base:,.2f}/h"
        )

    def a_diccionario(self) -> dict[str, Any]:
        """Extiende el diccionario base con los datos propios del alquiler de equipos."""
        datos = super().a_diccionario()
        datos.update(
            {
                "categoria_equipo": self.__categoria_equipo,
                "unidades_disponibles": self.__unidades_disponibles,
                "seguro_obligatorio": self.__seguro_obligatorio,
            }
        )
        return datos


class AsesoriaEspecializada(Servicio):
    """
    Servicio especializado de consultoría técnica y asesoría profesional.

    Ajusta la tarifa según el nivel de experiencia del consultor y la modalidad
    de atención (virtual, presencial o híbrida).
    """

    # Multiplicadores tarifarios válidos según el nivel del consultor asignado
    MULTIPLICADORES_NIVEL: dict[str, float] = {
        "junior": 1.0,
        "semi-senior": 1.25,
        "senior": 1.5,
    }
    # Modalidades de ejecución permitidas por Software FJ
    MODALIDADES_VALIDAS: tuple[str, ...] = ("virtual", "presencial", "hibrida")
    # Recargo por desplazamiento cuando la asesoría es presencial
    RECARGO_PRESENCIAL: float = 40000.0

    def __init__(
        self,
        id_entidad: str,
        nombre: str,
        tarifa_base: float,
        area_especialidad: str,
        nivel_consultor: str = "senior",
        modalidad: str = "virtual",
        disponible: bool = True,
    ) -> None:
        # Se inicializa la clase base Servicio
        super().__init__(id_entidad, nombre, tarifa_base, disponible)
        self.__area_especialidad: str = ""
        self.__nivel_consultor: str = "senior"
        self.__modalidad: str = "virtual"
        # Asignación controlada con validaciones de dominio
        self.area_especialidad = area_especialidad
        self.nivel_consultor = nivel_consultor
        self.modalidad = modalidad
        self.validar()

    @property
    def area_especialidad(self) -> str:
        """Retorna el área de conocimiento de la asesoría (ej. Ciberseguridad, Cloud)."""
        return self.__area_especialidad

    @area_especialidad.setter
    def area_especialidad(self, valor: str) -> None:
        """Valida que el área de especialidad sea una cadena no vacía."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                "El área de especialidad de la asesoría es obligatoria.",
                detalles={"campo": "area_especialidad"},
            )
        if not isinstance(valor, str):
            raise DatosInvalidosError(
                "El área de especialidad debe ser una cadena de texto.",
                detalles={"campo": "area_especialidad", "tipo": type(valor).__name__},
            )
        self.__area_especialidad = valor.strip()

    @property
    def nivel_consultor(self) -> str:
        """Retorna el nivel de experiencia del consultor."""
        return self.__nivel_consultor

    @nivel_consultor.setter
    def nivel_consultor(self, valor: str) -> None:
        """Valida que el nivel pertenezca al catálogo permitido."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                "El nivel del consultor es obligatorio.",
                detalles={"campo": "nivel_consultor"},
            )
        if not isinstance(valor, str):
            raise DatosInvalidosError(
                "El nivel del consultor debe ser una cadena de texto.",
                detalles={"campo": "nivel_consultor", "valor": valor},
            )
        nivel_norm = valor.strip().lower()
        if nivel_norm not in self.MULTIPLICADORES_NIVEL:
            raise DatosInvalidosError(
                f"Nivel de consultor inválido. Permitidos: {list(self.MULTIPLICADORES_NIVEL.keys())}.",
                detalles={"campo": "nivel_consultor", "valor": valor},
            )
        self.__nivel_consultor = nivel_norm

    @property
    def modalidad(self) -> str:
        """Retorna la modalidad de prestación de la asesoría."""
        return self.__modalidad

    @modalidad.setter
    def modalidad(self, valor: str) -> None:
        """Valida que la modalidad sea virtual, presencial o hibrida."""
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(
                "La modalidad de la asesoría es obligatoria.",
                detalles={"campo": "modalidad"},
            )
        if not isinstance(valor, str):
            raise DatosInvalidosError(
                "La modalidad debe ser una cadena de texto.",
                detalles={"campo": "modalidad", "valor": valor},
            )
        mod_norm = valor.strip().lower()
        if mod_norm not in self.MODALIDADES_VALIDAS:
            raise DatosInvalidosError(
                f"Modalidad no soportada. Permitidas: {list(self.MODALIDADES_VALIDAS)}.",
                detalles={"campo": "modalidad", "valor": valor},
            )
        self.__modalidad = mod_norm

    def validar_parametros(self, duracion: float, **kwargs: Any) -> bool:
        """Valida que la duración de la asesoría esté entre 1 y 40 horas."""
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)):
            raise DatosInvalidosError(
                "La duración de la asesoría debe ser un valor numérico.",
                detalles={"duracion": duracion},
            )
        if duracion < 1 or duracion > 40:
            raise DatosInvalidosError(
                "La asesoría especializada debe contratarse entre 1 y 40 horas.",
                detalles={"duracion": duracion, "min": 1, "max": 40},
            )
        return True

    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
        recargo_adicional: float = 0.0,
    ) -> float:
        """Calcula el costo aplicando el factor de nivel y el recargo presencial."""
        self.validar_parametros(duracion)
        factor_nivel = self.MULTIPLICADORES_NIVEL[self.__nivel_consultor]
        subtotal = self.tarifa_base * float(duracion) * factor_nivel
        # Si la modalidad es presencial se añade el recargo logístico de desplazamiento
        if self.__modalidad == "presencial":
            subtotal += self.RECARGO_PRESENCIAL
        return self._aplicar_ajustes_financieros(
            subtotal=subtotal,
            impuesto=impuesto,
            descuento=descuento,
            recargo_adicional=recargo_adicional,
        )

    def describir_servicio(self) -> str:
        """Retorna una descripción completa de la asesoría técnica."""
        return (
            f"Asesoría '{self.nombre}' | Área: {self.__area_especialidad} | "
            f"Consultor: {self.__nivel_consultor.upper()} | Modalidad: {self.__modalidad} | "
            f"Tarifa base: ${self.tarifa_base:,.2f}/h"
        )

    def a_diccionario(self) -> dict[str, Any]:
        """Extiende el diccionario base con los atributos de la asesoría."""
        datos = super().a_diccionario()
        datos.update(
            {
                "area_especialidad": self.__area_especialidad,
                "nivel_consultor": self.__nivel_consultor,
                "modalidad": self.__modalidad,
            }
        )
        return datos
