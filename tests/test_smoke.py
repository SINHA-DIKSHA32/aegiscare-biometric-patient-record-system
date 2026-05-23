import importlib


def test_login_dashboard_and_ledger(tmp_path, monkeypatch):
    app_module = importlib.import_module("app")
    monkeypatch.setattr(app_module, "INSTANCE_DIR", tmp_path)
    monkeypatch.setattr(app_module, "DB_PATH", tmp_path / "patients.db")
    monkeypatch.setattr(app_module, "KEY_PATH", tmp_path / "biometric.key")
    monkeypatch.setattr(app_module, "BIOMETRIC_DIR", tmp_path / "encrypted_biometrics")

    app_module.app.config.update(TESTING=True)

    with app_module.app.test_client() as client:
        response = client.post(
            "/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Smart Dashboard" in response.data

        ledger = app_module.verify_ledger()
        assert ledger["valid"] is True
        assert ledger["total_blocks"] >= 1
