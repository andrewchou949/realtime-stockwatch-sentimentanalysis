def test_health_check(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "stock-watch-api"


def test_watchlist_crud_and_metrics(client):
    client.provider.seed("AAPL", 100.0)

    create_response = client.post(
        "/watchlist",
        json={"symbol": "aapl", "threshold_pct": 2.0},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["symbol"] == "AAPL"
    assert created["baseline_price"] == 100.0
    assert created["last_price"] == 100.0
    assert created["pct_change_from_baseline"] == 0.0

    list_response = client.get("/watchlist")
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 1
    assert items[0]["symbol"] == "AAPL"

    delete_response = client.delete("/watchlist/AAPL")
    assert delete_response.status_code == 204

    empty_response = client.get("/watchlist")
    assert empty_response.json() == []


def test_duplicate_and_invalid_watchlist_input(client):
    client.provider.seed("MSFT", 250.0)
    first = client.post("/watchlist", json={"symbol": "MSFT", "threshold_pct": 2.5})
    duplicate = client.post("/watchlist", json={"symbol": "MSFT", "threshold_pct": 2.5})
    invalid = client.post("/watchlist", json={"symbol": "  ", "threshold_pct": -1})

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert invalid.status_code == 422


def test_get_price_snapshot(client):
    client.provider.seed("NVDA", 880.5)

    response = client.get("/prices/NVDA")

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "NVDA"
    assert payload["price"] == 880.5


def test_provider_error_returns_clear_api_error(client):
    response = client.get("/prices/FAIL")

    assert response.status_code == 502
    assert "Unable to fetch price" in response.json()["detail"]


def test_refresh_creates_up_alert_once_threshold_is_crossed(client):
    client.provider.seed("TSLA", 100.0, 103.0, 104.0)
    create_response = client.post("/watchlist", json={"symbol": "TSLA", "threshold_pct": 2.0})
    assert create_response.status_code == 201

    first_refresh = client.post("/refresh")
    assert first_refresh.status_code == 200
    assert first_refresh.json()["alerts_created"] == 1

    second_refresh = client.post("/refresh")
    assert second_refresh.status_code == 200
    assert second_refresh.json()["alerts_created"] == 0

    alerts_response = client.get("/alerts?limit=50")
    alerts = alerts_response.json()
    assert len(alerts) == 1
    assert alerts[0]["symbol"] == "TSLA"
    assert alerts[0]["direction"] == "UP"
    assert alerts[0]["pct_change"] == 3.0


def test_refresh_creates_down_alert_when_threshold_is_crossed(client):
    client.provider.seed("AMD", 100.0, 97.5)
    client.post("/watchlist", json={"symbol": "AMD", "threshold_pct": 2.0})

    refresh_response = client.post("/refresh")
    assert refresh_response.status_code == 200
    assert refresh_response.json()["alerts_created"] == 1

    alerts = client.get("/alerts").json()
    assert alerts[0]["direction"] == "DOWN"
    assert alerts[0]["pct_change"] == -2.5


def test_refresh_updates_last_known_fields(client):
    client.provider.seed("META", 100.0, 101.2)
    client.post("/watchlist", json={"symbol": "META", "threshold_pct": 5.0})

    refresh_response = client.post("/refresh")
    assert refresh_response.status_code == 200

    item = client.get("/watchlist").json()[0]
    assert item["last_price"] == 101.2
    assert item["pct_change_from_baseline"] == 1.2


def test_root_returns_api_message(client):
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "stock-watch-api"
    assert "v0/frontend" in payload["frontend"]
    assert payload["dev_tools_enabled"] is True


def test_dev_force_breach_creates_demo_alert(client):
    client.provider.seed("TSLA", 200.0)
    client.post("/watchlist", json={"symbol": "TSLA", "threshold_pct": 2.0})

    response = client.post(
        "/dev/force-breach",
        json={"symbol": "TSLA", "direction": "DOWN", "pct_change": 6.5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Forced a DOWN breach for TSLA" in payload["message"]
    assert payload["alert_count"] == 1

    item = client.get("/watchlist").json()[0]
    assert item["last_price"] == 187.0
    assert item["pct_change_from_baseline"] == -6.5

    alerts = client.get("/alerts").json()
    assert len(alerts) == 1
    assert alerts[0]["direction"] == "DOWN"


def test_dev_reset_clears_demo_state(client):
    client.provider.seed("AAPL", 100.0)
    client.post("/watchlist", json={"symbol": "AAPL", "threshold_pct": 3.0})
    client.post("/dev/force-breach", json={"symbol": "AAPL", "direction": "UP", "pct_change": 7.0})

    response = client.post("/dev/reset", json={"scope": "all"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["watchlist_count"] == 0
    assert payload["alert_count"] == 0
    assert client.get("/watchlist").json() == []
    assert client.get("/alerts").json() == []
