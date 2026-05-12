# IoT Device Registry

Full-stack app for registering MQTT devices and generating integration templates.

# Project structure

```text
iot-device-registry/
├── backend/   FastAPI
└── frontend/  Nuxt


Backend setup — Windows
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install "fastapi[standard]" "psycopg[binary]" python-dotenv


If using SSH tunnel to Radxa:
ssh -L 5433:localhost:5432 radxa@RADXA_IP


Backend setup — Linux / Radxa
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install "fastapi[standard]" "psycopg[binary]" python-dotenv

Frontend setup
cd frontend
npm install
npm install --save-dev @types/node(in case nuxt.config has error)

Run command: 
cd backend
fastapi dev app/main.py / fastapi run app/main.py --host 0.0.0.0 --port 8000

cd frontend
npm run dev