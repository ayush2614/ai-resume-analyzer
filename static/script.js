const resumeInput = document.getElementById("resumeInput");
const fileName = document.getElementById("fileName");

if (resumeInput) {
  resumeInput.addEventListener("change", function () {
    if (this.files.length > 0) {
      fileName.textContent = "📄 " + this.files[0].name;
    } else {
      fileName.textContent = "📄 Choose Resume PDF";
    }
  });
}