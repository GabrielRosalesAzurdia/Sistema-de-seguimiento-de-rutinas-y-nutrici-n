# Club Fitness App

Sistema de seguimiento de rutinas y nutrición — Gimnasio Fitness Club,
Jocotenango, Sacatepéquez. Proyecto de graduación, Ingeniería en
Sistemas de Información, Universidad Mariano Gálvez de Guatemala.

> 📄 **Empieza por [`CLAUDE.md`](./CLAUDE.md)** — contiene todo el
> contexto del anteproyecto (decisiones de negocio, requerimientos,
> pantallas, terminología) necesario para continuar el desarrollo.

## Estructura

```
club_fitness_app/
├── backend/     # Django REST Framework + PostgreSQL (API + panel admin)
├── mobile/      # App Flutter (Android) para los usuarios del gimnasio
├── ml/          # Entrenamiento de modelos scikit-learn (offline)
├── docs/        # Resumen de requerimientos levantados con el gimnasio
├── docker-compose.yml
└── CLAUDE.md    # Contexto completo para retomar el desarrollo
```

## Quickstart

### Backend

```bash
cd backend
cp .env.example .env
python -m venv venv && source venv/bin/activate   # o venv\Scripts\activate en Windows
pip install -r requirements.txt

# Levantar PostgreSQL con Docker (o usa tu propia instancia local)
cd .. && docker compose up -d db && cd backend

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API disponible en `http://localhost:8000/api/`, panel Django admin en
`http://localhost:8000/admin/`.

### Mobile (Flutter)

```bash
cd mobile
flutter create .
flutter pub get
flutter run
```

Ajusta `ApiClient.baseUrl` en `lib/core/api_client.dart` según tu
entorno (emulador Android usa `10.0.2.2`, dispositivo físico usa la IP
de tu máquina en la red local).

### Todo junto con Docker

```bash
docker compose up
```

## Stack

- **Mobile**: Flutter (Android)
- **Backend**: Django REST Framework, JWT auth
- **Base de datos**: PostgreSQL
- **ML**: scikit-learn (LinearRegression, RandomForestRegressor)
- **Hosting objetivo**: Render

## Estado

Scaffold inicial generado a partir del anteproyecto y los mockups
validados con el gimnasio. Ver `CLAUDE.md` sección 8 para los
próximos pasos recomendados.


MeDasMiedoUmg
