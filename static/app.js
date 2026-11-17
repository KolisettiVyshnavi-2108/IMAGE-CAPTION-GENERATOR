const form = document.querySelector("#caption-form");
const input = document.querySelector("#image-input");
const dropZone = document.querySelector("#drop-zone");
const uploadEmpty = document.querySelector("#upload-empty");
const previewWrap = document.querySelector("#preview-wrap");
const previewImage = document.querySelector("#image-preview");
const fileName = document.querySelector("#file-name");
const browseButton = document.querySelector("#browse-files");
const replaceButton = document.querySelector("#replace-image");
const removeButton = document.querySelector("#remove-image");
const generateButton = document.querySelector("#generate-button");
const regenerateButton = document.querySelector("#regenerate-button");
const formHint = document.querySelector("#form-hint");
const resultPlaceholder = document.querySelector("#result-placeholder");
const resultContent = document.querySelector("#result-content");
const captionText = document.querySelector("#caption-text");
const errorMessage = document.querySelector("#error-message");
const copyButton = document.querySelector("#copy-button");
const themeToggle = document.querySelector("#theme-toggle");

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
let selectedFile = null;
let previewUrl = null;
let isGenerating = false;

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
  formHint.textContent = "Check your image and try again.";
  formHint.classList.add("hint-error");
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
  formHint.textContent = "A good caption starts with a good moment.";
  formHint.classList.remove("hint-error");
}

function setSelectedFile(file) {
  clearError();
  if (!file) return;
  if (!ACCEPTED_TYPES.includes(file.type)) {
    showError("Choose a JPEG, PNG, or WebP image.");
    return;
  }
  if (file.size > MAX_FILE_SIZE) {
    showError("This image is larger than 10 MB. Choose a smaller file.");
    return;
  }

  if (previewUrl) URL.revokeObjectURL(previewUrl);
  selectedFile = file;
  previewUrl = URL.createObjectURL(file);
  previewImage.src = previewUrl;
  fileName.textContent = file.name;
  uploadEmpty.hidden = true;
  previewWrap.hidden = false;
  generateButton.disabled = false;
  resultPlaceholder.hidden = true;
  resultContent.hidden = true;
}

function resetImage() {
  selectedFile = null;
  input.value = "";
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
  previewImage.removeAttribute("src");
  previewWrap.hidden = true;
  uploadEmpty.hidden = false;
  generateButton.disabled = true;
  resultContent.hidden = true;
  resultPlaceholder.hidden = false;
  clearError();
}

function setGenerating(active) {
  isGenerating = active;
  generateButton.disabled = active || !selectedFile;
  regenerateButton.disabled = active;
  generateButton.classList.toggle("is-loading", active);
  generateButton.querySelector("span").textContent = active ? "Finding the words…" : "Generate caption";
  if (active) {
    resultPlaceholder.hidden = false;
    resultPlaceholder.querySelector(".result-title").textContent = "Looking closely at your image…";
    resultPlaceholder.querySelector(".result-description").textContent = "This can take a little longer the first time while the AI model loads.";
    resultPlaceholder.classList.add("is-loading");
    resultContent.hidden = true;
    clearError();
  } else {
    resultPlaceholder.classList.remove("is-loading");
    resultPlaceholder.querySelector(".result-title").textContent = "Your caption will appear here";
    resultPlaceholder.querySelector(".result-description").textContent = "A thoughtful description, made in moments.";
  }
}

async function generateCaption(event) {
  if (event) event.preventDefault();
  if (!selectedFile || isGenerating) return;

  setGenerating(true);
  try {
    const body = new FormData();
    body.append("image", selectedFile);
    const response = await fetch("/api/caption", { method: "POST", body });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Caption generation failed. Please try again.");
    captionText.textContent = payload.caption;
    resultPlaceholder.hidden = true;
    resultContent.hidden = false;
  } catch (error) {
    resultPlaceholder.hidden = true;
    showError(error.message || "Could not reach the caption service. Check your connection and try again.");
  } finally {
    setGenerating(false);
  }
}

dropZone.addEventListener("click", (event) => {
  if (event.target.closest("button")) return;
  input.click();
});
browseButton.addEventListener("click", () => input.click());
replaceButton.addEventListener("click", () => input.click());
input.addEventListener("change", () => {
  setSelectedFile(input.files[0]);
  input.value = "";
});
["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("is-dragging");
  });
});
["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("is-dragging");
  });
});
dropZone.addEventListener("drop", (event) => setSelectedFile(event.dataTransfer.files[0]));
removeButton.addEventListener("click", (event) => {
  event.stopPropagation();
  resetImage();
});
form.addEventListener("submit", generateCaption);
regenerateButton.addEventListener("click", generateCaption);

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(captionText.textContent);
    copyButton.querySelector("span").textContent = "Copied!";
    window.setTimeout(() => {
      copyButton.querySelector("span").textContent = "Copy caption";
    }, 1800);
  } catch (_error) {
    showError("Your browser could not copy the caption. Select and copy the text instead.");
  }
});

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem("frame-theme", theme);
  const nextTheme = theme === "dark" ? "light" : "dark";
  themeToggle.setAttribute("aria-label", `Switch to ${nextTheme} mode`);
}

themeToggle.addEventListener("click", () => {
  setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
});
setTheme(localStorage.getItem("frame-theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
