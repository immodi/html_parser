const button = document.querySelector("#submitButton");
const form = document.querySelector(".form");
const ButtonLoader = Object.freeze({
    BUTTON: `
        <button type="submit" id="submitButton" class="submit-button">
            Submit
        </button>
    `,
    LOADING: `
        <div class="spinner-container">
            <span class="loader"></span>
        </div>
    `,
});

button.addEventListener("click", (e) => {
    e.preventDefault();
    replaceButton(ButtonLoader.LOADING);

    submitForm()
        .then(() => replaceButton(ButtonLoader.BUTTON))
        .finally(() => replaceButton(ButtonLoader.BUTTON));
});

async function submitForm() {
    const formData = new FormData(form);

    try {
        const response = await fetch("/", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const blob = await response.blob(); // Since the response is a file download
            const filename = response.headers
                .get("Content-Disposition")
                .split("filename=")[1]
                .replace(/['"]/g, "");

            // Create a link element to download the file
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();

            // Cleanup the DOM
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);

            replaceButton(ButtonLoader.BUTTON);
        } else {
            const errorData = await response.json();
            console.error("Error:", errorData.message);
        }
    } catch (error) {
        console.error("An error occurred while submitting the form:", error);
    }
}

function replaceButton(option) {
    const newDiv = document.createElement("div");
    newDiv.id = "submitButton";

    newDiv.innerHTML = option;

    document.querySelector("#submitButton").replaceWith(newDiv);
}
