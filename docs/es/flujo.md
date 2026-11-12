# Flujo de trabajo

OpenReplica trabaja en once fases. Cada fase produce artefactos en `replica/` y
tiene una puerta que comprueba la evidencia. El orden importa: la fase siguiente
lee lo que escribió la anterior.

```text
recon -> architect -> design -> build -> backend -> test -> diff
      -> entrepreneur -> brand -> launch -> deploy
```

## Estado del proyecto

Al empezar, crea el estado:

```bash
replica init
```

Esto crea `replica/state.json`. El archivo guarda qué fase está pendiente, en
curso o pasada, las notas y los artefactos. No guarda secretos.

Para ver dónde estás:

```bash
replica status
```

La salida muestra la fase actual y la siguiente. También puedes pedir JSON:

```bash
replica status --json
```

## Ciclo de una fase

```bash
replica mark recon in_progress
# ejecuta la skill y produce los artefactos
replica gate recon
# si sale 0, la evidencia alcanza
replica mark recon passed
```

Si la puerta falla, sale con código 2 y lista lo que falta. Corrige el artefacto
y vuelve a ejecutar `replica gate`. No marques la fase como pasada a mano para
saltarte la puerta: el estado quedaría mintiendo y la fase siguiente leería
evidencia incompleta.

Estados válidos:

| Estado | Significado |
| --- | --- |
| `pending` | No empezó. |
| `in_progress` | Se está trabajando. |
| `blocked` | Hay un impedimento externo. |
| `passed` | La puerta pasó. |
| `skipped` | La fase no aplica. Úsalo solo con un motivo en `--notes`. |

## Las fases

### 1. Recon

Comando: `/replica-recon`

Estudia la app original: pantallas, flujos, funciones, modelo de datos inferido
y límites. Produce `replica/recon.md`, `replica/features.csv` y capturas.

La puerta exige mapa de pantallas, matriz de funciones con prioridades y al
menos un must-have. Si no hay evidencia suficiente, no deja avanzar.

### 2. Architect

Comando: `/replica-architect`

Elige stack, esquema, rutas y orden de construcción. Produce
`replica/architecture.md`.

La puerta exige stack, esquema, rutas y orden. No valida que tus decisiones sean
buenas; valida que estén escritas y sean coherentes.

### 3. Design

Comando: `/replica-design`

Convierte las capturas en tokens: colores, tipografía, espaciado y componentes.
Produce `replica/design/tokens.json`.

La puerta comprueba que los tokens existan y que el contraste WCAG AA pase.

### 4. Build

Comando: `/replica-build`

Construye la app por partes: shell, flujo principal y después cada pantalla con
sus estados. Actualiza la matriz de funciones y guarda capturas del clon.

La puerta exige funciones implementadas y capturas. Si una función está marcada
como hecha pero no tiene evidencia, no pasa.

### 5. Backend

Comando: `/replica-backend`

Añade registro, sesión, base de datos, pagos e integraciones. Produce
migraciones, código de servidor y `replica/backend.md`.

La puerta exige notas de backend, un `.env.example` y que no haya secretos
reales en los archivos versionados.

### 6. Test

Comando: `/replica-test`

Escribe el plan de pruebas desde los flujos, tests e2e para caminos felices y
casos límite, y registra bugs por severidad en `replica/bugs.md`.

La puerta exige plan y que no queden bugs S1 o S2 abiertos.

### 7. Diff

Comando: `/replica-diff`

Compara el clon con la original. Puntúa funciones y diferencias visuales.
Produce `replica/parity.json` e imágenes de diferencias.

La puerta exige paridad mínima de 70. En deploy la exigencia sube a 80.

### 8. Entrepreneur

Comando: `/replica-entrepreneur`

Lee reseñas reales de la original, las ordena por queja y petición, y propone
mejoras y un ángulo de posicionamiento. Produce `replica/reviews.csv`,
`replica/feedback.md` y `replica/fixes.md`.

La puerta exige reseñas con enlace y un plan de mejoras. Cada cita debe ser
literal y verificable.

### 9. Brand

Comando: `/replica-brand`

Pone nombre nuevo, paleta, logo y voz. Después barre el código para comprobar
que no queda nada de la original.

La puerta exige el barrido limpio. Si aparece el nombre, dominio o color de la
original, bloquea.

### 10. Launch

Comando: `/replica-launch`

Escribe la landing, el precio y la ficha de tienda. Produce
`replica/launch/` y `replica/listing.json`.

La puerta ejecuta el lint de la ficha: límites de caracteres, afirmaciones en el
título y nombres prohibidos.

### 11. Deploy

Comando: `/replica-deploy`

Ejecuta el preflight completo, prepara producción y entrega los registros DNS.
Produce `replica/preflight.md`.

La puerta exige tests, paridad mínima 80, barrido limpio y ficha sin errores.
Si algo falla, no publica.

## Reanudar y repetir

Puedes volver a una fase anterior y repetirla. Actualiza sus artefactos y vuelve
a pasar la puerta. Las fases siguientes no se actualizan solas: si cambias la
matriz de funciones, vuelve a ejecutar parity y diff.

Para ver el estado en cualquier momento:

```bash
replica status
```

Para trabajar solo una fase:

```bash
/replica-entrepreneur
```

No necesitas haber construido la app para leer el mercado de la original.
