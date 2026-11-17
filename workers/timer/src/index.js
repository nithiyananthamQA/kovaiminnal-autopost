// test - the pages' job timer (owner 17-18 Nov; plain name in Cloudflare, owner 18 Nov: "use GitHub only when needed"): every minute, start each page's GitHub workflows at their OWN cron
// times (schedule.json, made by tools/make_timer.py from the .yml schedule blocks) - replaces the always-running keeper.yml and the
// Google Apps Script timers. A job whose time came within the last LATE_MIN minutes and that has no run created since that time is
// started once (workflow_dispatch with the inputs of a live run); GitHub's own timer running it first counts too. Nothing else runs.
import SCHEDULE from "./schedule.json";

export const LATE_MIN = 15;

function field(spec, lo, hi) {
  const out = new Set();
  for (const part of spec.split(",")) {
    let [range, step] = part.split("/");
    step = step ? Number(step) : 1;
    let a = lo, b = hi;
    if (range !== "*") {
      [a, b] = range.includes("-") ? range.split("-").map(Number) : [Number(range), step > 1 ? hi : Number(range)];
    }
    for (let v = a; v <= b; v += step) out.add(v);
  }
  return out;
}

export function matches(cron, d) {      // d: a UTC Date; 5-field cron in UTC like GitHub's
  const [mi, ho, dom, mon, dow] = cron.trim().split(/\s+/);
  return field(mi, 0, 59).has(d.getUTCMinutes()) && field(ho, 0, 23).has(d.getUTCHours()) &&
    field(dom, 1, 31).has(d.getUTCDate()) && field(mon, 1, 12).has(d.getUTCMonth() + 1) && field(dow, 0, 6).has(d.getUTCDay());
}

export function lastSlot(crons, now) {      // the most recent cron time within LATE_MIN minutes (or null)
  const t = new Date(Math.floor(now.getTime() / 60000) * 60000);
  for (let k = 0; k <= LATE_MIN; k++) {
    const d = new Date(t.getTime() - k * 60000);
    if (crons.some((c) => matches(c, d))) return d;
  }
  return null;
}

async function gh(env, method, path, body) {
  const r = await fetch(`https://api.github.com/${path}`, {
    method,
    headers: { Authorization: `Bearer ${env.GH_TOKEN}`, Accept: "application/vnd.github+json", "User-Agent": "test",
               "X-GitHub-Api-Version": "2022-11-28", ...(body ? { "Content-Type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  return r;
}

export async function tick(env, now, schedule = SCHEDULE, call = gh) {
  const started = [];
  for (const [repo, jobs] of Object.entries(schedule.repos)) {
    for (const job of jobs) {
      const slot = lastSlot(job.crons, now);
      if (!slot) continue;
      const since = slot.toISOString().replace(/\.\d+Z$/, "Z");
      const runs = await call(env, "GET", `repos/${repo}/actions/workflows/${job.file}/runs?per_page=1&created=%3E%3D${since}`);
      if (!runs.ok) { console.log(repo, job.file, "runs not read", runs.status); continue; }
      if ((await runs.json()).total_count > 0) continue;      // already ran since its time (by us or GitHub's own timer)
      const r = await call(env, "POST", `repos/${repo}/actions/workflows/${job.file}/dispatches`, { ref: "main", inputs: job.inputs });
      console.log(repo, job.file, "slot", since, r.status === 204 ? "STARTED" : `not started (${r.status})`);
      if (r.status === 204) started.push(`${repo} ${job.file}`);
    }
  }
  return started;
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(tick(env, new Date(event.scheduledTime)));
  },
  async fetch() {
    return new Response("ok\n");
  },
};
