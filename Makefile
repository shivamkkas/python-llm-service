APP_NAME = grpc-forecasting
DOCKER_REPO = infinityshiv/edge-python-prognosis-service
RELEASE_VERSION = occ3.0.0_cpu
PLATFORM ?= linux/amd64
ENTRYPOINT = main.py
VENV=.venv
PYTHON=python3

.PHONY: run stop docker hub bin clean

run:
	uv run main.py

stop:
	docker compose down

docker:
	docker build --platform $(PLATFORM) -t $(APP_NAME) .

hub:
	docker tag $(APP_NAME) $(DOCKER_REPO):$(RELEASE_VERSION)
	docker push $(DOCKER_REPO):$(RELEASE_VERSION)

wdfcc:
	docker build --platform $(PLATFORM) -t $(APP_NAME) .
	docker tag $(APP_NAME) $(DOCKER_REPO):$(RELEASE_VERSION)
	docker save -o bin/pyprogimage.tar $(DOCKER_REPO):$(RELEASE_VERSION)

# gpu building
buildgpu:
	docker build --platform $(PLATFORM) -f Dockerfile.gpu -t $(APP_NAME):gpu .

rungpu:
	$(MAKE) buildgpu
	docker compose -f compose.gpu.yaml up -d

stopgpu:
	docker compose -f compose.gpu.yaml down

bin:
	pyinstaller --onefile --name $(APP_NAME) $(ENTRYPOINT)
	
proto:
	$(PYTHON) -m grpc_tools.protoc -I. --python_out=./predictor --grpc_python_out=./predictor predictor.proto

clean:
	find . -type d -name "__pycache__" -exec rm -r {} + && find . -type f -name "*.pyc" -delete
