"""owner 14 Nov: GitHub's own timer (cron) almost never starts Kovai Minnal's jobs - the Kovai Minnal bridge (apps_script/Code.gs,
startKovaiJobs) starts them every 5 minutes on the workflows' own times. These tests run that JavaScript under node with a fake
Apps Script (no network) and check it against the workflow files."""
import json, os, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WF = ROOT / ".github" / "workflows"
CODE = (ROOT / "apps_script" / "Code.gs").read_text(encoding="utf-8")
BLOCK = re.search(r"\n// ===== KOVAI JOBS TIMER \(start\).*?\n// ===== KOVAI JOBS TIMER \(end\) =====\n", CODE, re.S)

FAKE = r"""
var store = {}, mails = [], calls = [], states = {}, scheduled = {}, dispatchCode = 204;
function props_() { return { getProperty: function (k) { return k in store ? store[k] : null; }, setProperty: function (k, v) { store[k] = String(v); } }; }
var OWNER_EMAIL = 'owner@example.invalid';
var Logger = { log: function () {} };
var GmailApp = { sendEmail: function (to, subject) { mails.push(subject); } };
var LockService = { getUserLock: function () { return { tryLock: function () { return true; }, releaseLock: function () {} }; } };
var UrlFetchApp = { fetch: function (url, o) {
  var path = url.replace('https://api.github.com/repos/nithiyananthamQA/kovaiminnal-autopost', '');
  calls.push({ method: o.method, path: path, body: o.payload ? JSON.parse(o.payload) : null });
  var resp = function (code, obj) { return { getResponseCode: function () { return code; }, getContentText: function () { return obj === undefined ? '' : JSON.stringify(obj); } }; };
  if (path.indexOf('/actions/workflows?') === 0) return resp(200, { workflows: KOVAI_JOBS.map(function (j) { return { path: '.github/workflows/' + j.file, state: states[j.file] || 'active' }; }) });
  var m = path.match(/^\/actions\/workflows\/([^/]+)\/runs\?/);
  if (m) return resp(200, { total_count: scheduled[m[1]] || 0 });
  if (/\/dispatches$/.test(path)) return dispatchCode === 204 ? resp(204) : resp(dispatchCode, { message: 'Bad credentials' });
  throw new Error('unexpected call ' + path);
} };
"""

SCENARIOS = r"""
function at(hhmm) { var p = hhmm.split(':'); return new Date(Date.UTC(2026, 10, 14, +p[0], +p[1]) - 5.5 * 3600000); }      // IST
function tick(hhmm) {
  calls = []; kovaiTick_(at(hhmm));
  var o = {};
  calls.filter(function (c) { return c.method === 'post'; }).forEach(function (c) { o[c.path.split('/')[3]] = c.body.inputs; });
  return o;
}
function reset() { store = { GH_DISPATCH_TOKEN: 't' }; mails = []; states = {}; scheduled = {}; dispatchCode = 204; }
var out = {};
reset(); out.t0602 = tick('06:02'); out.t0604 = tick('06:04'); out.t1002 = tick('10:02');
reset(); out.t2335 = tick('23:35'); out.t0100 = tick('01:00');
reset(); out.t0731 = tick('07:31');
reset(); out.t0215 = tick('02:15');
reset(); out.t0310 = tick('03:10');
reset(); states['post.yml'] = 'disabled_manually'; out.disabled = tick('06:02'); out.disabledMails = mails.length; out.disabledMark = store['KOVAI_SLOT_post.yml'];
reset(); states['pick.yml'] = 'disabled_inactivity'; out.inactive = tick('09:02'); out.inactiveMails = mails.length;
reset(); dispatchCode = 401; out.fail1 = tick('09:02'); out.failMark = store['KOVAI_SLOT_pick.yml'] || null; out.fail2 = tick('09:04'); out.failMails = mails.slice();
reset(); scheduled['pick.yml'] = 1; out.byGithub = tick('09:02'); out.byGithubMark = store['KOVAI_SLOT_pick.yml'];
out.runsQuery = calls.filter(function (c) { return /pick\.yml\/runs/.test(c.path); }).map(function (c) { return c.path; });
reset(); delete store.GH_DISPATCH_TOKEN; out.noToken = tick('06:02'); out.noTokenMails = mails.length;
out.slots = {}; out.inputs = {};
KOVAI_JOBS.forEach(function (j) {
  var s = [], all = {};
  for (var m = 0; m < 1440; m++) if (kovaiSlot_(j, m) === m) s.push(kovaiHhmm_(m));
  out.slots[j.file] = s;
  Object.keys(j.inputs).forEach(function (k) { all[k] = j.inputs[k]; });
  Object.keys(j.slotInputs || {}).forEach(function (t) { Object.keys(j.slotInputs[t]).forEach(function (k) { all[k] = j.slotInputs[t][k]; }); });
  out.inputs[j.file] = all;
});
console.log(JSON.stringify(out));
"""


