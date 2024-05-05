# alpha_fetch
A simple python script to fetch the alpha vantage data for a given stock symbol.

## How to Run
1. Clone the repository
2. Create .env file and Setup the environment variables (example below)
```bash
ALPHA_API_KEY= # Your alpha vantage api key
PORT=8000
HOST=0.0.0.0
REDIS_URL=redis://redis:6379/0
DATABASE_URL=sqlite:////data/test.db
```
2. Run the following commands in the terminal
```bash
docker-compose build
docker-compose up
```
3. Open the browser and go to `http://localhost:8000/docs` to see the swagger documentation. You can use the swagger documentation to test the api.
4. Or call the api using the following curl command
```bash
curl -X 'GET' \
  'http://localhost:8000/stocks?symbol=AAPL&currency=EUR&start_date=2024-01-01&end_date=2024-05-05' \
  -H 'accept: application/json'
```
5. You can also run the tests using the following command
```bash
docker-compose exec web pytest
```