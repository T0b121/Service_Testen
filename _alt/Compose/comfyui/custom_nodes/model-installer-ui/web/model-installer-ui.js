import { app } from "../../scripts/app.js";

const style = `
  #t0b-model-installer-launch { border: 1px solid #4f8fff; border-radius: 7px; background: #18335d; color: #fff; padding: 6px 9px; font: 600 12px sans-serif; cursor: pointer; margin-left: auto; }
  #t0b-model-installer-launch:hover { background: #245093; }
  #t0b-model-installer-backdrop { position: fixed; inset: 0; z-index: 3000; background: rgba(0,0,0,.68); display: flex; align-items: center; justify-content: center; }
  #t0b-model-installer { width: min(980px, calc(100vw - 48px)); height: min(700px, calc(100vh - 64px)); display: flex; flex-direction: column; gap: 12px; padding: 20px; border: 1px solid #4b5563; border-radius: 10px; background: #161a20; color: #e5e7eb; font: 14px sans-serif; box-shadow: 0 24px 70px #000; }
  #t0b-model-installer header { display: flex; align-items: center; gap: 12px; }
  #t0b-model-installer h2 { margin: 0; font-size: 19px; flex: 1; }
  #t0b-model-installer input { flex: 1; min-width: 160px; padding: 9px; border: 1px solid #4b5563; border-radius: 6px; background: #0f1217; color: #fff; }
  #t0b-model-installer button { padding: 8px 11px; border: 1px solid #5b6471; border-radius: 6px; background: #2a3341; color: #fff; cursor: pointer; }
  #t0b-model-installer button:hover { background: #3b4759; }
  #t0b-model-installer button.install { background: #1857a6; border-color: #3d82d4; }
  #t0b-model-installer button:disabled { opacity: .55; cursor: default; }
  #t0b-model-installer .hint, #t0b-model-installer .status { color: #aeb8c7; }
  #t0b-model-installer .filters { display: flex; flex-wrap: wrap; gap: 7px; }
  #t0b-model-installer .filter { font-size: 12px; padding: 6px 9px; }
  #t0b-model-installer .filter[data-state="1"] { background: #1857a6; border-color: #3d82d4; }
  #t0b-model-installer .filter[data-state="2"] { background: #59303a; border-color: #9a5364; }
  #t0b-model-installer .results { overflow: auto; border: 1px solid #303946; border-radius: 6px; }
  #t0b-model-installer .row { display: grid; grid-template-columns: minmax(280px, 1fr) 110px 115px 120px; gap: 10px; align-items: center; padding: 10px; border-bottom: 1px solid #2b3340; }
  #t0b-model-installer .row:last-child { border-bottom: 0; }
  #t0b-model-installer .name { font-weight: 600; color: #e8eef9; overflow-wrap: anywhere; }
  #t0b-model-installer .meta { color: #aeb8c7; font-size: 12px; overflow-wrap: anywhere; }
  #t0b-model-installer .installed { color: #70d59c; font-size: 12px; }
  .t0b-instance-button { box-sizing: border-box; min-width: 92px; padding: 5px 9px; margin-left: 7px; border: 1px solid #5b6471; border-radius: 4px; background: #2a3341; color: #fff; font: 600 12px sans-serif; line-height: 16px; white-space: nowrap; cursor: pointer; vertical-align: middle; }
  .t0b-instance-button:hover { background: #3b4759; }
  .t0b-instance-button:disabled { opacity: .58; cursor: default; }
  .t0b-instance-all-wrap { display: block; width: 100%; margin-top: 6px; }
  .t0b-instance-all { display: block; width: 100%; margin: 0; }
`;

function text(value) { return document.createTextNode(value ?? ""); }

function makeElement(tag, attrs = {}, children = []) {
  const element = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") element.className = value;
    else if (key === "dataset") Object.assign(element.dataset, value);
    else if (key.startsWith("on")) element.addEventListener(key.slice(2), value);
    else element[key] = value;
  }
  for (const child of children) element.append(child);
  return element;
}

