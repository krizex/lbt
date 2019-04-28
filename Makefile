IMAGE_LABEL := krizex/lbt
CONTAINER_PORT := 8000
HOST_DEBUG_PORT := 8000
CUR_DIR := $(shell pwd)
APP_CONTAINER_NAME := lbt

.PHONY: build
build:
	mkdir -p _build/datatmp
	docker build -t $(IMAGE_LABEL) .

.PHONY: debug
debug:
	docker run -it --rm \
	--name $(APP_CONTAINER_NAME) \
	-p $(HOST_DEBUG_PORT):$(CONTAINER_PORT) \
	-v $(CUR_DIR)/src:/app \
	$(IMAGE_LABEL):latest /bin/bash

.PHONY: run stop restart attach

run:
	docker run --rm \
	--name $(APP_CONTAINER_NAME) \
	$(IMAGE_LABEL):latest

attach:
	docker exec -it $(APP_CONTAINER_NAME) /bin/bash

stop:
	docker-compose down

restart: stop run


.PHONY: push pull
push:
	docker push ${IMAGE_LABEL}

pull:
	docker pull ${IMAGE_LABEL}
