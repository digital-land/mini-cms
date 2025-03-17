import { initAll } from "govuk-frontend";

// Initialize all GOV.UK Frontend components
document.addEventListener("DOMContentLoaded", () => {
  document.body.className +=
    " js-enabled" +
    ("noModule" in HTMLScriptElement.prototype
      ? " govuk-frontend-supported"
      : "");

  initAll();
});
