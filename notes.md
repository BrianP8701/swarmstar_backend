export PYTHONPATH=/Users/brianprzezdziecki/Code/agent_swarm_interface/backend/flask


run fastapi app:
uvicorn main:app --reload
uvicorn main:app --reload --port 5000


pytest -m client_non_blocking

poetry run uvicorn main:app --reload --port 5000