def expand(field, n):
    vals = set()
    for part in field.split(","):
        step = 1
        if "/" in part:
            part, step = part.split("/")
            step = int(step)
        lo, hi = (0, n - 1) if part == "*" else map(int, part.split("-")) if "-" in part else (int(part), int(part))
        vals.update(range(lo, hi + 1, step))
    return vals


def cron_ist(text):
    """IST HH:MM of every cron time in a workflow file"""
    out = set()
    for expr in re.findall(r'cron:\s*"([^"]+)"', text):
        mi, hr = expr.split()[:2]
        for h in expand(hr, 24):
            for m in expand(mi, 60):
                t = (h * 60 + m + 330) % 1440
                out.add(f"{t // 60:02d}:{t % 60:02d}")
    return sorted(out)


def dispatch_inputs(text):
    lines = text.splitlines()
    i = next(n for n, line in enumerate(lines) if line.strip() == "workflow_dispatch:")
    names = []
    for line in lines[i + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= 2:
            break
        m = re.match(r"^      ([a-z_]+):\s*$", line)
        if m:
            names.append(m.group(1))
    return names


@unittest.skipUnless(shutil.which("node"), "node not installed")
class KovaiTimer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert BLOCK, "KOVAI JOBS TIMER block missing in apps_script/Code.gs"
        js = Path(tempfile.mkdtemp()) / "timer_test.js"
        js.write_text(FAKE + BLOCK.group(0) + SCENARIOS, encoding="utf-8")
        r = subprocess.run(["node", str(js)], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-1500:]
        cls.out = json.loads(r.stdout)

    def test_first_tick_after_six(self):
        o = self.out
        self.assertEqual(sorted(o["t0602"]), ["comments.yml", "post.yml", "powercut.yml"])      # owner 16 Nov: pick rounds 01/05/09/13/17/21
        self.assertEqual(o["t0602"]["post.yml"], {"dry_run": "false", "prebuild": "false", "timer": "true"})
        self.assertEqual(o["t0604"], {})      # the same slots are never started twice

    def test_quiet_hours_and_fixed_times(self):
        o = self.out
        self.assertNotIn("post.yml", o["t2335"])      # posting timer 05:30 - 23:30 IST
        self.assertEqual(o["t0100"], {"pick.yml": {"dry": "0", "resume": "0"}})      # owner 16 Nov: the 01:00 pick round (reference)
        self.assertEqual(o["t0731"]["rasipalan.yml"], {"dry": "0", "date": "", "repost": "0"})      # waits until 07:31 itself
        self.assertIn("insights.yml", o["t0215"])
        self.assertNotIn("insights.yml", o["t0310"])

    def test_switched_off_and_failures(self):
        o = self.out
        self.assertNotIn("post.yml", o["disabled"])      # gh workflow disable still stops everything - quietly
        self.assertEqual((o["disabledMails"], o["disabledMark"]), (0, "2026-11-14 06:00"))
        self.assertNotIn("pick.yml", o["inactive"])      # switched off by GitHub itself: the owner is told
        self.assertEqual(o["inactiveMails"], 1)
        self.assertIsNone(o["failMark"])      # a failed start is tried again at the next tick ...
        self.assertIn("pick.yml", o["fail2"])
        self.assertEqual(o["failMails"], ["[KOVAIMINNAL PROBLEM] GitHub job could not be started"])      # ... with one e-mail a day
        self.assertEqual((o["noToken"], o["noTokenMails"]), ({}, 1))

    def test_slot_github_already_started_is_not_started_again(self):
        o = self.out
        self.assertNotIn("pick.yml", o["byGithub"])      # a second pick round would post more news
        self.assertEqual(o["byGithubMark"], "2026-11-14 09:00")
        self.assertEqual(o["runsQuery"], ["/actions/workflows/pick.yml/runs?event=schedule&per_page=1&created=%3E%3D2026-11-14T03%3A30%3A00Z"])

    def test_times_follow_the_workflow_schedules(self):
        for f, slots in self.out["slots"].items():
            cron = cron_ist((WF / f).read_text(encoding="utf-8"))
            if f == "post.yml":      # the Google timer: every 5 minutes 05:30 - 23:30 IST
                self.assertEqual(slots, [f"{m // 60:02d}:{m % 60:02d}" for m in range(330, 1411, 5)])
                # GITHUB SAFE MODE (owner 17 Nov): post.yml's own schedule is hourly and the owner stops this Google timer
                # (stopKovaiTimer) - back to "slots within the 5-minute cron" when the Cloudflare Workers timer takes over
            else:      # SAFE MODE 17 Nov: comments / power cuts hourly on GitHub - every GitHub time is still a timer time
                self.assertTrue(set(cron) <= set(slots), f)

    def test_inputs_exist_and_mean_a_live_run(self):
        live = {"dry": "0", "dry_run": ("0", "false"), "prebuild": "false", "resume": "0", "repost": "0", "date": "", "timer": "true"}
        for f, inputs in self.out["inputs"].items():
            declared = dispatch_inputs((WF / f).read_text(encoding="utf-8"))
            for k, v in inputs.items():
                self.assertIn(k, declared, f"{f}: input {k} not in the workflow (GitHub refuses the start)")
                if k in live:
                    self.assertIn(v, live[k] if isinstance(live[k], tuple) else (live[k],), f"{f}: {k}={v!r} is not a live run")


class Bridges(unittest.TestCase):
    def test_district_bridge_has_no_kovai_timer(self):
        gs = (ROOT / "apps_script" / "Code.districts.gs").read_text(encoding="utf-8")
        for word in ("KOVAI JOBS TIMER", "startKovaiJobs", "startKovaiTimer", "KOVAI_JOBS", "kovaiTick_"):
            self.assertNotIn(word, gs)
        self.assertIn("function startDistrictJob()", gs)      # the district job keeps its own timer
        self.assertIn("function startTimer()", gs)
        self.assertIn("district_powercut.yml/dispatches", gs)
        self.assertEqual(CODE.count("// ===== KOVAI JOBS TIMER (start)"), 1)
        self.assertIn("ScriptApp.newTrigger('startKovaiJobs').timeBased().everyMinutes(5)", CODE)


def run_blocks(text):
    """the shell scripts of a workflow file (run: | blocks and one-line run:), ${{ ... }} replaced - no YAML library needed"""
    lines, out = text.splitlines(), []
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*(?:- )?)run:\s*(.*)$", line)
        if not m:
            continue
        col, rest = len(m.group(1)), m.group(2)
        if rest.startswith("|"):
            body = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= col:
                    break
                body.append(nxt)
            src = "\n".join(body)
        else:
            src = rest
        out.append((i + 1, re.sub(r"\$\{\{.*?\}\}", "X", src)))
    return out


