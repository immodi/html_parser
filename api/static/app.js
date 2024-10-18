const button = document.querySelector("#submitButton");
const form = document.querySelector(".form");

button.addEventListener("click", () => {
    const newDiv = document.createElement("div");
    newDiv.classList.add("replaced-div");

    newDiv.innerHTML = `
        <div class="spinner-container">
            <span class="loader"></span>
        </div>
    `;

    button.replaceWith(newDiv);
    form.submit();
});
