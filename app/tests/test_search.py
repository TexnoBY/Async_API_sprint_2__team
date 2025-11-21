import pytest
from fastapi.testclient import TestClient


class TestSearchEndpoints:
    """Тесты для универсального search endpoint"""

    def test_universal_search_all_success(self, client: TestClient):
        """Тест успешного универсального поиска по всем сущностям"""
        response = client.get("/api/v1/search?query=Test")
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["total"], int)
        
        if data["results"]:  # если поиск что-то нашел
            result = data["results"][0]
            assert "type" in result
            assert "data" in result
            assert result["type"] in ["film", "person", "genre"]

    def test_universal_search_films_only(self, client: TestClient):
        """Тест поиска только по фильмам"""
        response = client.get("/api/v1/search?query=Test&search_type=films")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["results"], list)
        
        # Все результаты должны быть типа film
        for result in data["results"]:
            assert result["type"] == "film"

    def test_universal_search_persons_only(self, client: TestClient):
        """Тест поиска только по персонам"""
        response = client.get("/api/v1/search?query=Test&search_type=persons")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["results"], list)
        
        # Все результаты должны быть типа person
        for result in data["results"]:
            assert result["type"] == "person"

    def test_universal_search_genres_only(self, client: TestClient):
        """Тест поиска только по жанрам"""
        response = client.get("/api/v1/search?query=Test&search_type=genres")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["results"], list)
        
        # Все результаты должны быть типа genre
        for result in data["results"]:
            assert result["type"] == "genre"

    def test_universal_search_with_pagination(self, client: TestClient):
        """Тест универсального поиска с пагинацией"""
        response = client.get("/api/v1/search?query=Test&page_size=1&page_number=0")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["results"], list)
        # Пагинация применяется к каждому типу отдельно, поэтому может быть до 3 результатов
        assert len(data["results"]) <= 3

    def test_universal_search_not_found(self, client: TestClient):
        """Тест универсального поиска с пустым результатом"""
        response = client.get("/api/v1/search?query=xyz123nonexistent")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "nothing found"

    def test_universal_search_empty_query(self, client: TestClient):
        """Тест универсального поиска с пустым запросом"""
        response = client.get("/api/v1/search?query=")
        
        # Должен вернуть 404 так как пустой запрос не найдет ничего
        assert response.status_code == 404

    def test_universal_search_invalid_page_size(self, client: TestClient):
        """Тест универсального поиска с невалидным размером страницы"""
        response = client.get("/api/v1/search?query=test&page_size=0")
        
        assert response.status_code == 422

    def test_universal_search_invalid_page_number(self, client: TestClient):
        """Тест универсального поиска с невалидным номером страницы"""
        response = client.get("/api/v1/search?query=test&page_number=-1")
        
        assert response.status_code == 422

    def test_universal_search_invalid_search_type(self, client: TestClient):
        """Тест универсального поиска с невалидным типом поиска"""
        response = client.get("/api/v1/search?query=test&search_type=invalid")
        
        # Должен вернуть 404 так как тип поиска не поддерживается
        assert response.status_code == 404

    def test_universal_search_total_count(self, client: TestClient):
        """Тест корректности подсчета общего количества результатов"""
        response = client.get("/api/v1/search?query=Test&search_type=all")
        
        if response.status_code == 200:
            data = response.json()
            assert data["total"] == len(data["results"])

    def test_universal_search_data_structure(self, client: TestClient):
        """Тест структуры данных в результатах поиска"""
        response = client.get("/api/v1/search?query=Test&search_type=all")
        
        if response.status_code == 200:
            data = response.json()
            for result in data["results"]:
                assert "type" in result
                assert "data" in result
                
                # Проверяем структуру данных в зависимости от типа
                if result["type"] == "film":
                    assert "title" in result["data"]
                    assert "imdb_rating" in result["data"]
                elif result["type"] == "person":
                    assert "full_name" in result["data"]
                elif result["type"] == "genre":
                    assert "name" in result["data"]