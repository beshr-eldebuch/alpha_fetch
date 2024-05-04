from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)
def test_get_stock_data_success():
    # Mock the dependencies: Database session and StockService
    with patch('app.routers.get_db'
            , return_value=MagicMock(spec=Session)) as mock_db:
        with patch('app.routers.StockService') as mock_service:
            # Setup mock return value for the service method
            mock_service_instance = mock_service.return_value
            mock_service_instance.get_processed_stock_data.return_value = {
                "symbol": "AAPL",
                "currency": "USD",
                "daily_close": {"2020-01-01": 150.0},
                "last_refreshed": "2020-01-01"
            }

            # Call the endpoint
            response = client.get("/stocks", params={
                "symbol": "AAPL",
                "start_date": "2020-01-01",
                "end_date": "2020-01-01",
                "currency": "USD"
            })

            # Assertions
            assert response.status_code == 200
            assert response.json() == {
                "symbol": "AAPL",
                "currency": "USD",
                "daily_close": {"2020-01-01": 150.0},
                "last_refreshed": "2020-01-01"
            }

def test_get_stock_data_not_found():
    with patch('app.routers.get_db', return_value=MagicMock(spec=Session)) as mock_db:
        with patch('app.routers.StockService') as mock_service:
            mock_service_instance = mock_service.return_value
            mock_service_instance.get_processed_stock_data.side_effect = ValueError("No data available")

            response = client.get("/stocks", params={
                "symbol": "AAPL",
                "start_date": "2020-01-01",
                "end_date": "2020-01-01",
                "currency": "USD"
            })

            assert response.status_code == 404
            assert response.json() == {"detail": "No data available"}
