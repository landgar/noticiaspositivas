from noticias_positivas.configuracion import cargar


def test_carga_configuracion():
    configuracion = cargar()
    assert configuracion["cantidad_noticias"] == 10
    assert configuracion["ruta_repositorio"] == "."
    assert configuracion["publicacion"]["subir_automaticamente"] is False
    assert configuracion["fuentes"]
    assert all(fuente["region"].lower() == "europa" for fuente in configuracion["fuentes"])
    assert all(fuente["pais"] for fuente in configuracion["fuentes"])
