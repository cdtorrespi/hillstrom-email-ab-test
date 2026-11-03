# Campañas por correo: análisis de un experimento A/B/n

Una tienda de ropa en línea tenía dos campañas de correo, una con mercancía de hombre y otra de mujer, y quería saber si valía la pena mandarlas, cuál de las dos y a quién. Para responderlo tomó a 64,000 clientes y los repartió al azar en tres grupos: unos recibieron el correo de hombre, otros el de mujer y otros ninguno. Dos semanas después se midió quién visitó el sitio, quién compró y cuánto gastó.

Este repositorio es mi análisis de ese experimento, desde validar que estuviera bien hecho hasta estimar cuánto dinero deja cada decisión.

Herramientas: PostgreSQL y Python (pandas, NumPy, SciPy, scikit-learn, matplotlib). Al final se exportan tablas listas para armar un reporte en Power BI.

---

## La respuesta corta

Conviene mandar el correo de hombre a toda la base. Deja unos 770 USD adicionales por cada 1,000 correos, casi el doble que el de mujer, y no encontré ningún segmento de clientes donde convenga hacer otra cosa.

| | Sin correo | Correo de mujer | Correo de hombre |
|---|---|---|---|
| Tasa de visita | 10.6 % | 15.1 % | 18.3 % |
| Tasa de conversión | 0.57 % | 0.88 % | 1.25 % |
| Ingreso por cliente (2 semanas) | $0.65 | $1.08 | $1.42 |
| Ingreso incremental por cada 1,000 correos | — | $424 | $770 |

En una lista del tamaño de la del experimento, eso equivale a unos 49 mil USD adicionales en dos semanas (IC 95 %: 31 mil a 67 mil).

![Efectos principales](reports/figures/02_efectos_principales.png)

## Cómo llegué a esa conclusión

### Primero, revisar que el experimento fuera confiable

Antes de comparar resultados quise descartar que el experimento estuviera mal hecho, porque si la asignación al azar falló, cualquier diferencia entre grupos podría deberse a otra cosa. Los tres grupos quedaron casi del mismo tamaño (21,306 / 21,307 / 21,387; prueba de SRM, p = 0.90) y son comparables en todas las variables previas al envío (diferencia estandarizada máxima: 0.014).

También encontré una advertencia importante: más del 99 % de los clientes no compra nada, así que el ingreso por cliente es muy ruidoso. Con este tamaño de muestra, el experimento solo podía detectar efectos de unos 0.31 USD por cliente (48 % del control) con 80 % de poder. Para las visitas el poder es mucho mayor. Eso me obligó a ser cuidadoso con cualquier conclusión sobre grupos pequeños.

Para no acomodar el análisis a los resultados, escribí el [plan de análisis](docs/plan_de_analisis.md) antes de calcular cualquier efecto: qué métricas, qué pruebas y qué criterio de decisión.

![Distribución del gasto](reports/figures/01_distribucion_gasto.png)

### Después, medir si las campañas funcionan

Las dos funcionan. Frente a no mandar correo, ambas aumentan visitas, compras e ingreso, y las nueve comparaciones siguen siendo significativas después de ajustar por comparaciones múltiples con el método de Holm.

El correo de hombre gana con claridad: deja +0.77 USD por cliente frente al control (IC 95 %: 0.49 a 1.05), contra +0.42 del de mujer. La diferencia entre los dos (+0.35 USD, IC 95 %: 0.03 a 0.66) también es significativa (p ajustado = 0.03).

Quise saber de dónde salía ese efecto. El ticket promedio es parecido en los tres grupos, así que el correo parece funcionar porque compra más gente, no porque cada quien gaste más. Lo tomo como descriptivo, porque el ticket solo se calcula sobre quienes compraron.

Para comprobar que el resultado no dependía del método, repetí los intervalos con bootstrap (10,000 réplicas), que difieren de los de Welch en menos de 0.01 USD, y acoté el gasto al percentil 95 de los compradores. Ninguna conclusión cambió.

### La tentación de personalizar

El siguiente paso natural era preguntar si algunos clientes responden mejor a un correo que a otro. Si fuera así, mandar a cada quien el que le conviene dejaría más dinero que mandar el mismo a todos.

Para no engañarme con resultados casuales, dividí la muestra al azar en dos mitades: una para explorar y otra para confirmar. En la primera, dos diferencias del correo de mujer parecían prometedoras (clientes nuevos y canal de compra, p < 0.10). En la mitad de confirmación ninguna se repitió (p = 0.72 y 0.94). Solo usé variables medidas antes del envío, porque segmentar por algo que el correo pudo cambiar, como haber visitado el sitio, rompería la aleatorización.