@unittest.skipUnless(shutil.which("bash"), "bash not installed")
class WorkflowShell(unittest.TestCase):
    def test_every_run_block_is_valid_shell(self):
        """14 Nov: a comment put after `then` on a one-line if swallowed the closing fi - the check job (and all posting) would fail"""
        for f in sorted(WF.glob("*.yml")):
            for line, src in run_blocks(f.read_text(encoding="utf-8")):
                r = subprocess.run(["bash", "-n"], input=src, capture_output=True, text=True, timeout=30)
                self.assertEqual(r.returncode, 0, f"{f.name} line {line}: {r.stderr[-300:]}")


class TimerRunNeedsLive(unittest.TestCase):
    def test_timer_post_run_needs_the_live_file(self):
        """a run started by the Google timer counts as scheduled: no LIVE file -> nothing posted (pick / powercut / manual runs: unchanged)"""
        code = """
import sys, pathlib, tempfile
sys.path.insert(0, 'poster')
import post
d = pathlib.Path(tempfile.mkdtemp()); post.ROOT = d; post.DRY = False; post.log = lambda *a, **k: None
a = post.live_allowed(); (d / 'LIVE').write_text('live'); print(a, post.live_allowed())"""
        res = {}
        for name, extra in (("timer", {"POST_TIMER": "1"}), ("manual", {"POST_TIMER": ""})):
            env = dict(os.environ, GITHUB_EVENT_NAME="workflow_dispatch", DRY_RUN="", **extra)
            r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr[-800:])
            res[name] = r.stdout.split()[-2:]
        self.assertEqual(res, {"timer": ["False", "True"], "manual": ["True", "True"]})


if __name__ == "__main__":
    unittest.main()
