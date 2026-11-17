// node workers/timer/test.mjs - one simulated day (every minute) against a fake GitHub: each job starts once per cron time,
// a job GitHub's own timer already ran is not started again, and a missed minute is caught up within LATE_MIN.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const src = readFileSync(new URL("./src/index.js", import.meta.url), "utf8").replace(/^import SCHEDULE.*$/m, "const SCHEDULE = {repos:{}};");
const mod = await import("data:text/javascript," + encodeURIComponent(src));
const schedule = JSON.parse(readFileSync(new URL("./src/schedule.json", import.meta.url), "utf8"));
const kovai = { repos: { K: schedule.repos["nithiyananthamQA/kovaiminnal-autopost"] } };

function fake(runs) {      // runs: {file: [Date]}
  return async (env, method, path, body) => {
    const file = path.split("/workflows/")[1].split("/")[0];
    if (method === "GET") {
      const since = new Date(decodeURIComponent(path.split("created=")[1]).replace(">=", ""));
      return { ok: true, json: async () => ({ total_count: (runs[file] || []).filter((t) => t >= since).length }) };
    }
    return { status: 204, _file: file };
  };
}
async function day(schedule, start, minutes, runs = {}, skip = new Set()) {
  const n = {}, call = fake(runs), at = {};
  for (let m = 0; m < minutes; m++) {
    const now = new Date(start.getTime() + m * 60000);
    if (skip.has(m)) continue;
    for (const s of await mod.tick({}, now, schedule, call)) {
      const f = s.split(" ")[1];
      n[f] = (n[f] || 0) + 1;
      (runs[f] ||= []).push(now);
      (at[f] ||= []).push(now);
    }
  }
  return { n, at };
}
const D = new Date("2026-11-18T18:30:00Z");      // 00:00 IST 19 Nov (an odd day: cloudclean "*/2" runs on odd days of the month)
const { n, at } = await day(kovai, D, 1440);
console.log(n);
assert.equal(n["post.yml"], 24);
assert.equal(n["pick.yml"], 6);
assert.equal(n["powercut.yml"], 17);
assert.equal(n["comments.yml"], 18);
assert.equal(n["rasipalan.yml"], 4);
assert.equal(n["insights.yml"], 1);
assert.equal(n["goldrate.yml"], 3);
const ist = (d) => new Date(d.getTime() + 330 * 60000).toISOString().slice(11, 16);
assert.deepEqual(at["pick.yml"].map(ist), ["01:00", "05:00", "09:00", "13:00", "17:00", "21:00"]);
assert.equal(ist(at["goldrate.yml"][0]), "09:35");

// GitHub's own timer already ran pick at 05:02 -> the Worker does not start it again
const r2 = await day(kovai, new Date("2026-11-18T23:25:00Z"), 20, { "pick.yml": [new Date("2026-11-18T23:32:00Z")] });
assert.equal(r2.n["pick.yml"] || 0, 0);
// the Worker missed the 05:00 minute (Cloudflare skipped a tick) -> started at 05:01
const r3 = await day(kovai, new Date("2026-11-18T23:25:00Z"), 20, {}, new Set([5]));
assert.equal(ist(r3.at["pick.yml"][0]), "05:01");
// a time older than LATE_MIN is left
assert.equal(mod.lastSlot(["30 23 * * *"], new Date("2026-11-18T23:46:00Z")), null);
console.log("timer test OK");
