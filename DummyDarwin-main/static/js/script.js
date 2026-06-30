/**
 * AI Recruitment Portal — Client-side interactions
 * Handles file uploads, drag-and-drop, delete confirmations, and flash dismissal.
 */

document.addEventListener("DOMContentLoaded", function () {
    initFlashMessages();
    initDeleteConfirmations();
    initFileUploads();
});


/**
 * Auto-dismiss flash messages and wire close buttons.
 */
function initFlashMessages() {
    const flashes = document.querySelectorAll(".flash");

    flashes.forEach(function (flash) {
        const closeBtn = flash.querySelector(".flash-close");

        if (closeBtn) {
            closeBtn.addEventListener("click", function () {
                dismissFlash(flash);
            });
        }

        // Auto-dismiss success messages after 5 seconds
        if (flash.classList.contains("flash-success")) {
            setTimeout(function () {
                dismissFlash(flash);
            }, 5000);
        }
    });
}


/**
 * Animate and remove a flash message element.
 */
function dismissFlash(flash) {
    flash.style.transition = "opacity 0.3s ease, transform 0.3s ease";
    flash.style.opacity = "0";
    flash.style.transform = "translateY(-8px)";

    setTimeout(function () {
        flash.remove();

        const container = document.querySelector(".flash-container");
        if (container && container.children.length === 0) {
            container.remove();
        }
    }, 300);
}


/**
 * Show a confirmation dialog before deleting a document.
 */
function initDeleteConfirmations() {
    const deleteForms = document.querySelectorAll(".delete-form");

    deleteForms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const button = form.querySelector("[data-filename]");
            const filename = button ? button.getAttribute("data-filename") : "this document";

            const confirmed = confirm(
                "Are you sure you want to delete \"" + filename + "\"?\n\nThis action cannot be undone."
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}


/**
 * Initialize drag-and-drop and auto-submit for both upload forms.
 */
function initFileUploads() {
    const uploadForms = document.querySelectorAll(".upload-form");

    uploadForms.forEach(function (form) {
        const fileInput = form.querySelector('input[type="file"]');
        const uploadArea = form.querySelector(".upload-area");

        if (!fileInput || !uploadArea) return;

        // Update label text when a file is selected and auto-submit
        fileInput.addEventListener("change", function () {
            if (fileInput.files.length > 0) {
                updateUploadLabel(uploadArea, fileInput.files[0].name);
                form.submit();
            }
        });

        // Drag-and-drop handlers
        uploadArea.addEventListener("dragover", function (event) {
            event.preventDefault();
            uploadArea.classList.add("drag-over");
        });

        uploadArea.addEventListener("dragleave", function () {
            uploadArea.classList.remove("drag-over");
        });

        uploadArea.addEventListener("drop", function (event) {
            event.preventDefault();
            uploadArea.classList.remove("drag-over");

            const files = event.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateUploadLabel(uploadArea, files[0].name);
                form.submit();
            }
        });

        // Prevent click on upload area from triggering file dialog twice
        uploadArea.addEventListener("click", function (event) {
            if (event.target.closest(".btn-upload")) {
                event.preventDefault();
            }
        });
    });
}


/**
 * Update the upload area text to show the selected filename.
 */
function updateUploadLabel(uploadArea, filename) {
    const textEl = uploadArea.querySelector(".upload-text");
    if (textEl) {
        textEl.textContent = "Uploading: " + filename;
    }
}
