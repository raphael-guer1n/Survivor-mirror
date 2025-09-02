##
## EPITECH PROJECT, 2025
## JEB-Incubator
## File description:
## Makefile
##

include .env
export $(shell sed 's/=.*//' .env)

DB_CONTAINER = db
DB_NAME = $(MYSQL_DATABASE)
DB_USER = $(MYSQL_USER)
DB_PASS = $(MYSQL_PASSWORD)

up:
	docker compose up -d

down:
	docker compose down --remove-orphans

shell:
	docker compose exec -it $(DB_CONTAINER) mariadb -u$(DB_USER) -p$(DB_PASS) $(DB_NAME)

dump:
	docker compose exec $(DB_CONTAINER) mysqldump -u$(DB_USER) -p$(DB_PASS) $(DB_NAME) > dump.sql
	@echo "Dumped in dump.sql"

restore:
	docker compose exec -T $(DB_CONTAINER) mariadb -u$(DB_USER) -p$(DB_PASS) $(DB_NAME) < dump.sql
	@echo "Base restored from dump.sql"
