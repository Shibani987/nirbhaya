const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
  container.classList.add("sign-up-mode"); 
});

sign_in_btn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode"); 
});

const togglePasswordBtn = document.getElementById("eye-icon");
togglePasswordBtn.addEventListener("click", togglePassword);
function togglePassword() {
  const passwordField = document.getElementById('password');
  const eyeIcon = document.getElementById('eyeIcon');
  
  if (passwordField.type === 'password') {
      passwordField.type = 'text';
      eyeIcon.textContent = '👁️'; 
  } else {
      passwordField.type = 'password';
      eyeIcon.textContent = '👁️‍🗨️';
  }
}
