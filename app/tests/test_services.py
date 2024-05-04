import pytest
from unittest.mock import MagicMock
from datetime import datetime
from app.services import StockDBRepository


@pytest.fixture
def mock_db_session():
    """ Creates a mock SQLAlchemy session """
    return MagicMock()

@pytest.fixture
def db_repository(mock_db_session):
    """ Fixture for database repository """
    return StockDBRepository(db=mock_db_session)

def test_db_repository_returns_data_when_present(mock_db_session, db_repository):
    # Arrange
    mock_query = mock_db_session.query.return_value.join.return_value.filter.return_value.order_by.return_value
    expected_date = datetime.now().date()
    mock_query.all.return_value = [
        ('AAPL', 'USD', expected_date, 150.0, datetime.now())
    ]

    # Act
    result = db_repository.get_stock_data('AAPL', '2022-01-01', '2022-01-02')

    # Assert
    assert result is not None
    assert result.symbol == 'AAPL'
    assert result.daily_close == {str(expected_date): 150.0}

def test_db_repository_returns_none_when_no_data(mock_db_session, db_repository):
    # Arrange
    mock_db_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []

    # Act
    result = db_repository.get_stock_data('AAPL', '2022-01-01', '2022-01-02')

    # Assert
    assert result is None