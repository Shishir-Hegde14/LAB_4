# LAB 4 - Breakout Submission

Name: shishir  
SRN: PES1UG24CS438  
Section: 5H

## Repository Layout

This repository contains the completed LAB 4 submission files.

```text
.
+-- lab-4/
|   +-- breakout/              # Updated Breakout game code
+-- old breakout/
|   +-- README.md              # Original lab README
|   +-- breakout/              # Original buggy starter code
+-- LAB4_conversation_shishir.pdf
+-- 10-SEC-BUG_GAMEPLAY.mp4
+-- final_bug_fix_gameplay.mp4
+-- README.md                  # This submission summary
```

## What Was Implemented

### Task 1

- Fixed brick removal when the ball hits a brick.
- Kept the existing ball bounce mechanism unchanged.
- Added a simple particle effect when bricks break.

### Task 2

- Added a 3-life system.
- Added life display on screen.
- Reset the ball and paddle when a life is lost while preserving brick state.
- Added `YOU WIN` and `GAME OVER` screens.
- Added white `Restart Game` and `Quit` buttons.

### Task 3

- Added multiple brick types:
  - Red brick: breaks in 1 hit.
  - Moss brick: breaks in 3 hits.
  - Concrete brick: breaks in 5 hits and cracks more after each hit.
  - Metal brick: breaks in 6 hits, glows, and shakes the screen on hit.
  - Obsidian brick: unbreakable, purple glow, maximum 3 per game.
- Added type-specific hit and break particle effects.
- Randomized brick spawning while keeping normal bricks most common.

### Task 4

- Removed the `Bricks left` counter.
- Added a score system:
  - Red: 1 point
  - Moss: 3 points
  - Concrete: 5 points
  - Metal: 6 points
- Added improved score and lives HUD.
- Added final score display on win and game-over screens.
- Added combo scoring and visual effects:
  - `1X` yellow combo
  - `2X` red combo
  - `5X` violet/fire combo
- Added combo ball trails and paddle glow effects.
- Added screen shake during combo transitions.
- Combo resets when a life is lost.
- Combo degradation happens only when the ball bounces off the paddle/user bar.
- In `5X` combo, breaking the last breakable block triggers an explosion that removes all remaining blocks, including obsidian, before showing the win screen.

## How To Run Updated Game

```bash
cd lab-4/breakout
pip install -r requirements.txt
python main.py
```

Controls: Left and Right arrow keys move the paddle.

## Included Submission Files

- `LAB4_conversation_shishir.pdf`: exported LLM conversation.
- `10-SEC-BUG_GAMEPLAY.mp4`: gameplay video showing the old bug.
- `final_bug_fix_gameplay.mp4`: gameplay video showing the completed game.
