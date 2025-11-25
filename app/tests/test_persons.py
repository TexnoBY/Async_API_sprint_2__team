from fastapi import status
from fastapi.testclient import TestClient


class TestPersonEndpoints:
    """Тесты для API endpoint'ов персон"""

    def test_person_details_success(self, client: TestClient, setup_test_data):
        """Тест успешного получения детальной информации о персоне"""
        person_uuid = setup_test_data["person_uuid"]
        response = client.get(f"/api/v1/persons/{person_uuid}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "films" in data
        assert data["id"] == person_uuid
        assert data["name"] == "Test Actor"

    def test_person_details_not_found(self, client: TestClient):
        """Тест получения ошибки 404 при отсутствии персоны"""
        response = client.get("/api/v1/persons/non-existent-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "person not found"

    def test_person_search_success(self, client: TestClient, setup_test_data):
        """Тест успешного поиска персон"""
        response = client.get("/api/v1/persons/search?query=Test")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if data:  # если поиск что-то нашел
            person = data[0]
            assert "id" in person
            assert "name" in person
            assert "films" in person

    def test_person_search_with_pagination(self, client: TestClient):
        """Тест поиска персон с пагинацией"""
        response = client.get("/api/v1/persons/search?query=Test&page_size=1&page_number=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 1

    def test_person_search_not_found(self, client: TestClient):
        """Тест поиска персон с пустым результатом"""
        response = client.get("/api/v1/persons/search?query=xyz123nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "persons not found"

    def test_person_search_empty_query(self, client: TestClient):
        """Тест поиска с пустым запросом"""
        response = client.get("/api/v1/persons/search?query=")

        # Должен вернуть 404 так как пустой запрос не найдет персоны
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_person_films_success(self, client: TestClient, setup_test_data):
        """Тест успешного получения фильмов персоны"""
        person_uuid = setup_test_data["person_uuid"]
        response = client.get(f"/api/v1/persons/{person_uuid}/film")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if data:  # если фильмы есть
            film = data[0]
            assert "id" in film
            assert "title" in film
            assert "imdb_rating" in film

    def test_person_films_not_found(self, client: TestClient):
        """Тест получения фильмов для несуществующей персоны"""
        response = client.get("/api/v1/persons/non-existent-id/film")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "films not found"

    def test_person_details_invalid_id_format(self, client: TestClient):
        """Тест получения персоны с невалидным ID"""
        response = client.get("/api/v1/persons/invalid-id-format")

        # Может вернуть 404 или ошибку валидации
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_person_search_invalid_page_size(self, client: TestClient):
        """Тест поиска с невалидным размером страницы"""
        response = client.get("/api/v1/persons/search?query=test&page_size=0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_person_search_invalid_page_number(self, client: TestClient):
        """Тест поиска с невалидным номером страницы"""
        response = client.get("/api/v1/persons/search?query=test&page_number=-1")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_person_films_invalid_id_format(self, client: TestClient):
        """Тест получения фильмов персоны с невалидным ID"""
        response = client.get("/api/v1/persons/invalid-id-format/film")

        # Может вернуть 404 или ошибку валидации
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]
