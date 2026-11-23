from pathlib import Path
from time import monotonic

from playwright.sync_api import sync_playwright


URL_EDITOR_SUBSTACK = "https://substack.com/publish/post"


def es_pagina_privada(texto: str, url: str) -> bool:
    contenido = texto.lower()
    url = url.lower()
    frases = (
        "this page is private",
        "page is private",
        "página privada",
        "pagina privada",
        "you don't have access",
        "you do not have access",
        "no tienes acceso",
        "not authorized",
        "no autorizado",
        "unauthorized",
    )
    return any(frase in contenido for frase in frases) or "/publish/post" not in url and "private" in contenido


def crear_borrador(
    url_substack: str,
    titulo: str,
    ruta_html: str,
    perfil: str,
    publicar: bool = False,
) -> None:
    perfil_ruta = Path(perfil)
    perfil_ruta.mkdir(parents=True, exist_ok=True)
    html = Path(ruta_html).read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch_persistent_context(
            str(perfil_ruta),
            headless=False,
            timeout=120_000,
        )
        pagina = navegador.pages[0] if navegador.pages else navegador.new_page()

        pagina.goto(URL_EDITOR_SUBSTACK, wait_until="domcontentloaded", timeout=120_000)

        espera_final = monotonic() + 900
        while monotonic() < espera_final:
            url_actual = pagina.url.lower()
            texto_pagina = ""
            try:
                texto_pagina = pagina.locator("body").inner_text(timeout=1_000).lower()
            except Exception:
                pass

            requiere_inicio = (
                "/sign-in" in url_actual
                or "/signin" in url_actual
                or "sign in" in texto_pagina[:2_000]
                or "iniciar sesión" in texto_pagina[:2_000]
                or "log in" in texto_pagina[:2_000]
            )
            if es_pagina_privada(texto_pagina, url_actual):
                raise RuntimeError(
                    "Substack muestra una página privada. Inicia sesión en Chromium con la cuenta "
                    "que posee la publicación o tiene permisos de autor, y vuelve a ejecutar --subir. "
                    "Si persiste, elimina el perfil de Chromium y autentícate de nuevo."
                )
            if requiere_inicio:
                print("Inicia sesión en la ventana de Chromium. La aplicación esperará hasta 15 minutos.")
                pagina.wait_for_timeout(5_000)
                continue

            editores = pagina.locator("textarea, [contenteditable='true']")
            if editores.count() > 0:
                break

            pagina.wait_for_timeout(5_000)
        else:
            raise RuntimeError("No apareció el editor de Substack durante los 15 minutos de espera.")

        editores = pagina.locator("textarea, [contenteditable='true']")
        if editores.count() == 0:
            raise RuntimeError("No se encontró el editor de Substack.")

        editores.first.fill(titulo)

        cuerpos = pagina.locator("[contenteditable='true']")
        if cuerpos.count() == 0:
            raise RuntimeError("No se encontró el cuerpo del editor de Substack.")

        cuerpo = cuerpos.last
        cuerpo.evaluate(
            "(element, value) => { element.innerHTML = value; element.dispatchEvent(new InputEvent('input', { bubbles: true })); }",
            html,
        )

        print("Entrada creada como borrador. Revisa y publica manualmente.")

        if publicar:
            botones = pagina.get_by_role("button", name="Publish")
            if botones.count() == 0:
                botones = pagina.get_by_role("button", name="Publicar")
            if botones.count() == 0:
                raise RuntimeError("No se encontró el botón de publicación.")
            botones.first.click()
            pagina.wait_for_timeout(3_000)

        try:
            input("Pulsa Intro aquí para cerrar Chromium y terminar el proceso...")
        except EOFError:
            pass
        navegador.close()
