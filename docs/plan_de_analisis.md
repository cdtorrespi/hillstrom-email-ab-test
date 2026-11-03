# Plan de análisis

Escrito antes de calcular efectos. La idea es fijar desde el inicio qué se mide, cómo y con qué criterio se decide, para no escoger después la métrica o el segmento que salga mejor.

## 1. Contexto

Una tienda de ropa en línea tomó a 64,000 clientes que compraron en los últimos 12 meses y los asignó al azar a tres grupos:

| Grupo | Tratamiento |
|---|---|
| Control | No recibe correo |
| Hombre | Recibe un correo con mercancía de hombre |
| Mujer | Recibe un correo con mercancía de mujer |

Durante las dos semanas siguientes se registró si el cliente visitó el sitio, si compró y cuánto gastó.

## 2. Pregunta de negocio

¿Conviene mandar campañas por correo? Si sí, ¿cuál de las dos y a qué clientes?

## 3. Unidad de análisis y población

- Unidad: cliente (una fila por cliente).
- Análisis por intención de tratar (ITT): se compara a todos los clientes según el grupo asignado, abrieran o no el correo. El dataset no trae aperturas, así que este es además el único análisis posible, y es el que importa para decidir: la empresa controla a quién manda, no quién abre.

## 4. Métricas

| Tipo | Métrica | Definición |
|---|---|---|
| Principal | Ingreso por cliente | Promedio de `spend` en las dos semanas, incluyendo ceros |
| Secundaria | Tasa de visita | Proporción con `visit = 1` |
| Secundaria | Tasa de conversión | Proporción con `conversion = 1` |
| Descriptiva | Ticket promedio | `spend` promedio entre quienes compraron |

**Por qué el ingreso es la principal:** la decisión final es de dinero. La visita es más fácil de mover y de detectar, pero una campaña que trae visitas sin compras no paga.

**Guardrails:** en un experimento real mediría bajas de la lista de correo y quejas de spam. El dataset no las incluye; queda como limitación.

**El ticket promedio es solo descriptivo:** se calcula sobre quienes compraron, que es un grupo definido después del tratamiento. Compararlo entre grupos no tiene interpretación causal.

## 5. Hipótesis

Para cada métrica:

- H1: Hombre vs. Control
- H2: Mujer vs. Control
- H3: Hombre vs. Mujer

Pruebas bilaterales con α = 0.05. Las tres comparaciones de cada métrica se ajustan con Holm.

## 6. Métodos

| Paso | Método |
|---|---|
| Asignación balanceada | Prueba chi-cuadrada de *sample ratio mismatch* contra 1/3 por grupo |
| Balance de covariables | Diferencia estandarizada de medias (umbral de alerta: \|DEM\| > 0.1) |
| Poder | Efecto mínimo detectable con 80 % de poder para cada métrica |
| Proporciones | Diferencia de proporciones, IC de Wald y prueba z |
| Ingreso | Diferencia de medias con prueba de Welch y bootstrap (10,000 réplicas, IC por percentiles) |

`spend` tiene muchísimos ceros y una cola larga, así que el bootstrap sirve para confirmar que la aproximación normal se sostiene. No se recortan valores extremos en el análisis principal: son compras reales y el ingreso total depende de ellas. Como prueba de sensibilidad se repite con `spend` acotado al percentil 99.

## 7. Efectos por segmento

Solo con variables medidas antes del experimento:

- `newbie` (cliente nuevo en los últimos 12 meses)
- `channel` (canal de compra: Phone, Web, Multichannel)
- `zip_code` (Urban, Surburban, Rural)
- `mens` y `womens` (compró mercancía de hombre / de mujer en el último año)
- `recency` agrupada en terciles
- `history` agrupada en terciles

Para no confundir ruido con hallazgos, la muestra se divide al azar en dos mitades:

1. **Exploración:** se estiman los efectos por segmento y se eligen las interacciones prometedoras.
2. **Confirmación:** solo esas interacciones se prueban otra vez, con ajuste de Holm.

Lo que no se confirme se reporta como exploratorio.

## 8. Modelo de uplift (extensión)

Un modelo por grupo (*T-learner*) predice el ingreso esperado de cada cliente con y sin cada correo. La regla resultante ("mandar a cada cliente el correo con mayor ingreso incremental esperado") se evalúa en un 30 % de los datos que el modelo nunca vio, con un estimador de ponderación por probabilidad inversa, y se compara contra reglas simples: no mandar, mandar a todos el de hombre y mandar a todos el de mujer.

## 9. Criterio de decisión

- Una campaña se recomienda si el límite inferior del IC 95 % del ingreso incremental por cliente es mayor que el costo de envío.
- Entre dos campañas recomendables se elige la de mayor ingreso incremental, solo si la diferencia (H3) es significativa; si no, se elige por costo o se prueban ambas otra vez.
- Una regla por segmento o un modelo solo se recomienda si supera a la mejor regla simple en datos que no se usaron para construirlo (mitad de confirmación o conjunto de prueba).

## 10. Limitaciones conocidas

- El experimento es de 2008; el comportamiento con correo electrónico hoy es distinto.
- No hay datos de costo, margen ni bajas de la lista; los supuestos de costo se marcan como tales.
- Ventana de dos semanas: no mide efectos de largo plazo ni canibalización de compras futuras.
