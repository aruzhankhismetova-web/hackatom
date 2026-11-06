#!/usr/bin/env node
// Open a chrome://settings URL in the already running Assignment 4 Chrome
// and scroll a label into view. Reads CDP on 127.0.0.1:9223.
const http = require("http");
const url = process.argv[2];
const scrollText = process.argv[3] || "";

function get(path) {
  return new Promise((resolve, reject) => {
    http
      .get("http://127.0.0.1:9223" + path, (res) => {
        let d = "";
        res.on("data", (c) => (d += c));
        res.on("end", () => resolve(d));
      })
      .on("error", reject);
  });
}

(async () => {
  const list = JSON.parse(await get("/json/list"));
  const page = list.find(
    (t) => t.type === "page" && (t.url || "").startsWith("chrome://settings")
  );
  if (!page) {
    console.error("no settings page");
    process.exit(1);
  }
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  ws.addEventListener("message", (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      pending.get(m.id)(m);
      pending.delete(m.id);
    }
  });
  const send = (method, params = {}) =>
    new Promise((resolve) => {
      const my = ++id;
      pending.set(my, resolve);
      ws.send(JSON.stringify({ id: my, method, params }));
    });
  await new Promise((r) => ws.addEventListener("open", r));
  await send("Page.enable");
  await send("Runtime.enable");
  if (url) await send("Page.navigate", { url });
  await new Promise((r) => setTimeout(r, 900));
  const expr = `(() => {
    const want = ${JSON.stringify(scrollText)};
    function walk(node, fn) {
      if (!node) return;
      if (node.shadowRoot) walk(node.shadowRoot, fn);
      fn(node);
      for (const ch of node.childNodes || []) walk(ch, fn);
    }
    walk(document.documentElement, (node) => {
      if (node.nodeType === 1 && (node.innerText || "").trim() === "No thanks") node.click();
    });
    if (!want) return location.href;
    let el = null;
    walk(document.documentElement, (node) => {
      if (el || node.nodeType !== 1) return;
      const direct = [...node.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(" ").trim();
      if (direct === want) el = node;
    });
    if (el) el.scrollIntoView({ block: "center" });
    return location.href + " scrolled=" + !!el;
  })()`;
  const res = await send("Runtime.evaluate", { expression: expr, returnByValue: true });
  console.log(res.result && res.result.result && res.result.result.value);
  ws.close();
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
