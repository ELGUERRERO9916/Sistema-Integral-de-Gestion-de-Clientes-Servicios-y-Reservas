import os
import datetime as dt
from abc import ABC, abstractmethod

# Obtengo la ruta exacta de la carpeta donde está guardado este script actual para el log
ruta_script = os.path.dirname(os.path.abspath(__file__))
ruta_log = os.path.join(ruta_script, "error.log")

# EXCEPCIONES PERSONALIZADAS

class ErrorServicioNoDisponible(Exception):
    """Excepción personalizada para manejar servicios no disponibles o fallos en reservas."""
    pass

class ErrorParametroInvalido(ValueError):
    """Excepción personalizada para parámetros de entrada incorrectos."""
    pass


# DEFINICIÓN DE CLASES 

# Creo la clase Cliente con encapsulamiento y validación de datos personales requerida en la guía.
class Cliente:
    def __init__(self, nombre, cedula, correo):
        self._nombre = nombre
        self._cedula = cedula
        self._correo = correo

    @property
    def nombre(self):
        return self._nombre

    @property
    def cedula(self):
        return self._cedula

    def validar_datos(self):
        # Valido que los campos no estén vacíos o nulos
        if not self._nombre or not str(self._cedula).isdigit():
            raise ErrorParametroInvalido("Datos del cliente inválidos (Nombre vacío o cédula no numérica).")
        return True


# Creo la clase base Servicio heredando de ABC para implementar abstracción y polimorfismo.
class Servicio(ABC):
    def __init__(self, tiempo):
        if tiempo <= 0:
            raise ErrorParametroInvalido("El tiempo en horas debe ser mayor a cero.")
        self.tiempo = tiempo

    # Método abstracto con parámetros opcionales para simular sobrecarga/variantes de costos (impuestos o descuentos).
    @abstractmethod
    def calcular_precio(self, descuento=0, impuesto=0):
        pass


# Clase hija para gestión de salas
class Salas(Servicio):
    PRECIO_HORA_SALA = 50000 

    def __init__(self, ubicacion, piso, tiempo):
        super().__init__(tiempo)
        if piso not in [1, 2, 3, 4, 5]:
            raise ErrorParametroInvalido("El piso de la sala debe estar entre 1 y 5.")
        self.ubicacion = ubicacion
        self.piso = piso

    def calcular_precio(self, descuento=0, impuesto=0):
        subtotal = self.tiempo * self.PRECIO_HORA_SALA
        total = subtotal - (subtotal * descuento) + (subtotal * impuesto)
        return total


# Clase hija para alquiler de equipos
class Equipos(Servicio):
    PRECIO_HORA_EQUIPO = 25000 

    def __init__(self, id_equipo, nombre_equipo, tiempo):
        super().__init__(tiempo)
        self.id_equipo = id_equipo
        self.nombre_equipo = nombre_equipo

    def calcular_precio(self, descuento=0, impuesto=0):
        subtotal = self.tiempo * self.PRECIO_HORA_EQUIPO
        total = subtotal - (subtotal * descuento) + (subtotal * impuesto)
        return total


# Clase hija para asesorías académicas
class Asesorias(Servicio):
    PRECIO_HORA_ASESORIA = 40000 

    def __init__(self, nombre_tutor, ubicacion, piso, tiempo):
        super().__init__(tiempo)
        self.nombre_tutor = nombre_tutor
        self.ubicacion = ubicacion
        self.piso = piso

    def calcular_precio(self, descuento=0, impuesto=0):
        subtotal = self.tiempo * self.PRECIO_HORA_ASESORIA
        total = subtotal - (subtotal * descuento) + (subtotal * impuesto)
        return total


