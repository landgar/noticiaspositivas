from noticias_positivas.traduccion import traducir_texto


class RespuestaSimulada:
    def raise_for_status(self):
        pass

    def json(self):
        return [[["Gran avance científico", "Great scientific breakthrough"]]]


def test_traduce_texto(monkeypatch):
    import noticias_positivas.traduccion as modulo

    monkeypatch.setattr(modulo.requests, "get", lambda *args, **kwargs: RespuestaSimulada())

    resultado = traducir_texto("Great scientific breakthrough")
    assert resultado == "Gran avance científico"


def test_texto_vacio_no_llama_al_servicio(monkeypatch):
    import noticias_positivas.traduccion as modulo

    def fallo(*args, **kwargs):
        raise AssertionError("No debe llamar al servicio para texto vacío")

    monkeypatch.setattr(modulo.requests, "get", fallo)
    assert traducir_texto("") == ""
