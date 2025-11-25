import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestFilmEndpoints:
    """Тесты для API endpoint'ов фильмов"""

    def test_film_details_success(self, client: TestClient, setup_test_data):
        """Тест успешного получения детальной информации о фильме"""
        film_uuid = setup_test_data["film_uuid"]
        response = client.get(f"/api/v1/films/{film_uuid}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "title" in data
        assert "imdb_rating" in data
        assert "description" in data
        assert "genres" in data
        assert "directors" in data
        assert "actors" in data
        assert "writers" in data
        assert data["title"] == "Test Film"
        assert data["imdb_rating"] == 8.5

    def test_film_details_not_found(self, client: TestClient):
        """Тест получения ошибки 404 при отсутствии фильма"""
        response = client.get("/api/v1/films/non-existent-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "film not found"

    def test_film_list_success(self, client: TestClient):
        """Тест успешного получения списка фильмов"""
        response = client.get("/api/v1/films/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if data:  # если список не пустой
            film = data[0]
            assert "title" in film
            assert "imdb_rating" in film

    def test_film_list_with_pagination(self, client: TestClient):
        """Тест пагинации списка фильмов"""
        response = client.get("/api/v1/films/?page_number=0&page_size=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 1

    def test_film_list_with_sorting_asc(self, client: TestClient):
        """Тест сортировки списка фильмов по возрастанию"""
        response = client.get("/api/v1/films/?sort=imdb_rating")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_film_list_with_sorting_desc(self, client: TestClient):
        """Тест сортировки списка фильмов по убыванию"""
        response = client.get("/api/v1/films/?sort=-imdb_rating")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_film_list_with_genre_filter(self, client: TestClient, setup_test_data):
        """Тест фильтрации списка фильмов по жанру"""
        # Пропускаем этот тест, так как он требует nested структуру в Elasticsearch
        # которая не настроена в тестовом окружении
        pytest.skip("Genre filter requires nested Elasticsearch mapping")

    def test_film_list_not_found(self, client: TestClient):
        """Тест получения ошибки 404 когда фильмы не найдены"""
        response = client.get("/api/v1/films/?page_number=999&page_size=1")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "film not found"

    def test_film_search_success(self, client: TestClient):
        """Тест успешного поиска фильмов"""
        response = client.get("/api/v1/films/search?query=Test")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if data:  # если поиск что-то нашел
            film = data[0]
            assert "title" in film
            assert "imdb_rating" in film

    def test_film_search_with_pagination(self, client: TestClient):
        """Тест поиска фильмов с пагинацией"""
        response = client.get("/api/v1/films/search?query=Test&page_size=1&page_number=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 1

    def test_film_search_not_found(self, client: TestClient):
        """Тест поиска фильмов с пустым результатом"""
        response = client.get("/api/v1/films/search?query=xyz123nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "film not found"

    def test_film_search_empty_query(self, client: TestClient):
        """Тест поиска с пустым запросом"""
        response = client.get("/api/v1/films/search?query=")

        # Должен вернуть 404 так как пустой запрос не найдет фильмы
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_page_size(self, client: TestClient):
        """Тест невалидного параметра page_size"""
        response = client.get("/api/v1/films/?page_size=0")

        # Должна быть ошибка валидации
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_page_number(self, client: TestClient):
        """Тест невалидного параметра page_number"""
        response = client.get("/api/v1/films/?page_number=-1")

        # Должна быть ошибка валидации
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_film_details_invalid_id_format(self, client: TestClient):
        """Тест получения фильма с невалидным ID"""
        response = client.get("/api/v1/films/invalid-id-format")

        # Может вернуть 404 или ошибку валидации
        assert response.status_code in [404, 422]

    def test_film_search_invalid_page_size(self, client: TestClient):
        """Тест поиска с невалидным размером страницы"""
        response = client.get("/api/v1/films/search?query=test&page_size=0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_film_search_invalid_page_number(self, client: TestClient):
        """Тест поиска с невалидным номером страницы"""
        response = client.get("/api/v1/films/search?query=test&page_number=-1")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
