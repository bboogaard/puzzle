start:
	docker-compose build
	docker-compose start db
	make init
	docker-compose up

init:
	docker-compose run web scripts/init.sh

migrations:
	docker-compose run web scripts/migrations.sh

migrate:
	docker-compose run web scripts/migrate.sh

test:
	docker-compose run web scripts/test.sh

word_squares:
	docker-compose run web python manage.py generate_word_squares 4 10

word_ladders:
	docker-compose run web python manage.py generate_word_ladders 4 10