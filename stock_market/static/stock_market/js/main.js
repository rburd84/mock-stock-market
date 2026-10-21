document.addEventListener('DOMContentLoaded', () => {
    // Initialize bootstrap modal
    const modalElement = document.getElementById("tradeExecutionModal");
    const tradeModal = new bootstrap.Modal(modalElement);
    const formContainer = document.getElementById("modalFormContainer");
    const formInputs = document.querySelectorAll("form input");

    const loadingHtml = formContainer.innerHTML;


    formInputs.forEach(input => {
        input.classList.add("form-control");
    });


    document.querySelectorAll(".open-trade-modal").forEach(button => {
        button.addEventListener("click", (evt) => {
            formContainer.innerHTML = loadingHtml;

            const ticker = evt.currentTarget.getAttribute("data-ticker");
            const tradeType = evt.currentTarget.getAttribute("data-trade-type");

            const targetUrl = `/trade/get-form/${ticker}/?type=${tradeType}`;

            tradeModal.show()

            fetch(targetUrl).then(response => {
                if (!response.ok) {
                    throw new Error("Network query was unsuccessful");
                }
                return response.text()
            })
                .then(htmlSnippet => {
                    formContainer.innerHTML = htmlSnippet;
                })
                .catch(error => {
                    formContainer.innerHTML = `
                        <div class="alert alert-danger mb-0" role="alert">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            Failed to configure order. Please try again.
                        </div>`;
                    console.log("Fetch Error: ", error);
                });
        })
    });


})

console.log("Hello from javascript");