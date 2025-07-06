document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded!"); // Debugging step

    const elements = document.querySelectorAll(".slide-up");
    elements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = "1";
            el.style.transform = "translateY(0)";
        }, index * 200);
    });

    // Select the form and popup
    const joinForm = document.getElementById("joinForm");
    const successPopup = document.getElementById("successPopup");

    if (!joinForm) {
        console.error("⚠️ Form element (joinForm) not found!");
        return;
    }
    if (!successPopup) {
        console.error("⚠️ Popup element (successPopup) not found!");
        return;
    }

    // Add event listener for form submission
    joinForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission
        console.log("✅ Form submitted!"); // Debugging step
        successPopup.style.display = "flex"; // Show popup
    });
});

// Function to close the popup
function closePopup() {
    const successPopup = document.getElementById("successPopup");
    if (successPopup) {
        successPopup.style.display = "none"; // Hide popup
    }
}
