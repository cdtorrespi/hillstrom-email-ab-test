# Datos

El dataset original está en `data/raw/hillstrom.csv`, sin modificaciones. Para validarlo (o descargarlo si no está):

```bash
python src/descargar_datos.py
```

El script revisa que tenga las 12 columnas y 64,000 filas esperadas.

Si necesitas volver a descargarlo y el enlace falla, baja el archivo manualmente desde el [blog de MineThatData](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html) o desde Kaggle (buscar "Hillstrom email marketing") y guárdalo con ese nombre.

## Fuente

Kevin Hillstrom, *MineThatData E-Mail Analytics and Data Mining Challenge* (2008).

| | |
|---|---|
| Clientes | 64,000 que compraron en los últimos 12 meses |
| Grupos | Correo de hombre, correo de mujer, sin correo (asignación aleatoria) |
| Ventana de resultados | 2 semanas después del envío |
| Columnas | 12 (ver diccionario en `notebooks/01_validacion.ipynb`) |
| Tamaño | ~3.8 MB |
