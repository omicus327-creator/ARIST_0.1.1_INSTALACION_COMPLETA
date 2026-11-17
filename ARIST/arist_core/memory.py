"""Memoria simulada en una lista de valores; no accede a la RAM del equipo."""


class Memoria:
    def __init__(self, tamaño: int = 1024, store=None):
        if not isinstance(tamaño, int) or tamaño <= 0:
            raise ValueError("El tamaño debe ser un entero positivo.")
        self.tamaño = tamaño
        self.store = store
        self.memoria = store.load_memory(tamaño) if store else [0] * tamaño

    def leer(self, dirección: int) -> int:
        self._validar_direccion(dirección)
        return self.memoria[dirección]

    def escribir(self, dirección: int, valor: int) -> None:
        self._validar_direccion(dirección)
        if not isinstance(valor, int) or not 0 <= valor <= 255:
            raise ValueError("El valor debe ser un entero entre 0 y 255.")
        self.memoria[dirección] = valor
        if self.store:
            self.store.save_memory(self.memoria)

    def _validar_direccion(self, dirección: int) -> None:
        if not isinstance(dirección, int) or not 0 <= dirección < self.tamaño:
            raise ValueError(f"Dirección no válida. Usa una dirección entre 0 y {self.tamaño - 1}.")