También probé un modelo de uplift (T-learner) que elige el correo para cada cliente. Lo ajusté en un conjunto de validación y lo evalué una sola vez en un 30 % de datos que no había visto. Tampoco le ganó a la regla simple: −0.15 USD por cliente (IC 95 %: −0.41 a +0.10).

De forma exploratoria, el correo de hombre tiene efecto positivo en los 18 segmentos revisados y es el mejor en 15. Con el poder disponible por segmento, no encontrar diferencias no prueba que no existan, pero sí que no hay evidencia para complicar la estrategia.

![Valor de cada regla](reports/figures/03_valor_reglas.png)

### Por último, traducirlo a dinero

El experimento no incluye costos, así que planteé escenarios. Con un margen de 30 % y usando el límite inferior del intervalo, la campaña sigue dejando ganancia mientras cada correo cueste menos de unos 0.15 USD. Es decir, la recomendación se sostiene incluso con supuestos conservadores.

## Qué haría después

Probaría una versión mejorada del correo de hombre contra la actual, manteniendo siempre un grupo sin correo para seguir midiendo el efecto incremental, y agregaría la tasa de bajas de la lista como métrica de control.

## Limitaciones

- El experimento es de 2008; la respuesta al correo electrónico hoy es distinta.
- No hay datos de costos, márgenes, bajas de la lista ni quejas de spam. Los escenarios de margen y costo son supuestos y están marcados como tales.
- La ventana es de dos semanas: no mide efectos de largo plazo ni si las compras solo se adelantaron.
- El gasto parece estar topado en 499 USD (12 compradores en ese valor).

---

## Dónde está cada parte

| Pregunta | Método | Notebook |
|---|---|---|
| ¿El experimento es válido? | Sample ratio mismatch, balance de covariables, poder estadístico | [01_validacion](notebooks/01_validacion.ipynb) |
| ¿Funcionan las campañas? ¿Cuál es mejor? | Pruebas de proporciones y de Welch, ajuste de Holm, bootstrap, sensibilidad a extremos | [02_analisis](notebooks/02_analisis.ipynb) |
| ¿A quién mandar qué? ¿Cuánto vale? | Interacciones con muestra de confirmación, T-learner evaluado con IPW, escenarios de margen y costo | [03_segmentos_e_impacto](notebooks/03_segmentos_e_impacto.ipynb) |

## Cómo reproducirlo

```bash
git clone https://github.com/cdtorrespi/hillstrom-email-ab-test.git
cd hillstrom-email-ab-test
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/descargar_datos.py   # valida el CSV incluido (o lo descarga si falta)
jupyter notebook notebooks/
```

El CSV ya viene en `data/raw/`. Si lo borras y la descarga automática falla, baja el CSV del [blog de MineThatData](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html) y guárdalo como `data/raw/hillstrom.csv`.

Parte de SQL (opcional; correr desde la raíz del repo porque la carga usa una ruta relativa):

```bash
createdb hillstrom
psql -d hillstrom -f sql/01_crear_tabla.sql
psql -d hillstrom -f sql/02_calidad_datos.sql
psql -d hillstrom -f sql/03_exploracion.sql
```

## Estructura

```
hillstrom-email-ab-test/
├── README.md
├── requirements.txt
├── data/raw/hillstrom.csv    # datos originales (64,000 clientes)
├── docs/
│   └── plan_de_analisis.md   # métricas, hipótesis y criterios fijados antes del análisis
├── sql/
│   ├── 01_crear_tabla.sql    # esquema y carga en PostgreSQL
│   ├── 02_calidad_datos.sql
│   └── 03_exploracion.sql
├── src/
│   ├── descargar_datos.py
│   ├── datos.py              # carga y constantes
│   └── estadistica.py        # pruebas, bootstrap, Holm, MCO robusto
├── notebooks/
│   ├── 01_validacion.ipynb
│   ├── 02_analisis.ipynb
│   └── 03_segmentos_e_impacto.ipynb
└── reports/
    ├── figures/
    └── powerbi/              # tablas para el reporte de decisión
```

## Datos

Kevin Hillstrom, *MineThatData E-Mail Analytics and Data Mining Challenge* (2008). Dataset público de 64,000 clientes que compraron en los últimos 12 meses, asignados al azar a tres grupos y seguidos durante dos semanas después del envío.

## Autor

Carlos Daniel Torres Pillado, analista de datos. Chihuahua, México.

- GitHub: [@cdtorrespi](https://github.com/cdtorrespi)
- Correo: [cdtorres.pi@gmail.com](mailto:cdtorres.pi@gmail.com)
