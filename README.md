# Autonomous Growth Engine

Autonomous organic growth marketing engine with dashboard, review queue, and scheduled content pipeline.

## What It Does

This plugin provides a WebUI dashboard and API for managing an autonomous organic growth marketing engine. The engine runs scheduled tasks that research, draft, and queue marketing content (blog posts, social media, Reddit posts, email newsletters, influencer outreach).

### Features

- **Dashboard view** showing pipeline stats, review queue, metrics, and action items
- **Review queue** where users can browse, read, approve, and move content to published
- **Settings panel** for configuring the engine (timezone, schedule times, paths)
- **Setup hook** that creates the directory structure on install
- **Sidebar button** for quick access

## Directory Structure

The engine manages content in the configured `growth_docs_path` (default: `docs/growth`):

```
docs/growth/
├── review/
│   ├── blog/          # Draft blog posts awaiting review
│   ├── social/        # Draft social media posts
│   ├── reddit/        # Draft Reddit/community posts
│   ├── email/         # Draft email newsletters
│   └── influencer/    # Draft influencer outreach messages
├── research/
│   ├── competitor-watch/
│   ├── trend-reports/
│   └── keyword-research/
├── pipeline/          # Approved content ready to publish
├── published/         # Published content archive
└── growth-dashboard.md  # Central tracking dashboard
```

## Usage

1. Click the **📈 Growth** button in the sidebar.
2. If not initialized, click **Initialize Now** to create the directory structure.
3. Configure schedule times and paths in **Settings → Agent → Autonomous Growth Engine**.
4. Use the dashboard to review, approve, and publish content.

## Configuration

Settings are managed per-project via the Settings UI:

| Setting | Default | Description |
|---|---|---|
| `growth_docs_path` | `docs/growth` | Relative path to growth content directory |
| `timezone` | User default timezone | IANA timezone for scheduled tasks |
| `monday_time` | `08:00` | Weekly research task time |
| `tuesday_time` | `09:00` | Weekly content creation time |
| `wednesday_time` | `09:00` | Weekly community engagement time |
| `thursday_time` | `09:00` | Weekly influencer pipeline time |
| `friday_time` | `09:00` | Weekly email newsletter time |
| `monthly_day` | `1` | Day of month for strategy review |
| `monthly_time` | `10:00` | Monthly review task time |

## API Endpoints

- `POST /api/plugins/autonomous_growth_engine/dashboard` — Dashboard stats, review queue, file operations
- `POST /api/plugins/autonomous_growth_engine/setup` — Setup status and initialization

## Related

- Skill: `autonomous-growth-engine` — methodology, task prompts, and playbook
- Dashboard template: `assets/dashboard-template.md` in the skill
