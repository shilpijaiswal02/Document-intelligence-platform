from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_unsupported_file_type():
    response = client.post(
        "/api/v1/documents/process",
        files={
            "file": (
                "test.txt",
                b"hello",
                "text/plain"
            )
        },
        data={
            "document_type": "invoice"
        }
    )

    assert response.status_code == 400

    body = response.json()

    assert body["detail"]["error_code"] == (
        "UNSUPPORTED_FILE_TYPE"
    )


def test_invalid_document_type():
    response = client.post(
        "/api/v1/documents/process",
        files={
            "file": (
                "test.pdf",
                b"fake pdf content",
                "application/pdf"
            )
        },
        data={
            "document_type": "invalid_type"
        }
    )

    assert response.status_code == 400

    body = response.json()

    assert body["detail"]["error_code"] == (
        "INVALID_DOCUMENT_TYPE"
    )


def test_get_all_documents():
    response = client.get(
        "/api/v1/documents"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_process_document_success(monkeypatch):
    from backend.app.api.routes import documents

    class FakeDocument:
        document_name = "test.pdf"
        document_type = "invoice"
        processing_status = "PASS"

        file_validation = (
            '{"status": "PASS", '
            '"is_supported": true, '
            '"is_readable": true}'
        )

        extracted_data = (
            '{"header": {"invoice_number": "INV-001"}, '
            '"line_items": [], '
            '"totals": {}}'
        )

        validation = (
            '{"status": "PASS", '
            '"checks": []}'
        )

        processing_metadata = (
            '{"processing_time_seconds": 0.1}'
        )

    def fake_process_document(
        db,
        file_path,
        document_name,
        document_type
    ):
        return FakeDocument()

    monkeypatch.setattr(
        documents,
        "process_document",
        fake_process_document
    )

    response = client.post(
        "/api/v1/documents/process",
        files={
            "file": (
                "test.pdf",
                b"fake pdf content",
                "application/pdf"
            )
        },
        data={
            "document_type": "invoice"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert body["document_name"] == "test.pdf"
    assert body["document_type"] == "invoice"
    assert body["processing_status"] == "PASS"

    assert "file_validation" in body
    assert "extracted_data" in body
    assert "validation" in body
    assert "processing_metadata" in body