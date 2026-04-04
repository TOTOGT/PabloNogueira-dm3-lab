# Teacher Setup Guide — GitHub Classroom for Book 3

This guide walks you through the **exact steps** to configure GitHub Classroom for three assignment types (Individual, Pairs, Groups) using a single starter template.

---

## Prerequisites

- [ ] You have a GitHub account that is an **Owner** of the `TOTOGT` organization.
- [ ] The `TOTOGT/book3-starter` repo exists and is marked as a **Template Repository** (see Step 1).
- [ ] You have access to [classroom.github.com](https://classroom.github.com).

---

## Step 1 — Mark the Template Repo

1. Go to **https://github.com/TOTOGT/book3-starter**
2. Click **Settings** (top tab row).
3. Under **General → Template repository**, check ✅ the box.
4. Click **Save**.

> ⚠️ If the repo doesn't exist yet: create a new repo named `book3-starter` under the `TOTOGT` org, then copy the contents of this `book3-starter/` folder into its root, push, and mark it as a template.

---

## Step 2 — Create or Open Your Classroom

1. Go to [https://classroom.github.com](https://classroom.github.com).
2. Click **Sign in with GitHub** if prompted.
3. You should see your classrooms. If you already have one for `TOTOGT`, click it.  
   If not: click **New classroom** → select the `TOTOGT` organization → name it (e.g., `Book 3 – 2026`).

---

## Step 3 — Create Assignment 1: Individual

1. Inside your classroom, click **New assignment**.
2. Fill in:
   | Field | Value |
   |---|---|
   | Title | `Book 3 – Individual Assignment` |
   | Deadline | *(set as needed)* |
   | Repository visibility | **Private** |
   | Assignment type | **Individual** |
   | Template repository | `TOTOGT/book3-starter` |
   | Repository prefix | `book3-individual-` |
3. Under **Grading and feedback** → optionally enable **Autograding** (uses `.github/workflows/autograding.yml`).
4. Click **Create assignment**.
5. **Copy the invite link** — this is what you share with individual-track students.

---

## Step 4 — Create Assignment 2: Pairs

1. Click **New assignment**.
2. Fill in:
   | Field | Value |
   |---|---|
   | Title | `Book 3 – Pair Assignment` |
   | Deadline | *(set as needed)* |
   | Repository visibility | **Private** |
   | Assignment type | **Group assignment** |
   | Max members per group | **2** |
   | Group set name | `pairs` *(creates a new group set — students self-assign into pairs)* |
   | Template repository | `TOTOGT/book3-starter` |
   | Repository prefix | `book3-pair-` |
3. Click **Create assignment**.
4. **Copy the invite link** — share with pair-track students.

> **How students pair up:** The first student to click the link creates the group and chooses a name. The second student clicks the same link and joins the existing group. GitHub Classroom enforces the max-2 limit automatically.

---

## Step 5 — Create Assignment 3: Groups/Teams

1. Click **New assignment**.
2. Fill in:
   | Field | Value |
   |---|---|
   | Title | `Book 3 – Group Assignment` |
   | Deadline | *(set as needed)* |
   | Repository visibility | **Private** |
   | Assignment type | **Group assignment** |
   | Max members per group | **4** *(or 5 — your choice)* |
   | Group set name | `groups` *(new group set)* |
   | Template repository | `TOTOGT/book3-starter` |
   | Repository prefix | `book3-group-` |
3. Click **Create assignment**.
4. **Copy the invite link** — share with group-track students.

---

## Step 6 — Share Links with Students

You now have **three invite links**. Share the correct one with each cohort:

| Cohort | Link to share |
|---|---|
| Working individually | Individual assignment invite link |
| Working in pairs | Pair assignment invite link |
| Working in teams of 3–5 | Group assignment invite link |

You can share via email, LMS (Canvas/Moodle/Blackboard), or directly in Slack/Teams.

---

## What Students Will See

1. They click the link.
2. GitHub asks them to sign in (or creates an account).
3. Classroom shows: *"Your assignment repo is being created…"*
4. In ~30 seconds: their private repo appears, pre-loaded with all starter files.
5. They open Codespaces or clone and start working.
6. They submit by pushing commits — no email, no manual steps.

---

## Monitoring Student Progress

From your classroom dashboard at [classroom.github.com](https://classroom.github.com):
- Click an assignment to see **all student repos** and their last push timestamp.
- Click any repo to open it directly.
- If autograding is on, you'll see pass/fail status per student.

---

## Resetting or Reusing for Next Semester

- To reuse, simply create **new assignments** pointing at the same `TOTOGT/book3-starter` template.
- Update assignment prompts by editing the files in `book3-starter` and pushing (new repos generated from the template will get the update; existing student repos are not affected).

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Students can't find their repo | Ask them to go to github.com and check their repositories list |
| Classroom says "template not found" | Make sure `book3-starter` is marked as Template Repository (Step 1) |
| Student accidentally left a group | Teacher can manage groups from the classroom dashboard |
| Autograding fails on every push | Check `.github/workflows/autograding.yml` — the `continue-on-error: true` flag on the self-test step means partial implementations won't block the run |

---

*Teacher Setup Guide v1.0 · TOTOGT · 2026*
