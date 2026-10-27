# 02 · Especificaciones funcionales

Prioridad: **P0** = MVP · **P1** = tras validar hábito · **P2** = exploratorio.

## Módulo A · Volcado rápido (memoria de trabajo externa)
| ID | Requisito | Prioridad | Criterio de aceptación |
|---|---|---|---|
| A1 | Captura de voz con un solo gesto (botón físico, atajo, widget, Action Button, doble toque en pulsera si el SO lo permite) | P0 | ≤ 2 s desde el gesto hasta grabar |
| A2 | Transcripción automática sin revisar | P0 | La nota queda guardada aunque falle la transcripción |
| A3 | Clasificación automática: tarea, idea, recordatorio, compra, emoción, preocupación | P0 | El usuario no tiene que elegir categoría |
| A4 | Extracción de fecha/hora/persona si se menciona | P0 | Se propone, no se impone |
| A5 | Importación desde Plaud y notas de voz del móvil | P1 | Sin duplicados |
| A6 | Captura offline | P0 | Se sincroniza al recuperar red |
| A7 | Captura con pantalla bloqueada y manos ocupadas | P1 | Funciona con auriculares o reloj |
| A8 | "Vuelve a lo que estaba diciendo": recuperar el hilo de la última captura interrumpida | P1 | Resumen de 1 frase |

## Módulo B · Recuperación de foco (función ejecutiva)
| ID | Requisito | Prioridad |
|---|---|---|
| B1 | Pregunta proactiva de re-enfoque ("¿Sigues con X o has cambiado?") según calendario y patrón | P0 |
| B2 | Una sola tarea visible: **"Lo siguiente"** | P0 |
| B3 | Descomposición de una tarea en pasos mínimos bajo petición | P0 |
| B4 | Temporizador visual y arranque de 2 min ("solo empieza") | P1 |
| B5 | Detección de deriva (cambios rápidos de app o inactividad) con permiso explícito | P2 |
| B6 | Body doubling: sesión silenciosa acompañada, humana o IA | P2 |
| B7 | Transiciones guiadas entre actividades | P1 |
| B8 | Modo "descarga mental" antes de dormir (3 min de voz libre) | P1 |

## Módulo C · Revisión y cierre del bucle
| ID | Requisito | Prioridad |
|---|---|---|
| C1 | Revisión diaria automática de 2 min: 3 elementos máximo | P0 |
| C2 | Revisión semanal: convertir bandeja en proyecto/tarea/archivo/descarte | P1 |
| C3 | Caducidad amable: lo que lleva 30 días sin tocar se propone archivar, sin culpa | P0 |
| C4 | Límite de bandeja (señal de saturación) | P1 |

## Módulo D · Cuerpo (todo lo que afecta a MT y FE)
| ID | Señal | Fuente | Uso | Prioridad |
|---|---|---|---|---|
| D1 | Sueño (duración, regularidad, hora de acostarse) | Google Health API / otros | Ajustar carga y tono del día | P1 |
| D2 | HRV y FC en reposo | Fitbit Air vía Google Health API | Indicador de estrés/recuperación | P1 |
| D3 | Actividad y sedentarismo | Pulsera | Sugerir pausas de movimiento | P1 |
| D4 | Exposición a luz matinal | Manual o sensor | Rutina circadiana | P2 |
| D5 | Glucosa | CGM opcional | Experimento n=1, sin claims | P2 |
| D6 | Comidas y cafeína | Voz ("he comido") | Correlaciones personales | P1 |
| D7 | Medicación (hora de toma) | Manual por voz | Registro, nunca recomendación de dosis | P1 |
| D8 | Correlaciones personales ("tus días con <6 h de sueño tienes X% menos capturas ejecutadas") | Interno | Presentación suave | P2 |

**Regla:** el módulo D solo muestra patrones propios del usuario y propone experimentos; no emite consejos médicos.

## Módulo E · Construcción del hábito
- Onboarding de 3 minutos con una sola tarea: dictar la primera nota.
- Anclajes: asociar la captura a un evento ya existente (llegar a casa, abrir el portátil, dejar de caminar).
- Refuerzo positivo variable; sin rachas punitivas.
- Si el usuario no ha capturado en 3 días, el sistema envía **un** mensaje; si no hay respuesta, baja la frecuencia en lugar de insistir.

## Requisitos no funcionales
| Área | Requisito |
|---|---|
| Latencia | Captura inmediata; procesamiento asíncrono |
| Accesibilidad | WCAG 2.2 AA, modo bajo estímulo visual |
| Privacidad | Cifrado en tránsito y reposo, borrado completo en 1 acción, opción de proceso local |
| Fiabilidad | Nunca perder una captura |
| Notificaciones | Presupuesto diario máximo configurable |