# Clase Reserva que integra cliente, servicio, estado y manejo avanzado de las excepciones (try/except/else/finally)
class Reserva:
    def __init__(self, cliente, servicio):
        self.cliente = cliente
        self.servicio = servicio
        self.estado = "Pendiente"

    def procesar_reserva(self, descuento=0, impuesto=0):
        costo_final = 0
        try:
            # Validamos los datos del cliente
            self.cliente.validar_datos()
            
            # Calculamos el precio aplicando las variantes de impuestos o descuentos
            costo_final = self.servicio.calcular_precio(descuento, impuesto)
            
        except ErrorParametroInvalido as ep:
            self.estado = "Fallida"
            with open(ruta_log, "a") as log:
                log.write(f"[{dt.datetime.now()}] Error de parámetro en reserva: {ep}\n")
            raise
            
        except Exception as e:
            self.estado = "Error Inesperado"
            with open(ruta_log, "a") as log:
                log.write(f"[{dt.datetime.now()}] Excepción general en reserva: {e}\n")
            raise ErrorServicioNoDisponible("No se pudo procesar la reserva debido a un error crítico.") from e
            
        else:
            # Se ejecuta únicamente si todo salió bien en el try
            self.estado = "Confirmada"
            print(f"-> [ÉXITO] Reserva confirmada para {self.cliente.nombre}. Total a pagar: ${costo_final}")
            
        finally:
            # Se ejecuta siempre, garantizando estabilidad operativa
            print(f"-> [ESTADO FINALIZADO] Operación de reserva procesada. Estado actual: {self.estado}\n")


# SIMULACIÓN DE 10 OPERACIONES

print("==================================================")
print(" INICIANDO SIMULACIÓN DE LAS 10 OPERACIONES")
print("==================================================\n")

# Lista de casos de prueba simulados utilizando lambdas para diferir la ejecución y atrapar los errores
operaciones_simuladas = [
    # 1. Operación válida de Sala
    (lambda: Cliente("Ana Gómez", "1010108492", "ana@mail.com"), lambda: Salas("Sala 1", 2, 3), 0, 0),
    # 2. Operación inválida (tiempo menor o igual a 0 en equipos)
    (lambda: Cliente("Carlos Ruiz", "20202061374", "carlos@mail.com"), lambda: Equipos("EQ-01", "Laptop", 0), 0, 0),
    # 3. Operación válida de Asesoría con descuento e impuesto
    (lambda: Cliente("Lucía Pérez", "3030307814", "lucia@mail.com"), lambda: Asesorias("Prof. Juan", "Sala 3", 3, 2), 0.1, 0.05),
    # 4. Operación con datos de cliente inválidos (cédula con letras)
    (lambda: Cliente("Pedro Picapiedra", "ABCXYZ", "pedro@mail.com"), lambda: Salas("Sala 2", 1, 4), 0, 0),
    # 5. Operación válida de Equipos
    (lambda: Cliente("María Soto", "4040401453", "maria@mail.com"), lambda: Equipos("EQ-02", "Proyector", 5), 0.0, 0.0),
    # 6. Operación inválida por piso fuera de rango en Salas
    (lambda: Cliente("Jorge Neira", "5050508260", "jorge@mail.com"), lambda: Salas("Sala 9", 7, 2), 0, 0),
    # 7. Operación válida de Asesoría
    (lambda: Cliente("Sofia Vergara", "6060604536", "sofia@mail.com"), lambda: Asesorias("Prof. Andrea", "Sala 4", 4, 1), 0, 0),
    # 8. Operación válida de Salas con múltiples horas
    (lambda: Cliente("David Guetta", "7070705764", "david@mail.com"), lambda: Salas("Sala 5", 5, 6), 0.2, 0),
    # 9. Operación inválida (tiempo negativo en asesorías)
    (lambda: Cliente("Esteban Quito", "8080808936", "esteban@mail.com"), lambda: Asesorias("Prof. Luis", "Sala 1", 1, -3), 0, 0),
    # 10. Operación válida final de Equipos con impuestos
    (lambda: Cliente("Diana Urrego", "9090905746", "diana@mail.com"), lambda: Equipos("EQ-03", "Tablet", 2), 0, 0.19)
]

# Ejecutamos la simulación iterando las 10 operaciones de forma segura dentro del try-except
for i, (fabrica_cliente, fabrica_servicio, desc_op, imp_op) in enumerate(operaciones_simuladas, start=1):
    print(f"--- Ejecutando Operación N.° {i} ---")
    try:
        cliente_op = fabrica_cliente()
        servicio_op = fabrica_servicio()
        reserva_actual = Reserva(cliente_op, servicio_op)
        reserva_actual.procesar_reserva(descuento=desc_op, impuesto=imp_op)
    except (ErrorParametroInvalido, ErrorServicioNoDisponible, ValueError) as err:
        print(f"-> [CONTROL DE ERROR CAPTURADO]: {err}\n")
    except Exception as err_gen:
        print(f"-> [ERROR INESPERADO]: {err_gen}\n")

print("==================================================")
print(" SIMULACIÓN DE 10 OPERACIONES FINALIZADA CON ÉXITO")
print("==================================================")