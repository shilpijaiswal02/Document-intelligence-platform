const uploadForm = document.getElementById("uploadForm");
const message = document.getElementById("message");
const tableBody = document.getElementById("documentsTableBody");


uploadForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const fileInput = document.getElementById("file");
    const documentType = document.getElementById("documentType");

    if (!fileInput.files.length) {
        message.textContent = "Please select a file.";
        return;
    }

    const formData = new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );

    formData.append(
        "document_type",
        documentType.value
    );

    message.textContent = "Processing document...";

    try {

        const response = await fetch(
            "/api/v1/documents/process",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail?.message ||
                "Document processing failed."
            );
        }

        message.textContent =
            "Document processed successfully.";

        uploadForm.reset();

        loadDocuments();

    } catch (error) {

        message.textContent =
            error.message;

    }

});


async function loadDocuments() {

    try {

        const response = await fetch(
            "/api/v1/documents"
        );

        const documents = await response.json();

        tableBody.innerHTML = "";

        documents.forEach(doc => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${doc.document_name}</td>

                <td>${doc.document_type}</td>

                <td>${doc.processing_status}</td>

                <td>${doc.created_at}</td>

                <td>
                    <a href="/document/${encodeURIComponent(
                        doc.document_name
                    )}">
                        Open
                    </a>
                </td>
            `;

            tableBody.appendChild(row);

        });

    } catch (error) {

        console.error(
            "Failed to load documents:",
            error
        );

    }
}


loadDocuments();