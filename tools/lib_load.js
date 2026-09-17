// Loads the app's content + level logic from index.html into Node (no browser needed).
const fs = require("fs"), path = require("path"), vm = require("vm");
module.exports = function load() {
  const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
  const s = html.slice(html.lastIndexOf("<script>") + 8, html.lastIndexOf("</script>"));
  const cut = s.indexOf("/* ---- Progress ---- */");
  const back = s.slice(s.indexOf("const EX_SPECIAL"), s.indexOf("function picFor"));
  const code = s.slice(0, cut) + "\n" + back + `
    const slugId = s => s.toLowerCase().replace(/ä/g,"ae").replace(/ö/g,"oe").replace(/ü/g,"ue").replace(/ß/g,"ss").replace("·pl","").replace(/^(der|die|das|sich) /,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
    globalThis.APP = {PEOPLE,SHIFTS,BODY,WORDS,DOCS,EMERGENCY,DRILL,TR,GOALS,LEVELS,SPELL,DOC_KEYS,LETTER,levelDeck,levelTitle,roundForCard,exchangesFor,goalCards,backParts,wordByEn,slugId,plain,slotText};`;
  const ctx = { console, window: {}, document: { querySelector: () => null, addEventListener() {} }, localStorage: undefined, fetch: () => Promise.reject() };
  vm.createContext(ctx);
  vm.runInContext(code, ctx);
  return ctx.APP;
};
