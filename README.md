# Projekt Voyager
### Codename: DigitalLurker


#### Instalacja
1. Wypakuj/sklonuj repozytorium
2. Skopiuj plik `.env.dist` jako `.env` i wypełnij je odpowiednimi wartościami
3. Jeśli nie masz bazy danych PostGiS możesz ją zainstalować za pomocą dockera używając komendy `docker docker run --network host --name some-postgis -e POSTGRES_PASSWORD=<password> postgis/postgi`
4. Stwórz bazę danych `CREATE DATABASE digitallurker;`. Jeśli masz bazę danych w dockerze to możesz tam wejść za pomocą `docker exec -ti d127b44ebfd0 psql -U postgres`.
5. Zbuduj image projektu DigitalLurker za pomocą `docker build --network host . -t digital-lurker `.
6. Uruchom projekt komendą `docker run --network host digital-lurker --port 8000:8000 `.
7. Projekt jest gotowy do użytku.

#### Dokumentacja kodu
Aby dostać się do wszystkich możliwy route'ów w projekcie należy ustawić zmienną środowiskową (albo wartość w pliku `.env`) DEBUG='TRUE' oraz wejść na stronę projektu który uruchomiłeś z linkiem `/swagger/`. **Nie wszystkie tam dane są w 100% poprawne.**