function sizeBytes(value) {
  if (typeof value === "number") return value;
  const match = String(value || "").trim().match(/^([0-9]+(?:\.[0-9]+)?)\s*(B|KB|MB|GB|TB)$/i);
  if (!match) return 0;
  return Number(match[1]) * ({ b: 1, kb: 1024, mb: 1024 ** 2, gb: 1024 ** 3, tb: 1024 ** 4 }[match[2].toLowerCase()]);
}

function humanSize(value) {
  const bytes = sizeBytes(value);
  if (!bytes) return value ? String(value) : "Größe unbekannt";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const amount = bytes / (1024 ** index);
  return `${amount >= 10 || index === 0 ? amount.toFixed(0) : amount.toFixed(1)} ${units[index]}`;
}

function leafText(value, root = document) {
  return [...root.querySelectorAll("*")].filter((element) => element.children.length === 0 && element.textContent.trim() === value);
}

function workflowModelNames(models) {
  const modal = document.getElementById("t0b-model-installer-backdrop");
  return new Set(models.filter((model) => leafText(model.filename || "").some((element) => !modal || !modal.contains(element))).map((model) => model.filename));
}

function triButton(label, state, onChange) {
  const values = ["Egal", "Nur ja", "Nur nein"];
  const button = makeElement("button", { class: "filter", dataset: { state }, textContent: `${label}: ${values[state]}` });
  button.title = "Klicken: Egal → Nur ja → Nur nein";
  button.addEventListener("click", () => onChange((state + 1) % 3));
  return button;
}

function triMatches(state, value) { return state === 0 || (state === 1 ? value : !value); }

async function openInstaller() {
  const backdrop = makeElement("div", { id: "t0b-model-installer-backdrop" });
  const panel = makeElement("section", { id: "t0b-model-installer" });
  const status = makeElement("div", { class: "status" }, [text("Lade offizielle Modellliste …")]);
  const results = makeElement("div", { class: "results" });
  const filters = makeElement("div", { class: "filters" });
  const search = makeElement("input", { placeholder: "Modelle suchen, z. B. SDXL, Flux, Qwen …" });
  const close = makeElement("button", { textContent: "Schließen", onclick: () => backdrop.remove() });
  panel.append(makeElement("header", {}, [makeElement("h2", {}, [text("Model Installer")]), close]), makeElement("div", { class: "hint" }, [text("Downloads werden vom ComfyUI-Server in die passenden Modellordner geladen.")]), search, filters, status, results);
  backdrop.append(panel);
  document.body.append(backdrop);
  backdrop.addEventListener("click", (event) => { if (event.target === backdrop) backdrop.remove(); });

  const filterState = { workflow: 0, installed: 0, safetensors: 0, small: 0 };
  let models = [];
  const render = () => {
    const workflow = workflowModelNames(models);
    const query = search.value.trim().toLowerCase();
    const matches = models.filter((model) => {
      const installed = String(model.installed).toLowerCase() === "true";
      const haystack = [model.name, model.filename, model.base, model.type, model.description, model.save_path].join(" ").toLowerCase();
      return (!query || haystack.includes(query)) && triMatches(filterState.workflow, workflow.has(model.filename)) && triMatches(filterState.installed, installed) && triMatches(filterState.safetensors, String(model.filename || "").toLowerCase().endsWith(".safetensors")) && triMatches(filterState.small, sizeBytes(model.size) > 0 && sizeBytes(model.size) < 5 * 1024 ** 3);
    }).slice(0, 150);
    filters.replaceChildren(triButton("Im Workflow", filterState.workflow, (value) => { filterState.workflow = value; render(); }), triButton("Installiert", filterState.installed, (value) => { filterState.installed = value; render(); }), triButton("SafeTensors", filterState.safetensors, (value) => { filterState.safetensors = value; render(); }), triButton("Unter 5 GB", filterState.small, (value) => { filterState.small = value; render(); }));
    results.replaceChildren();
    for (const model of matches) {
      const installed = String(model.installed).toLowerCase() === "true";
      const install = makeElement("button", { class: "install", textContent: installed ? "Installiert" : "Installieren", disabled: installed });
      install.addEventListener("click", async () => {
        install.disabled = true; install.textContent = "Wird eingeplant …";
        const payload = { ...model, ui_id: `t0b-model-${crypto.randomUUID()}` };
        const response = await fetch("/v2/manager/queue/batch", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ batch_id: crypto.randomUUID(), install_model: [payload] }) });
        if (!response.ok) { install.disabled = false; install.textContent = "Installieren"; status.textContent = `Download konnte nicht gestartet werden (${response.status}).`; return; }
        status.textContent = `${model.name || model.filename} wird serverseitig heruntergeladen. Der Fortschritt erscheint in der ComfyUI-Konsole.`;
        install.textContent = "Download läuft";
      });
      results.append(makeElement("div", { class: "row" }, [makeElement("div", {}, [makeElement("div", { class: "name" }, [text(model.name || model.filename)]), makeElement("div", { class: "meta" }, [text(model.filename || "")])]), makeElement("div", { class: "meta" }, [text(model.type || model.base || "")]), makeElement("div", { class: "meta" }, [text(humanSize(model.size))]), installed ? makeElement("div", { class: "installed" }, [text("Installiert")]) : install]));
    }
    status.textContent = matches.length ? `${matches.length} passende Modelle${matches.length === 150 ? " (Anzeige begrenzt)" : ""}` : "Keine passenden Modelle gefunden.";
  };
  search.addEventListener("input", render);
  try { const response = await fetch("/v2/externalmodel/getlist?mode=cache"); if (!response.ok) throw new Error(`HTTP ${response.status}`); models = (await response.json()).models || []; render(); search.focus(); } catch (error) { status.textContent = `Die Modellliste konnte nicht geladen werden: ${error.message}`; }
}

