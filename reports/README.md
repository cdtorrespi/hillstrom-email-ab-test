# Reportes

## Figuras

Todas las gráficas del README y de los notebooks se guardan en `figures/` al correr los notebooks.

## Datos para Power BI

Los CSV de `powerbi/` se generan al final de `notebooks/03_segmentos_e_impacto.ipynb`.

| Archivo | Contenido | Granularidad |
|---|---|---|
| `resumen_grupos.csv` | Clientes, visitas, compradores e ingreso por grupo | Un renglón por grupo |
| `efectos_principales.csv` | Efecto de cada comparación con IC 95 %, p-valor y p ajustado por Holm | Métrica × comparación |
| `efectos_por_segmento.csv` | Efecto de cada campaña contra control por segmento, con IC 95 % | Segmento × nivel × campaña |
| `valor_reglas.csv` | Ingreso por cliente esperado de cada regla de envío en el conjunto de prueba | Un renglón por regla |
| `escenarios_impacto.csv` | Utilidad por correo y costo máximo rentable según margen | Margen × campaña |

## Reporte de decisión (una página)

La idea del reporte no es repetir las gráficas del análisis, sino servir como herramienta: alguien de marketing elige un segmento y ve qué campaña conviene y cuánto deja.

**Visuales sugeridos**

1. **Tarjetas:** ingreso incremental por cada 1,000 correos para cada campaña (desde `efectos_principales.csv`, métrica `spend`, multiplicando `diferencia` por 1,000).
2. **Segmentación:** filtros por `segmento` y `nivel` de `efectos_por_segmento.csv`.
3. **Gráfico de barras con barras de error:** `efecto` por `campana` para el segmento elegido, con `ic_inf` e `ic_sup`.
4. **Tabla de escenarios:** `escenarios_impacto.csv` con un parámetro de margen.
5. **Nota fija:** los efectos por segmento son exploratorios; ninguna diferencia entre segmentos se confirmó en la mitad de confirmación.

**Medidas DAX de ejemplo**

```DAX
Ingreso incremental por 1000 =
    SUM ( efectos_por_segmento[efecto] ) * 1000

Ancho IC =
    SUM ( efectos_por_segmento[ic_sup] ) - SUM ( efectos_por_segmento[ic_inf] )

Mejor campaña =
    VAR h = CALCULATE ( SUM ( efectos_por_segmento[efecto] ), efectos_por_segmento[campana] = "Hombre" )
    VAR m = CALCULATE ( SUM ( efectos_por_segmento[efecto] ), efectos_por_segmento[campana] = "Mujer" )
    RETURN IF ( h >= m, "Hombre", "Mujer" )
```
