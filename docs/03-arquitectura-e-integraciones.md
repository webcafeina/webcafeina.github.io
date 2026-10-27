# 03 · Arquitectura e integraciones

## Capas
```
[Entradas]            [Núcleo]                          [Salidas]
Voz móvil ─┐          Ingesta → Transcripción →         Tarjeta "Lo siguiente"
Plaud ─────┼──────►   Clasificación/Extracción →  ────► Notificación proactiva
Pulsera ───┤          Memoria (bandeja + contexto)      Revisión diaria/semanal
Calendario ┘          Motor de intervención              Exportación (calendario, tareas)
                      Capa corporal (contexto)
```

## Integraciones
| Integración | Estado de la información | Riesgo | Decisión |
|---|---|---|---|
| **Plaud** (NotePin / Note) | Plataforma de desarrolladores lanzada en oct 2025 con APIs/SDK; el SDK iOS exige claves de app, token de vinculación y token de partner | Condiciones, precio y alcance **sin confirmar** | Solicitar acceso a su programa; no bloquea el MVP |
| **Google Health API** (Fitbit Air) | ~31 tipos de datos, webhooks, HRV; acceso vía proyecto de Google Cloud y OAuth | La API web antigua de Fitbit se apaga hacia el 30 oct–2 nov 2026; tokens antiguos no migran; puede requerir revisión de aplicación | Construir solo sobre la API nueva |
| **Notas de voz del móvil** | Siempre disponibles | Bajo | Canal base del MVP |
| **Apple Salud / Health Connect** | Agregador de varios dispositivos | Permisos por plataforma | Alternativa agnóstica del dispositivo |
| **Calendario** (Google/Apple) | Contexto de agenda | Bajo | P0 |
| **CGM** (Libre, Dexcom) | Acceso variable | Datos sensibles y regulación del sensor | P2, vía el agregador de salud |

## Principio "integrar, no depender"
Cada integración implementa la misma interfaz (`CapturaSource`, `SeñalCorporal`). Si una API desaparece, el núcleo sigue funcionando con el resto.

## Privacidad por diseño
- Los datos de salud son **categoría especial** (art. 9 RGPD): base legal = consentimiento explícito y granular.
- Minimización: no guardar audio tras transcribir salvo que el usuario lo pida.
- Proceso local (en el dispositivo) para clasificación sencilla; nube europea para lo pesado.
- Si se usa un LLM de terceros: contrato de encargado (art. 28), sin entrenamiento con datos del usuario, región UE.
- Derecho de supresión con un solo botón; exportación en formato abierto.
- Evaluación de impacto (EIPD/DPIA) antes del lanzamiento: probable obligación por tratar datos de salud a escala.

## Elección técnica (a decidir tras el prototipo)
| Opción | Pros | Contras |
|---|---|---|
| App nativa iOS primero | Mejor captura (Action Button, widgets, Shortcuts), Apple Salud | Excluye Android |
| PWA + atajos | Rápido de lanzar | Captura en segundo plano limitada |
| Multiplataforma (Flutter/React Native) | Un código | Peor integración con disparadores del SO |

Recomendación provisional: **prototipo iOS o Android nativo según el móvil del fundador**, para validar el hábito antes de ampliar.
