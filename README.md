# Project Voyager
### Codename: DigitalLurker


#### Installation
1. Extract/clone repo.
2. Copy file `.env.dist` as `.env` and fill it with appropriate values.
3. If you do not have PostGis Database you can install it using docker using command `docker docker run --network host --name some-postgis -e POSTGRES_PASSWORD=<password> postgis/postgi` `docker docker run --network host --name some-postgis -e POSTGRES_PASSWORD=<password> postgis/postgi`
4. Create database by `CREATE DATABASE <databasename>;`. If you use docker use `docker exec -ti <container_id>> psql -U postgres`.
5. Build image of DigitalLurker by using command `docker build --network host . -t digital-lurker `.
6. Run project by using `docker run --network host digital-lurker --port 8000:8000 `.
7. DigitalLurker is ready to use.

#### Code documentation
To get to all possible routes in the project, set an environmental variable (or value in the `.env`) `debug = 'True'` and enter the project page you launched with the link `/swagger/`. **Although not all data there is 100% correct.**