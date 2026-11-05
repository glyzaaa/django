"use strict";
document.querySelectorAll("[data-workflow]").forEach(form => {
  const operation = form.querySelector("[name=operation]");
  function updateFields() {
    const op = operation.value;
    const needsValue = ["append", "prepend", "insert_at", "remove", "index_of"].includes(op);
    const needsIndex = ["insert_at", "remove_at", "get"].includes(op);
    [["value", needsValue], ["index", needsIndex]].forEach(([field, needed]) => {
      const group = form.querySelector(`[data-field="${field}"]`);
      group.hidden = !needed;
      group.querySelector("input").disabled = !needed;
    });
  }
  operation.addEventListener("change", updateFields);
  updateFields();
});
const menuToggle = document.querySelector("[data-menu-toggle]");
function closeNavigation() { document.body.classList.remove("nav-open"); menuToggle?.setAttribute("aria-expanded", "false"); }
menuToggle?.addEventListener("click", () => {
  const open = document.body.classList.toggle("nav-open");
  menuToggle.setAttribute("aria-expanded", String(open));
});
document.addEventListener("click", event => {
  if (document.body.classList.contains("nav-open") && !event.target.closest(".sidebar,[data-menu-toggle]")) closeNavigation();
  document.querySelectorAll(".user-menu[open],.workspace-switch[open]").forEach(details => { if (!details.contains(event.target)) details.open = false; });
});
document.addEventListener("keydown", event => {
  if (event.key === "Escape") { closeNavigation(); document.querySelectorAll(".user-menu,.workspace-switch").forEach(x => x.open = false); }
});
document.querySelectorAll("[data-dismiss]").forEach(button => button.addEventListener("click", () => button.closest(".notice").remove()));
document.querySelectorAll("form[data-confirm]").forEach(form => form.addEventListener("submit", event => { if (!window.confirm(form.dataset.confirm)) event.preventDefault(); }));
document.querySelectorAll("[data-copy]").forEach(button => button.addEventListener("click", async () => {
  const input = document.getElementById(button.dataset.copy);
  input.select();
  try { await navigator.clipboard.writeText(input.value); button.textContent = "Copied"; }
  catch { button.textContent = "Link selected — copy it"; }
}));
