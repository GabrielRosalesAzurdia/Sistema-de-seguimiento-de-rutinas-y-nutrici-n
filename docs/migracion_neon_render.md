# Migración de base de datos: Neon (free) → Render Postgres (Starter)

Decisión de infraestructura vigente (reemplaza la de
`docs/guia_primer_deploy_produccion.md` — actualízala si aún dice
"Render Postgres Starter" para la base):

- **Web service del backend**: Render, tier **Starter** (siempre
  activo).
- **Base de datos**: **Neon Postgres, tier Free** (100 CU-horas/mes,
  se suspende sola tras 5 min de inactividad y despierta
  automáticamente en la siguiente query — no requiere acción manual).

Este documento cubre **cuándo** y **cómo** migrar de Neon a Render
Postgres Starter si el consumo de CU-horas se acerca al tope mensual,
sin perder datos ni tumbar la app más de unos minutos.

## Cuándo disparar la migración

Durante el período de estudio (octubre-noviembre 2026), revisa
**semanalmente** el consumo de CU-horas en el dashboard de Neon
(Project → Usage).

- Neon free da **100 CU-horas/mes**.
- Si la proyección del mes (consumo actual ÷ días transcurridos ×
  días del mes) se acerca a **~80 CU-horas**, empieza la migración esa
  misma semana — no esperes a estar en el límite. Si Neon suspende el
  proyecto por exceder el tope, la app queda caída hasta el siguiente
  ciclo de facturación, justo lo que se quiere evitar durante la
  ventana de estudio.

## Orden de pasos

1. **Crear la base en Render primero**: Render dashboard → New +  →
   PostgreSQL → **Starter** → Postgres **16** (misma versión que Neon
   y que `docker-compose.yml`) → misma región que el web service.
   Anota `Hostname` (usa el interno), `Port`, `Database`, `Username`,
   `Password`.

2. **Generar el respaldo de Neon**:
   ```bash
   cd backend
   NEON_DATABASE_URL="postgres://usuario:password@host/db" \
     ./scripts/db-migration/backup_neon.sh
   ```
   Esto genera un archivo `.dump` en `scripts/db-migration/backups/`.
   La app puede seguir recibiendo tráfico mientras corre esto — el
   dump es una foto del momento, no bloquea la base.

3. **Restaurar en Render**:
   ```bash
   RENDER_DATABASE_URL="postgres://usuario:password@host/db" \
     ./scripts/db-migration/restore_render.sh scripts/db-migration/backups/neon_XXXXXXXX_XXXXXX.dump
   ```
   Pide una confirmación explícita antes de continuar porque
   sobrescribe lo que exista en la base destino (no debería haber
   nada más que las tablas vacías de las migraciones de Django, pero
   igual confirma). Al final imprime el conteo de filas por tabla.

4. **Verificar los conteos** contra lo que sabes que había en Neon
   (por ejemplo, número de miembros activos, sesiones registradas
   recientes). Si algo se ve claramente mal (conteos en 0 donde no
   deberían), no sigas al siguiente paso — revisa el log del
   `restore_render.sh` antes de cambiar nada en producción.

5. **Actualizar las variables de entorno del Web Service en Render**
   (dashboard → tu web service → Environment): `DB_HOST`, `DB_NAME`,
   `DB_USER`, `DB_PASSWORD`, `DB_PORT` con los valores de la base de
   Render creada en el paso 1 (reemplazando los de Neon).

6. **Reiniciar/redeploy** el web service para que tome las nuevas
   variables (Render lo hace automático al guardar env vars nuevas,
   pero confírmalo en la pestaña Events/Logs).

7. **Probar** `https://<tu-dominio>.onrender.com/panel/login/` y un
   login real antes de dar por cerrada la migración.

8. **No borres el proyecto de Neon todavía.** Déjalo vivo **al menos
   una semana** después de confirmar que Render funciona bien, como
   red de seguridad por si aparece algo que no se verificó en el
   conteo de tablas. Después de esa semana, sí puedes eliminarlo.

## Notas

- Ambos scripts corren `pg_dump`/`pg_restore`/`pg_isready`/`psql`
  dentro de un contenedor Docker (`postgres:16-alpine`) — no hace
  falta instalar el cliente de Postgres en tu máquina, y se garantiza
  la misma versión que usan Neon, Render y el `docker-compose.yml`
  local.
- Los archivos `.dump` en `scripts/db-migration/backups/` están en
  `.gitignore` — contienen datos reales de miembros (peso, medidas,
  teléfono), nunca deben subirse a git.
- Si en algún momento se quisiera migrar de vuelta o hacer un
  respaldo puntual de Render (no solo de Neon), los mismos scripts
  sirven: `backup_neon.sh` no depende de Neon específicamente, solo
  necesita una connection string de Postgres con `sslmode=require`.
