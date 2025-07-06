document.addEventListener("DOMContentLoaded", function () {
    // Animation Logic
    const elements = document.querySelectorAll(".animate");

    function handleScroll() {
        elements.forEach((el) => {
            const rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight * 0.8) {
                el.classList.add("active");
            }
        });
    }

    window.addEventListener("scroll", handleScroll);
    handleScroll(); // Run once to check initial visibility

    // OTP Handling Logic
    const form = document.querySelector(".join-form");
    const successPopup = document.getElementById("successPopup");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const name = document.querySelector('input[placeholder="Full Name"]').value;
        const email = document.querySelector('input[placeholder="Email Address"]').value;

        try {
            const response = await fetch("http://localhost:5000/api/auth/send-otp", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email }),
            });

            const result = await response.json();
            alert(result.message);

            if (response.ok) {
                const otp = prompt("Enter the OTP sent to your email:");

                if (otp) {
                    const verifyResponse = await fetch("http://localhost:5000/api/auth/verify-otp", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email, otp }),
                    });

                    const verifyResult = await verifyResponse.json();
                    alert(verifyResult.message);

                    if (verifyResponse.ok) {
                        successPopup.style.display = "flex"; // Show success popup
                    }
                }
            }
        } catch (error) {
            alert("Error sending OTP");
        }
    });

    // Close popup function
    document.getElementById("successPopup").querySelector("button").addEventListener("click", function () {
        successPopup.style.display = "none";
    });
});
