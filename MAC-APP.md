# Yes, Chef on your own computer

A small local focus tool: a ticket rail of everything in flight, focus sessions (timed burst or open), an optional yes/no check on what you're avoiding (your phone, by default), and points you spend in your own reward shop.

## Run it

- **Easiest:** double-click `start.command`. It starts the app and opens http://localhost:4747. Keep the Terminal window open while you use it.
- **From Terminal:** `cd` into this folder, run `node server.js`, then open http://localhost:4747.
- Pin the tab so it's always one click away.

The first time you double-click `start.command`, macOS may block it. Right-click it, choose Open, then Open again. If it says it isn't executable, run `chmod +x start.command` once.

**Test copy:** double-click `start-test.command` to open a throwaway copy at http://localhost:4748. It starts from a brand-new board every time, so you can run through the walkthrough or try things out. It can run alongside your normal one, and it never touches your real `data.json`. Its scratch data lives in the `test-run` folder and is wiped each time you start it. (Settings shows which data file a tab is using, if you lose track.)

Needs Node.js 18 or newer. There's nothing to install: no packages, no build step.

## Your data

- Everything is saved to `data.json` in this folder. It's the single source of truth.
- A dated copy goes in `backups/` once a day, the first time you save that day.
- Nothing leaves your computer. The server only listens on this machine.
- If the page can't reach the server, it saves in the browser instead and shows a yellow notice.

## Using it

