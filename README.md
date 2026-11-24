# Noticias positivas

Aplicación Python que recopila RSS de medios españoles importantes, selecciona las noticias más positivas del día y crea una edición diaria en español en formato TXT y HTML.

## Uso

```bash
python main.py
```

Sin argumentos, `main.py` crea una edición inmediatamente, la publica y permanece en espera hasta el mismo horario del día siguiente. El bucle usa `hora_generacion_diaria` de la configuración (09:00 por defecto).

Usa `python main.py --una-vez` para generar y terminar en una sola ejecución. Para GitHub Actions se recomienda `python main.py --una-vez --sin-publicar`.

El script crea una edición diaria en texto y una página web con estos nombres:

```text
salidas/YYYY-MM-DD-noticias-positivas.txt
salidas/YYYY-MM-DD-noticias-positivas.html
```

La página HTML utiliza una maquetación editorial periódica, incluye fotografías disponibles en el RSS y enlaza cada titular con su fuente original. Si se ejecuta varias veces el mismo día, se actualizan ambos archivos.

Solo se procesan fuentes declaradas en la configuración con `pais: España` y `region: España`. Los titulares y resúmenes se conservan exactamente como aparecen en los RSS. El sistema no utiliza medios de otros países.

## Configuración

- `cantidad_noticias`: número de noticias incluidas.
- `ventana_horas`: antigüedad máxima de las entradas RSS.
- `ruta_repositorio`: ruta local del repositorio; por defecto `.`
- `fuentes`: fuentes RSS españolas procesadas; deben indicar `pais: España` y `region: España`.

La opción `RUTA_REPOSITORIO` puede definirse en el entorno.
No se realizan traducciones ni verificaciones de idioma sobre titulares o resúmenes.

## Programación diaria

Ejemplo Linux cron:

```cron
0 9 * * * cd /ruta/noticiaspositivas && /ruta/noticiaspositivas/.venv/bin/python main.py >> /var/log/noticias-positivas.log 2>&1
```

En Windows puede usar el Programador de tareas ejecutando:

```bat
C:\ruta\noticiaspositivas\.venv\Scripts\python.exe C:\ruta\noticiaspositivas\main.py
```

Por defecto `main.py` genera la edición y hace commit/push a `origin/main`, y luego permanece a la espera. Si la publicación falla, muestra el error de Git y reintenta al día siguiente. Para usarlo en GitHub Actions sin publicar desde el runner, usa `--una-vez --sin-publicar`.

Antes de ejecutar en otro ordenador, autentica una vez:

```bat
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
```

Después prueba:

```bat
git remote get-url origin
git fetch origin main
git push origin main
```

Para Windows, `ejecutar_y_publicar.bat` inicia el modo continuo y muestra directamente los resultados.

## Despliegue en GitHub Pages

GitHub Actions puede generar la edición diariamente y desplegarla automáticamente en GitHub Pages. El flujo de trabajo usa el archivo HTML más reciente como `index.html`, de modo que la página principal siempre muestra la última edición. Las ediciones anteriores se conservan bajo `/ediciones/` en el sitio publicado.
