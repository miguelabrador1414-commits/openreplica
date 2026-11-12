# Modelos y configuración del agente

OpenReplica viene configurado para usarse con modelos gratuitos de opencode. El
valor por defecto es:

```text
opencode/deepseek-v4.1-flash-free
```

No es una dependencia externa ni una clave. Es el identificador que opencode
usa para enrutar la petición al proveedor.

## Dónde se configura

En dos sitios, y deben coincidir:

`.opencode/opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "replica",
  "model": "opencode/deepseek-v4.1-flash-free"
}
```

`.opencode/agents/replica.md`

```yaml
---
description: ...
mode: primary
model: opencode/deepseek-v4.1-flash-free
temperature: 0.2
---
```

El archivo del agente manda cuando opencode carga ese agente. El archivo de
proyecto fija el modelo por defecto del proyecto y el agente que se abre. Si
cambias uno y no el otro, puedes acabar con dos modelos distintos según cómo
inicies la sesión. Cámbialos juntos.

## Por qué DeepSeek Flash

La elección prioriza coste cero y velocidad. El trabajo pesado de OpenReplica no
está en el modelo: está en el CLI determinista y en las puertas.

- `parity`, `imgdiff`, `contrast`, `sweep`, `reviews` y `listing` calculan con
  Python, no con el modelo.
- Las puertas comprueban archivos y valores concretos.
- Las skills obligan a escribir evidencia antes de avanzar.

Eso reduce el riesgo de que un modelo barato invente un resultado. Aun así, usa
un modelo que sepa llamar herramientas y seguir instrucciones largas. Si ves
que se salta pasos, sube de modelo para la fase de reconstrucción o de tests,
donde hay más juicio.

## Cambiar de modelo

1. Edita `.opencode/opencode.json`.
2. Edita `.opencode/agents/replica.md`.
3. Reinicia opencode.
4. Comprueba con `replica doctor` y abre una sesión nueva.

Ejemplo con otro modelo:

```json
"model": "opencode/otro-modelo"
```

El prefijo del proveedor es obligatorio. Un identificador sin proveedor puede
fallar al cargar.

## Temperatura

El agente usa `temperature: 0.2`. Baja creatividad y menos variación entre
ejecuciones. Para fases de marca o textos de lanzamiento puedes subirla, pero
para recon, build y tests conviene mantenerla baja: queremos evidencia
repetible, no prosa distinta cada vez.

## Permisos

El agente pide confirmación para acciones destructivas o con efectos externos:

- `rm *`
- `git push*`
- `npm publish*`
- `gh *`
- `curl *`

El resto de comandos de shell están permitidos para que el flujo no se detenga
a cada paso. Si trabajas en un entorno sensible, revisa
`.opencode/agents/replica.md` y endurece la lista.

## Coste y privacidad

El pack no envía datos a ningún servicio propio. opencode envía las peticiones
al proveedor del modelo que elijas. No pegues secretos, credenciales ni datos
personales en los prompts. Las capturas y reseñas se guardan en tu proyecto,
no en este repositorio.

## Modelos sin herramientas

Un modelo que solo genera texto no puede ejecutar el CLI ni leer archivos. Las
skills asumen acceso a herramientas. Si tu modelo no las tiene, usa el CLI a
mano y sigue las fases como guía, pero no esperes que el agente complete el
flujo solo.
