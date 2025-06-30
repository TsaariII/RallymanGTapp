COMPOSE_FILE = docker-compose.dev.yml
ENV_FILE = .env

RESET = \033[0m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
BLUE = \033[34m

schedule: build start

build:
	@echo "$(BLUE)Building backend...$(RESET)"
	docker compose -f $(COMPOSE_FILE) build backend
	@echo "$(BLUE)Building frontend...$(RESET)"
	docker compose -f $(COMPOSE_FILE) build frontend
	@echo "$(BLUE)Building nginx...$(RESET)"
	docker compose -f $(COMPOSE_FILE) build nginx

start:
	@echo "$(GREEN)Starting containers...$(RESET)"
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)Services are running:$(RESET)"
	@echo "$(GREEN)- Frontend: https://localhost$(RESET)"
	@echo "$(GREEN)- Backend API: https://localhost/api/$(RESET)"

stop:
	@echo "$(YELLOW)Stopping containers...$(RESET)"
	docker compose -f $(COMPOSE_FILE) down

clean:
	@echo "$(RED)Cleaning up Docker resources...$(RESET)"
	docker compose -f $(COMPOSE_FILE) down -v
	@echo "$(RED)Removing named volumes...$(RESET)"
	docker volume ls -q --filter name=$$(basename $$(pwd)) | xargs -r docker volume rm || true

fclean: clean
	@echo "$(RED)Removing all unused Docker volumes...$(RESET)"
	docker volume prune -f
	@echo "$(RED)Removing all Docker images...$(RESET)"
	docker rmi -f $$(docker images -q) || true

logs:
	@echo "$(BLUE)Showing logs...$(RESET)"
	docker compose -f $(COMPOSE_FILE) logs -f

logs-backend:
	@echo "$(BLUE)Showing backend logs...$(RESET)"
	docker compose -f $(COMPOSE_FILE) logs -f backend

logs-frontend:
	@echo "$(BLUE)Showing frontend logs...$(RESET)"
	docker compose -f $(COMPOSE_FILE) logs -f frontend

logs-nginx:
	@echo "$(BLUE)Showing nginx logs...$(RESET)"
	docker compose -f $(COMPOSE_FILE) logs -f nginx

help:
	@echo "$(BLUE)Available commands:$(RESET)"
	@echo " make build 		- Build docker images"
	@echo " make start 		- Start containers in detached mode"
	@echo " make stop 		- Stop containers"
	@echo " make clean 		- Clean up container resources"
	@echo " make fclean 		- Cleans up container resources and wipes database"
	@echo " Make logs		- View logs from all containers"
	@echo " make logs-backend 	- View logs from backend"
	@echo " make logs-frontend 	- View logs from frontend"
	@echo " make logs-nginx 	- View logs from nginx"


.PHONY: build start stop clean fclean
