# 06 · Regulación (España/UE)

> **No es asesoramiento jurídico.** Es un mapa de riesgos para preparar la consulta con un abogado y, si procede, un consultor regulatorio de producto sanitario. Los puntos marcados **(verificar)** no se han contrastado con fuente primaria en esta sesión.

## Marcos aplicables
| Marco | Por qué aplica | Impacto |
|---|---|---|
| **RGPD** + LOPDGDD | Se tratan datos de salud (art. 9, categoría especial) | Consentimiento explícito, EIPD, registro de tratamientos, DPO probable (verificar), encargados (art. 28), transferencias internacionales |
| **MDR (UE 2017/745)** | Software con finalidad médica puede ser producto sanitario | Define si es bienestar o SaMD; ver sección siguiente |
| **AI Act (UE 2024/1689)** | Uso de IA, posible inferencia biométrica o emocional | Revisar prohibiciones e inferencia de emociones (verificar el alcance exacto) |
| **Ley de servicios digitales y consumo** | Venta B2C, suscripciones | Información precontractual, cancelación sencilla, desistimiento |
| **Publicidad sanitaria** | Los claims de salud están regulados | Control de lo que se promete |
| **ePrivacy / cookies** | Web y notificaciones | Consentimiento |
| **Terceros** | Condiciones de Plaud y de Google Health API | Cumplir los términos; puede haber revisión de app |

## Bienestar vs. producto sanitario
La clasificación depende de la **finalidad prevista** que declaras (en web, publicidad, instrucciones), no de la tecnología.

| Declaración | Probable encuadre |
|---|---|
| "Te ayuda a organizar tus ideas y a recordar tareas" | Productividad / bienestar |
| "Te muestra patrones de tu sueño y tu energía" | Bienestar (si no hay fin médico) |
| "Mejora los síntomas del TDAH" | **Producto sanitario** (terapéutico) |
| "Detecta TDAH" o "evalúa tu TDAH" | **Producto sanitario** (diagnóstico) |
| "Recomienda cambios de medicación" | **Producto sanitario** y práctica clínica |
| "Reduce olvidos en personas con TDAH" (con estudio) | Zona gris: requiere análisis regulatorio |

Referencia comparable: EndeavorRx obtuvo en EEUU autorización De Novo con una indicación estrecha, basada en una medida de atención. Es un ejemplo de que, si se hace afirmación terapéutica, hay que demostrarla en un ensayo ([resumen](https://www.consultantlive.com/news/fda-adhd-game-digital-therapeutic)).

## Lista de claims (borrador)
**Permitido (con evidencia en `05`):**
- "Ayuda a capturar y organizar tus ideas."
- "Te recuerda lo que dijiste que querías hacer."
- "Te muestra cómo se relacionan tu sueño y tu actividad con tus propios días."

**Prohibido hasta tener estudio y encuadre SaMD:**
- "Trata/cura/mejora el TDAH."
- "Mejora tu memoria de trabajo / función ejecutiva" como beneficio clínico.
- "Detecta/diagnostica."
- "Basado en ciencia" sin citar qué ciencia.

## Hoja de ruta a SaMD (opción futura)
1. Diseñar desde ya con trazabilidad: control de versiones, gestión de riesgos (ISO 14971), ciclo de vida de software (IEC 62304).
2. Definir finalidad prevista y clasificar según MDR (regla de software; verificar).
3. Sistema de gestión de calidad (ISO 13485) y organismo notificado.
4. Estudio clínico con un criterio de valoración validado.
5. Marcado CE y registro en la AEMPS (verificar).

## Medidas desde el día 1
- Aviso claro: "No sustituye diagnóstico ni tratamiento".
- Derivación a profesional ante señales de riesgo (ánimo muy bajo, ideación suicida).
- Texto legal y política de privacidad revisados por un abogado.
- EIPD antes de lanzar.
- Registro de qué claims se publican y quién los aprobó.

## Preguntas para el abogado
1. ¿Es obligatorio un DPO?
2. ¿Qué base legal para el procesamiento con LLM de terceros?
3. ¿La inferencia de estado emocional por voz entra en el AI Act?
4. ¿Cómo redactamos los claims para quedar fuera del MDR?
5. ¿Qué implica integrar datos de un CGM?
