# Bibliotecas, música y generación de recursos

## Qué hay comprobado

Nacho dispone de **Magnific**. En Claude Code existe un **conector MCP de Magnific** ya
autenticado con la cuenta de Webcafeina: da acceso a catálogo de stock (Freepik), generación
de imagen y vídeo, música, efectos de sonido, voz y utilidades de vídeo.

**Compruébalo tú al empezar, no lo supongas:** el conector puede no estar activo en esta
sesión, y una suscripción web no implica acceso por API.

```text
account_profile   -> identidad de la cuenta
account_balance   -> plan y créditos disponibles
stock_search      -> catálogo (no genera, no gasta créditos)
simulate_cost     -> coste estimado ANTES de generar
```

**El modo ilimitado del plan puede no aplicarse en una sesión de API: las generaciones
consumen créditos.** Consulta `account_balance` y avisa a Nacho **antes** de cualquier
generación de pago.

No uses la clave de Gemini para esto: son servicios distintos.

## Reglas

- La selección de bibliotecas entra en el **brief** y en el **guion**, con función narrativa,
  fuente y presupuesto. No se cuela material en el montaje sin que esté acordado.
- Registra por recurso: qué es, enlace o ruta, licencia y atribución, y **coste comprobable**.
  Ese registro es el manifiesto de recursos de la entrega.
- Propón generación **solo si aporta** y está acordada.
- **Nunca uses stock ni generación para fingir reacciones reales, producto o procesos
  acreditados de una marca.** En testimonios, esto no es un matiz: es mentir sobre el cliente.
- Actualizar el agente no autoriza compras, generaciones ni descargas ilimitadas.

## Música y licencias

Pregunta si la música la aporta el cliente, sale de biblioteca o se genera. Registra la
licencia concreta y si permite el uso previsto (publicidad, redes, cliente final). Si no
puedes comprobar la licencia, no la uses.