**First time?** A brand-new board opens with a one-screen **quick start**, all optional: pick what the end-of-session question asks (phone, games, getting up, your own, or don't ask), and rename, reprice or drop the starter rewards. **Skip, keep the defaults** works too. Then the board starts with a few practice slips, showing what the board looks like mid-shift: one ready to start, one on hold that comes back while you watch, a personal one, and one already on the spike. They come with a little work history so they look like a real shift. That practice history never counts toward your points, streak, today line or shift totals. Five short tips point out each part: the rail, hold, the spike, points and rewards, and adding your own. If you click into something along the way (a slip, a session, the check, the results, the spike), a short tip follows you there, and the walkthrough picks up where you left off when you're back on the rail. The spike step has **See an example**, which shows a sample shift report so you know what End shift gives you before you use it. The sample saves nothing. The last tip has **Clear practice tickets**, and until you clear them a reminder sits under the rail. Clearing removes the practice slips and any sessions you ran on them (with Undo). To see it again any time: **Settings → Show the walkthrough again**. That adds the practice slips back next to your real ones.

1. **Add** a ticket: type a name, pick a type (task, AI job, render, delivery, person) and an area (work or personal), then press Enter. Press `n` anywhere to jump to the add box.
2. **Hold:** waiting on something (an AI job, a render, a reply)? Tap Hold. The slip dims and counts down from 2 minutes. When time's up it comes back on its own with a yellow **Off hold** tag, moves to the front, and chimes. Tap End hold to bring it back early.
3. **Order:** left is the front of the line. The latest thing that happened goes to the front: starting a session on a slip, or a slip coming off hold. The worked slip stays at the front afterward, and the rail slides back to the left so you can see it. New tickets join at the right end. You can still drag a ticket anywhere, or focus it and press Alt with the left or right arrow.
4. **Filter** the rail to All, Work or Personal.
5. **Spike it** when a ticket is finished. Open any slip and press **Spike it**, or use the button on the results screen after a session. It lands on the spike in the bottom-right corner. Nothing is thrown away. Click the spike to fan out the stack, click a slip to review it, and use **Put back on the rail** if it wasn't really done. Undo stays up for 30 seconds after you spike something. When you're wrapping up, open the spike and press **End shift**: you get a receipt-style shift report. It breaks the time down by ticket (time, points, sessions and share of the shift, with a check mark on the ones you spiked), then totals tickets spiked, sessions, time worked, clean sessions and points, and the spike is cleared. Cleared tickets are archived under that shift, never deleted. Undo is there for 30 seconds. End shift is manual unless you turn on **Settings → End shift → Automatically on a new day**. Then the first time you open Yes, Chef on a new day, the previous shift is filed for you, and a notice with **View** shows its report. The day turns over at 4 AM, so late nights count as the day before. It never ends a shift in the middle of a session, and it leaves walkthrough practice slips alone. **Past shifts** (in the spike) lists every shift you've ended, newest first. Click one to see its full report again.
6. **Start** a ticket, then pick a burst length (10, 15, 25, 45, or type your own) or "Open, no timer." The slip stays on screen with the clock beside it. Jot where you are in the note on the slip any time, and it saves as you type. On a timed burst, the slip's dashed tear line fills in as time runs.
7. When it ends, answer the check. By default it's **Did you use your phone?** Points are based on the minutes you worked. No earns the full amount, and Yes takes off the cut. In Settings you can switch the question to games, getting up from the computer, or your own question, or turn the check off so sessions just log their time at full points. If you forgot to stop an open session, lower the minutes before you answer. Every session is saved, however short (only accidental starts of a few seconds are dropped). Sessions shorter than the hide setting (2 minutes by default) skip the check and are hidden: no points, no history, no effect on your streak, until you lower the setting.
8. **Rewards** are milestones (new boards start with a 15-minute break every 150 (30 min of work), a Coffee run every 900 (3 hr, about a good day) and Dinner out every 4,800 (16 hr, about a week)), not purchases. Points are a running total that only goes up. Each reward repeats on its own mark: a break set to every 150 points can be claimed at 150, 300, 450 and so on, while Dinner out at 4,800 keeps building in the background. Claiming never takes points away. When something is ready, the Rewards button shows a small badge with how many you can claim. Claim them in Rewards (with a 30-second Undo). To make points mean something, Rewards shows each one in time too: at 5 points a minute, a 900-point coffee run is 3 hr of focused work. The same conversion shows how much work is left to the next mark, and appears as you type a reward's points (in Rewards and the quick start).

## Using it on more than one device

This Mac app keeps its data in `data.json` in this folder, and only this Mac can see it. To share your tickets with a Chromebook or another computer, use the **browser-only version** (`Yes Chef Browser/yes-chef.html`) on every device, including this Mac in Chrome, with its data file kept in Google Drive. Its README walks through the setup and the one rule: one device at a time.

To bring your existing tickets along, copy this folder's `data.json` into your Google Drive folder in Finder (you can rename the copy to `yes-chef-data.json`). Then choose **Open an existing file** in the browser version and pick the copy in Drive. Use the copy, not the original, so the Mac app and the browser version never write to the same file.

## Backups and moving your data

**Settings → Your data** has two buttons:
- **Export data** downloads your whole board as a `.json` backup file.
- **Import data** replaces your board with a backup, or with a data file from another device (a phone, a Chromebook, or this folder's `data.json`). It shows what's in the file and what's on your board now before anything changes, offers to download a copy of your current board first, and has a 30-second Undo. Files from older versions of Yes, Chef are converted automatically.

## Settings (defaults, all changeable)

- Points per minute worked: 5 (a 15-minute burst earns 75, a 45-minute one earns 225)
- After each session, ask: Did you use your phone? (or games, getting up, your own question, or don't ask)
- A Yes costs: 20% (raise toward 50% as it gets easier)
- Hide sessions shorter than: 2 minutes (0 counts everything). Short sessions are always saved, so lowering it brings them back. **Delete them** removes hidden ones for good (with Undo).
- Hold length: 2 minutes
- Default burst: 15 minutes
- Chime halfway and at the end of a burst
- Optional desktop notification when a burst ends
- End shift: only when you press it (or automatically on a new day)
- Theme: match system, light or dark

## Data format and upgrades

Every data file records a `version`. New features normally just add a field with a default, so older files keep opening as they are. When the format ever has to change in a bigger way, the app gets a conversion step for each version. Opening an older file runs the steps it needs, in order, and saves it in the new format. Before the first save in a newer format, the original is kept: the Mac app writes `backups/data-v<old>-<date>.json`, and the browser version keeps a copy inside the browser.

Before shipping a build, `node tests/check-data.js` opens every sample file in `tests/fixtures` and checks that nothing is lost (it needs Playwright). When a new data version ships, add a sample file of the version before it.

## Files

- `public/logo.svg`: the Yes, Chef wordmark as an SVG (text turned into shapes, so it needs no font)

- `server.js`: tiny Node server, no dependencies
- `tests/`: sample data files from each version, and the check that opens them
- `public/index.html`: the whole app
- `start.command`: double-click launcher for macOS
- `data.json`: your data (created on first save)

## Support

Yes, Chef is free. If it helps you focus, you can [buy me a coffee](https://buymeacoffee.com/kkubesh). There's a link at the bottom of Settings too.
