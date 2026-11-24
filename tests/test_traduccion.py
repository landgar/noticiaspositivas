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


def test_traduce_texto_espanol_sin_pasar_por_heuristico(monkeypatch):
    import noticias_positivas.traduccion as modulo

    urls = []

    class RespuestaEspanol:
        def raise_for_status(self):
            pass

        def json(self):
            return {"responseData": {"translatedText": "Avance español confirmado"}}

    def responder(url, *args, **kwargs):
        urls.append(url)
        return RespuestaEspanol()

    modulo._CACHE_TRADUCCION.clear()
    monkeypatch.setattr(modulo.requests, "get", responder)

    resultado = traducir_texto("Avance español confirmado", "https://translate.googleapis.com/translate_a/single")
    assert resultado == "Avance español confirmado"
    assert "sl=auto" in urls[0]
    assert "tl=es" in urls[0]


def test_texto_vacio_no_llama_al_servicio(monkeypatch):
    import noticias_positivas.traduccion as modulo

    def fallo(*args, **kwargs):
        raise AssertionError("No debe llamar al servicio para texto vacío")

    monkeypatch.setattr(modulo.requests, "get", fallo)
    assert traducir_texto("") == ""
