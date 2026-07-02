---
name: ssh-backend-agent-temp
description: Connect to the temporary Laravel backend environment over SSH and coordinate with the remote backend Codex agent. Use when a task needs backend Laravel inspection, implementation, verification, or discussion via ubuntu@162.19.229.31 in /home/ubuntu/dev-sandbox, especially for Hades backend API, migrations, tests, Docker Compose, or running codex resume --last --yolo remotely.
---

# SSH Backend Agent Temp

## Quick Command

Open the remote backend Codex agent session:

```bash
ssh -tt ubuntu@162.19.229.31 'cd /home/ubuntu/dev-sandbox && codex resume --last --yolo'
```

Equivalent helper from this skill:

```bash
/Users/gabriele/.codex/skills/ssh-backend-agent-temp/scripts/connect-backend-agent.sh
```

## Workflow

1. Announce that you are connecting to the temporary Laravel backend over SSH.
2. Use the interactive Codex command above when you need to ask or educate the backend agent.
3. For direct backend inspection or commands, use non-interactive SSH from the repo root:

```bash
ssh ubuntu@162.19.229.31 'cd /home/ubuntu/dev-sandbox/backend && <command>'
```

4. Keep remote code edits scoped. If applying a patch remotely, run it from `/home/ubuntu/dev-sandbox` with repository-relative paths such as `backend/routes/api.php`.
5. Record decisions, answers, and implementation results in the local coordination document when working from the Hades repo:

```text
docs/backend-agent-coordination.md
```

If the remote backend repo needs its own trace, write a concise report under:

```text
ai-sandbox/docs/
```

## Remote Context

- SSH host: `ubuntu@162.19.229.31`
- Remote workspace: `/home/ubuntu/dev-sandbox`
- Laravel backend: `/home/ubuntu/dev-sandbox/backend`
- Public API base used in prior Hades work: `https://home-sweet-home.cloud`
- Docker Compose file for backend commands: `/home/ubuntu/dev-sandbox/docker-compose.devboard.yaml`

## Common Commands

List Hades routes:

```bash
ssh ubuntu@162.19.229.31 'cd /home/ubuntu/dev-sandbox && docker compose -f docker-compose.devboard.yaml exec -T app sh -lc "php artisan route:list --path=hades"'
```

Run Hades feature tests:

```bash
ssh ubuntu@162.19.229.31 'cd /home/ubuntu/dev-sandbox && docker compose -f docker-compose.devboard.yaml exec -T app sh -lc "APP_ENV=testing DB_CONNECTION=sqlite DB_DATABASE=:memory: DB_URL= php artisan test tests/Feature/Hades"'
```

Run Hades plus plugin auth regression:

```bash
ssh ubuntu@162.19.229.31 'cd /home/ubuntu/dev-sandbox && docker compose -f docker-compose.devboard.yaml exec -T app sh -lc "APP_ENV=testing DB_CONNECTION=sqlite DB_DATABASE=:memory: DB_URL= php artisan test tests/Feature/Hades tests/Feature/PluginAuthTest.php"'
```

Apply runtime migrations:

```bash
ssh ubuntu@162.19.229.31 'cd /home/ubuntu/dev-sandbox && docker compose -f docker-compose.devboard.yaml exec -T app sh -lc "php artisan migrate --force"'
```

Smoke public health:

```bash
curl -sS -i https://home-sweet-home.cloud/api/hades/v1/health | sed -n '1,20p'
```

## Guardrails

- Do not paste or print live tokens unless unavoidable; redact them in user-facing output.
- Prefer temporary `HERMES_HOME` values for local-to-remote smoke tests.
- Revoke temporary backend bootstrap or agent tokens created for tests.
- Do not run destructive remote commands unless the user explicitly asked for them.
- If the interactive backend agent stalls in `Working` without producing useful changes, interrupt it, continue with direct SSH implementation if appropriate, and record the outcome.
- Before claiming completion, verify with fresh command output: tests, route list, migrations or public smoke as relevant.
