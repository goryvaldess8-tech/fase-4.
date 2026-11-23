"""
Suite de pruebas unitarias para el Sistema Integral de Gestión de Software FJ.

Verifica de forma automatizada:
- Abstracción (imposibilidad de instanciar Entidad o Servicio directamente).
- Encapsulación y validaciones estrictas en Cliente.
- Herencia, polimorfismo y sobrecarga de métodos en los 3 servicios.
- Ciclo de vida de Reserva, transiciones válidas/inválidas y encadenamiento de excepciones.
- Ejecución completa de la simulación de 14 operaciones y generación del archivo de logs.
"""

import tempfile
import unittest
from pathlib import Path

from src.cliente import Cliente
from src.entidad import Entidad
from src.excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
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
from src.simulacion import ejecutar_simulacion


class TestSistemaSoftwareFJ(unittest.TestCase):
    """Casos de prueba unitarios y de integración para Software FJ."""

    def setUp(self) -> None:
        """Crea un archivo de log temporal aislado para cada prueba."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ruta_log = Path(self.temp_dir.name) / "test_software_fj.log"
        self.gestor_logs = GestorLogs(
            ruta_archivo=str(self.ruta_log),
            nombre_logger=f"TestLogger_{id(self)}",
        )
        self.sistema = SistemaGestionSoftwareFJ(gestor_logs=self.gestor_logs)

    def tearDown(self) -> None:
        """Cierra los manejadores de log y elimina el directorio temporal."""
        self.gestor_logs.cerrar()
        self.temp_dir.cleanup()

    def test_clases_abstractas_no_instanciables(self) -> None:
        """Verifica que Entidad y Servicio no puedan instanciarse directamente."""
        with self.assertRaises(TypeError):
            Entidad("ENT-001")  # type: ignore[abstract]
        with self.assertRaises(TypeError):
            Servicio("SRV-001", "Genérico", 10000.0)  # type: ignore[abstract]

    def test_cliente_encapsulacion_y_validaciones(self) -> None:
        """Comprueba creación válida y rechazo de datos erróneos o faltantes en Cliente."""
        cliente = Cliente(
            id_entidad="cli-100",
            nombre_completo="Rodrigo Valdés Vásquez",
            documento="1045678901",
            correo="RODRIGO@SOFTWAREFJ.CO",
            telefono="+57 300-123-4567",
        )
        self.assertEqual(cliente.id_entidad, "CLI-100")
        self.assertEqual(cliente.correo, "rodrigo@softwarefj.co")
        self.assertEqual(cliente.telefono, "+573001234567")

        # Correo inválido debe lanzar DatosInvalidosError
        with self.assertRaises(DatosInvalidosError):
            cliente.correo = "correo_sin_dominio"

        # Nombre vacío debe lanzar ParametroFaltanteError
        with self.assertRaises(ParametroFaltanteError):
            Cliente("CLI-101", "", "12345678", "ok@ok.com", "3001234567")

    def test_polimorfismo_y_sobrecarga_servicios(self) -> None:
        """Valida cálculo polimórfico y métodos sobrecargados calcular_costo/cotizar."""
        sala = ReservaSala("SAL-01", "Sala Norte", 100000.0, 20, incluye_audiovisual=True)
        equipo = AlquilerEquipo("EQU-01", "Laptop Pro", 50000.0, "Portátil", 4, seguro_obligatorio=True)
        asesoria = AsesoriaEspecializada("ASE-01", "Asesoría Cloud", 100000.0, "Cloud", "senior", "virtual")

        # Sala: 2h * 100.000 + 35.000 AV = 235.000
        self.assertEqual(sala.calcular_costo(2), 235000.0)
        # Equipo: 2h * 50.000 = 100.000 + 8% seguro = 108.000
        self.assertEqual(equipo.calcular_costo(2), 108000.0)
        # Asesoría senior virtual: 2h * 100.000 * 1.5 = 300.000
        self.assertEqual(asesoria.calcular_costo(2), 300000.0)

        # Sobrecarga con parámetros opcionales (IVA 19% + descuento 10%)
        self.assertEqual(asesoria.calcular_costo(2, 0.19, 0.10), 321300.0)

        # Sobrecarga dinámica @singledispatchmethod en cotizar()
        self.assertEqual(asesoria.cotizar(2), 300000.0)
        self.assertEqual(asesoria.cotizar((2, 0.10)), 270000.0)
        self.assertEqual(
            asesoria.cotizar({"duracion": 2, "impuesto": 0.19, "descuento": 0.10}),
            321300.0,
        )

    def test_reserva_ciclo_vida_y_encadenamiento_excepciones(self) -> None:
        """Comprueba transiciones de Reserva y encadenamiento explícito de causas."""
        cliente = Cliente("CLI-01", "Laura Gómez", "98765432", "laura@fj.co", "3101112233")
        sala = ReservaSala("SAL-01", "Sala Sur", 80000.0, 10, incluye_audiovisual=False)

        # Encadenamiento: aforo excedido lanza ReservaInvalidaError causada por DatosInvalidosError
        with self.assertRaises(ReservaInvalidaError) as contexto:
            Reserva("RES-ERR", cliente, sala, 3, parametros_adicionales={"asistentes": 50})
        self.assertIsInstance(contexto.exception.__cause__, DatosInvalidosError)

        # Ciclo completo válido
        reserva = Reserva("RES-OK", cliente, sala, 3, parametros_adicionales={"asistentes": 8})
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)
        reserva.confirmar()
        self.assertEqual(reserva.estado, EstadoReserva.CONFIRMADA)

        # Error de cálculo inconsistente encadenado
        with self.assertRaises(CalculoInconsistenteError) as ctx_calc:
            reserva.procesar(impuesto=0.19, descuento=1.5)
        self.assertIsInstance(ctx_calc.exception.__cause__, CalculoInconsistenteError)
        # El estado debe mantenerse CONFIRMADA tras el fallo controlado
        self.assertEqual(reserva.estado, EstadoReserva.CONFIRMADA)

        # Procesamiento exitoso posterior
        total = reserva.procesar(impuesto=0.19, descuento=0.0)
        self.assertEqual(total, 285600.0)
        self.assertEqual(reserva.estado, EstadoReserva.PROCESADA)

        # Operación no permitida: cancelar reserva ya procesada
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.cancelar("Ya no la necesito")

    def test_servicio_no_disponible_y_entidad_inexistente(self) -> None:
        """Valida detección de servicio no disponible y consulta de ID inexistente."""
        cliente = Cliente("CLI-02", "Carlos Ruiz", "11223344", "carlos@fj.co", "3123334455")
        sala_inactiva = ReservaSala("SAL-99", "Sala Cerrada", 50000.0, 10, disponible=False)

        with self.assertRaises(ServicioNoDisponibleError):
            Reserva("RES-99", cliente, sala_inactiva, 2)

        with self.assertRaises(EntidadNoEncontradaError):
            self.sistema.buscar_cliente("NO-EXISTE")

    def test_simulacion_completa_genera_logs_y_no_falla(self) -> None:
        """Ejecuta las 14 operaciones completas y verifica el archivo de logs generado."""
        sistema_sim = ejecutar_simulacion(ruta_log=str(self.ruta_log))
        try:
            reporte = sistema_sim.obtener_reporte_general()
            self.assertEqual(reporte["total_clientes"], 3)
            self.assertEqual(reporte["total_servicios"], 4)
            self.assertGreaterEqual(reporte["total_reservas"], 5)
            self.assertGreater(reporte["total_facturado"], 0)
            self.assertGreater(reporte["estadisticas_logs"]["errores"], 10)
            self.assertTrue(self.ruta_log.exists())
            contenido_log = self.ruta_log.read_text(encoding="utf-8")
            self.assertIn("Causa encadenada", contenido_log)
            self.assertIn("Simulación de 14 operaciones finalizada", contenido_log)
        finally:
            sistema_sim.logs.cerrar()


if __name__ == "__main__":
    unittest.main()
