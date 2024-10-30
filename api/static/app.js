const button = document.querySelector("#submitButton");
const form = document.querySelector(".form");

button.addEventListener("click", (e) => {
    buttonEventListner(e, button);
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
        } else {
            const errorData = await response.json();
            console.error("Error:", errorData.message);
        }
    } catch (error) {
        console.error("An error occurred while submitting the form:", error);
    }
}

function replaceWithLoader(element) {
    const spinnerElement = () => {
        const spinner = document.createElement("div");
        spinner.classList.add("spinner-container");
        spinner.id = "spinner";

        const loader = document.createElement("span");
        loader.classList.add("loader");
        spinner.appendChild(loader);

        return spinner;
    };

    const copy = getElementCopy(element, buttonEventListner);
    element.replaceWith(spinnerElement());
    return () => {
        document.querySelector("#spinner").replaceWith(copy);
    };
}

function getElementCopy(element, eventListner) {
    const copy = element.cloneNode(true);
    copy.addEventListener("click", (e) => {
        eventListner(e, copy);
    });

    return copy;
}

function buttonEventListner(e, element) {
    e.preventDefault();
    e.stopPropagation();

    const callback = replaceWithLoader(element);
    submitForm().finally(() => callback());
}