async function serverInstall(url, folder, filename, button) {
  button.disabled = true; button.textContent = "Wird eingeplant …";
  const response = await fetch("/t0b121/model-installer/download", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url, folder, filename }) });
  const payload = await response.json();
  if (!response.ok) { button.disabled = false; button.textContent = "Installieren"; alert(payload.error || "Download konnte nicht gestartet werden."); return; }
  const update = async () => {
    const status = await fetch(`/t0b121/model-installer/status/${payload.id}`).then((result) => result.json());
    const total = status.total ? ` / ${humanSize(status.total)}` : "";
    button.textContent = status.state === "complete" ? "Installiert" : status.state === "error" ? "Fehler" : `${status.state === "queued" ? "Wartet" : "Lädt"} ${humanSize(status.received)}${total}`;
    if (status.state === "queued" || status.state === "running") setTimeout(update, 1500);
  };
  update();
}

let workflowSources;
let workflowSourceLoading;
async function getWorkflowSources() {
  if (workflowSources) return workflowSources;
  if (!workflowSourceLoading) workflowSourceLoading = Promise.all([fetch("/t0b121/model-installer/workflow-models").then((result) => result.json()), fetch("/v2/externalmodel/getlist?mode=cache").then((result) => result.json()).catch(() => ({ models: [] }))]).then(([sources, catalog]) => {
    const sizes = new Map((catalog.models || []).map((model) => [model.filename, model.size]));
    workflowSources = Object.fromEntries(Object.entries(sources).map(([filename, source]) => [filename, { ...source, size: sizes.get(filename) || "" }]));
    return workflowSources;
  }).catch(() => (workflowSources = {}));
  return workflowSourceLoading;
}

function currentGraphSources() {
  const sources = {};
  const seen = new WeakSet();
  const folders = new Set(["checkpoints", "loras", "vae", "text_encoders", "diffusion_models", "clip_vision", "controlnet", "upscale_models", "embeddings"]);
  const visit = (value) => {
    if (!value || typeof value !== "object" || seen.has(value)) return;
    seen.add(value);
    const filename = value.name || value.filename;
    const folder = value.directory || value.save_path;
    if (typeof filename === "string" && typeof value.url === "string" && folders.has(folder)) {
      sources[filename] = { url: value.url, folder, size: value.size || "" };
    }
    for (const child of Object.values(value)) visit(child);
  };
  // Workflow-specific model metadata is kept client-side by ComfyUI. This is
  // the same metadata used for its native Download action.
  visit(app.graph);
  return sources;
}

