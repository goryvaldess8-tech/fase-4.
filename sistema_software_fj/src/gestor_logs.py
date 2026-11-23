"""
Módulo de registro de eventos y errores (logging) para Software FJ.

Gestiona la escritura en archivo de texto plano para auditar todas las
operaciones exitosas, advertencias y excepciones (incluyendo su causa
encadenada), sin utilizar ningún motor de base de datos.
"""

import logging
from pathlib import Path
from typing import Optional


class GestorLogs:
    """
    Clase encargada de centralizar el registro de eventos y errores en archivo.

    Aplica encapsulación sobre el objeto logger interno de Python y asegura
    que el directorio de logs exista antes de escribir cada entrada.
    """

    def __init__(
        self,
        ruta_archivo: str = "logs/sistema_software_fj.log",
        nombre_logger: str = "SoftwareFJ",
    ) -> None:
        # Se convierte la ruta recibida a un objeto Path para manejo seguro multiplataforma
        self.__ruta_archivo: Path = Path(ruta_archivo)
        # Se almacena el nombre identificador del logger
        self.__nombre_logger: str = nombre_logger
        # Contadores internos para generar estadísticas de auditoría al final de la ejecución
        self.__total_info: int = 0
        self.__total_advertencias: int = 0
        self.__total_errores: int = 0
        # Se configura el logger de Python al construir la instancia
        self.__logger: logging.Logger = self.__configurar_logger()

    @property
    def ruta_archivo(self) -> Path:
        """Retorna la ruta absoluta o relativa del archivo de logs."""
        return self.__ruta_archivo

    @property
    def estadisticas(self) -> dict[str, int]:
        """Retorna un resumen numérico de los eventos registrados en la sesión."""
        return {
            "info": self.__total_info,
            "advertencias": self.__total_advertencias,
            "errores": self.__total_errores,
            "total": self.__total_info + self.__total_advertencias + self.__total_errores,
        }

    def __configurar_logger(self) -> logging.Logger:
        """Crea el directorio de logs y configura el manejador de archivo UTF-8."""
        # Se crea la carpeta contenedora si todavía no existe en el sistema de archivos
        self.__ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        # Se obtiene o crea el logger con el nombre definido
        logger = logging.getLogger(self.__nombre_logger)
        # Se establece el nivel mínimo de registro en DEBUG para capturar todo detalle
        logger.setLevel(logging.DEBUG)
        # Se evita la propagación duplicada hacia el logger raíz
        logger.propagate = False

        # Se limpian manejadores previos si el logger ya había sido inicializado
        if logger.handlers:
            for handler in list(logger.handlers):
                handler.close()
                logger.removeHandler(handler)

        # Se define el formato estandarizado con fecha, hora, nivel y mensaje
        formato = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Se crea un FileHandler en modo escritura acumulativa (append) con codificación UTF-8
        manejador_archivo = logging.FileHandler(
            filename=self.__ruta_archivo,
            mode="a",
            encoding="utf-8",
        )
        # Se asigna el formato configurado al manejador de archivo
        manejador_archivo.setFormatter(formato)
        # Se vincula el manejador al logger de la instancia
        logger.addHandler(manejador_archivo)
        return logger

    def reiniciar_archivo(self) -> None:
        """Limpia el archivo de logs al iniciar una nueva simulación completa."""
        # Se cierran temporalmente los manejadores para evitar bloqueos de archivo en Windows
        for handler in list(self.__logger.handlers):
            handler.close()
            self.__logger.removeHandler(handler)
        # Se reinicia el archivo dejando una cabecera descriptiva inicial
        self.__ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        self.__ruta_archivo.write_text("", encoding="utf-8")
        # Se reinician los contadores de estadísticas de la sesión
        self.__total_info = 0
        self.__total_advertencias = 0
        self.__total_errores = 0
        # Se vuelve a enlazar el manejador de archivo
        self.__logger = self.__configurar_logger()

    def registrar_info(self, mensaje: str) -> None:
        """Registra un evento informativo relevante de operación exitosa."""
        # Se incrementa el contador de eventos informativos
        self.__total_info += 1
        # Se escribe la línea en el archivo de logs con nivel INFO
        self.__logger.info(mensaje)

    def registrar_advertencia(self, mensaje: str) -> None:
        """Registra una advertencia controlada que no detiene el flujo normal."""
        # Se incrementa el contador de advertencias
        self.__total_advertencias += 1
        # Se escribe la línea en el archivo de logs con nivel WARNING
        self.__logger.warning(mensaje)

    def registrar_error(
        self,
        contexto: str,
        excepcion: Optional[BaseException] = None,
    ) -> None:
        """
        Registra un error en el archivo de logs, detallando tipo y causa encadenada.

        Si la excepción fue lanzada mediante 'raise X from Y', también documenta
        explícitamente la excepción original encadenada.
        """
        # Se incrementa el contador de errores registrados
        self.__total_errores += 1
        if excepcion is None:
            # Registro de error general sin objeto excepción asociado
            self.__logger.error("%s", contexto)
            return

        # Se extrae el nombre de la clase de la excepción capturada
        tipo_error = type(excepcion).__name__
        # Se arma el mensaje base con el contexto y la descripción de la excepción
        detalle = f"{contexto} -> {tipo_error}: {excepcion}"

        # Se inspecciona si existe una excepción original encadenada (__cause__)
        causa = excepcion.__cause__
        if causa is not None:
            # Se añade la información de la causa original al mensaje del log
            detalle += f" | Causa encadenada ({type(causa).__name__}): {causa}"

        # Se escribe el registro completo con nivel ERROR en el archivo
        self.__logger.error(detalle)

    def cerrar(self) -> None:
        """Cierra ordenadamente todos los manejadores de archivo asociados al logger."""
        for handler in list(self.__logger.handlers):
            handler.flush()
            handler.close()
            self.__logger.removeHandler(handler)