function nearestDownload(label) {
  let host = label.parentElement;
  for (let count = 0; host && count < 8; count += 1, host = host.parentElement) {
    const downloads = [...host.querySelectorAll("button")].filter((button) => button.textContent.trim() === "Download");
    // The row itself has exactly one native Download button. Wider containers
    // contain several rows and must never be used as an insertion target.
    if (downloads.length === 1) return downloads[0];
  }
  return null;
}

async function addMissingModelActions() {
  if (document.getElementById("t0b-model-installer-backdrop")) return;
  const sources = { ...(await getWorkflowSources()), ...currentGraphSources() };
  const uniqueEntries = new Map();
  for (const filename of Object.keys(sources)) {
    const buttons = [...document.querySelectorAll(`button[data-instance-filename="${CSS.escape(filename)}"]`)];
    // A ComfyUI re-render can retain previous injected controls. Keep exactly
    // one per model before doing any new insertion.
    buttons.slice(1).forEach((button) => button.remove());
  }
  for (const [filename, source] of Object.entries(sources)) {
    for (const label of leafText(filename)) {
      if (label.closest("#t0b-model-installer")) continue;
      const download = nearestDownload(label);
      // The template's "Model link" note has no browser Download action. Keep
      // the server controls only in the Missing Models list, where their
      // position is stable directly beside ComfyUI's Download button.
      if (!download) continue;
      label.style.display = "inline-block";
      label.style.maxWidth = "min(250px, 30vw)";
      label.style.overflow = "hidden";
      label.style.textOverflow = "ellipsis";
      label.style.whiteSpace = "nowrap";
      if (download.dataset.instanceInstaller) {
        const existing = [...document.querySelectorAll(`button[data-instance-filename="${CSS.escape(filename)}"]`)][0];
        uniqueEntries.set(filename, { filename, source, install: existing });
        continue;
      }
      download.dataset.instanceInstaller = "true";
      const install = makeElement("button", { class: "t0b-instance-button", textContent: "Installieren" });
      install.dataset.instanceFilename = filename;
      install.style.flex = "0 0 auto";
      install.addEventListener("click", () => serverInstall(source.url, source.folder, filename, install));
      download.insertAdjacentElement("afterend", install);
      uniqueEntries.set(filename, { filename, source, install });
    }
  }
  const total = [...uniqueEntries.values()].reduce((sum, entry) => sum + sizeBytes(entry.source.size), 0);
  for (const button of document.querySelectorAll("button")) {
    if (button.closest("#t0b-model-installer") || button.dataset.instanceAll || !/^Download all/.test(button.textContent.trim()) || !uniqueEntries.size) continue;
    button.dataset.instanceAll = "true";
    const all = makeElement("button", { class: "t0b-instance-button t0b-instance-all", textContent: `Alle installieren${total ? ` (${humanSize(total)})` : ""}` });
    all.addEventListener("click", () => {
      for (const entry of uniqueEntries.values()) {
        if (entry.install instanceof HTMLButtonElement && !entry.install.disabled) serverInstall(entry.source.url, entry.source.folder, entry.filename, entry.install);
      }
    });
    // The native Download all control is a flex item. A separate block after
    // its wrapper prevents the two controls from squeezing each other.
    const allWrap = makeElement("div", { class: "t0b-instance-all-wrap" }, [all]);
    (button.parentElement || button).insertAdjacentElement("afterend", allWrap);
  }
}

function placeLauncher() {
  const title = leafText("Model Library")[0];
  const host = title?.parentElement;
  if (!host || document.getElementById("t0b-model-installer-launch")) return;
  host.style.display = "flex"; host.style.alignItems = "center";
  host.append(makeElement("button", { id: "t0b-model-installer-launch", textContent: "Model Installer", onclick: openInstaller }));
}

let missingActionsTimer;
function scheduleMissingActions() { clearTimeout(missingActionsTimer); missingActionsTimer = setTimeout(() => { addMissingModelActions(); }, 100); }

app.registerExtension({
  name: "t0b121.ModelInstaller",
  setup() {
    const styleElement = document.createElement("style"); styleElement.textContent = style; document.head.append(styleElement);
    const observer = new MutationObserver(() => { placeLauncher(); scheduleMissingActions(); });
    observer.observe(document.body, { childList: true, subtree: true });
    placeLauncher(); scheduleMissingActions();
  },
});
