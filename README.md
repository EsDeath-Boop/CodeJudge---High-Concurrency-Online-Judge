# CodeJudge 🏆

High-concurrency online judge with full React frontend, competitive programming problems, and real-time verdicts.

**Stack:** React · Monaco Editor · FastAPI · Docker · Redis Streams · PostgreSQL · Nginx · AWS EC2

---

## What's Included

### Frontend (React)
| Page | Route | Description |
|---|---|---|
| Home | `/` | Landing page |
| Problems | `/problems` | Filterable problem list |
| Solver | `/problems/:slug` | Monaco editor + live verdict + mini leaderboard |
| Leaderboard | `/leaderboard` | Global rankings |
| Profile | `/profile` | Your stats + submission history |
| Login/Register | `/login` `/register` | Auth pages |

### Backend API
| Group | Endpoints |
|---|---|
| Auth | `POST /api/auth/register`, `POST /api/auth/login` |
| Problems | `GET /api/problems`, `GET /api/problems/:slug`, `POST /api/problems` |
| Submissions | `POST /api/submissions`, `GET /api/submissions/:id`, `WS /api/submissions/ws/:id` |
| Test Cases | `GET/POST /api/problems/:id/testcases`, `POST .../bulk` |
| Leaderboard | `GET /api/leaderboard/global`, `GET /api/leaderboard/problem/:id`, `GET /api/leaderboard/me` |

### Problems (8 seeded)
| # | Title | Difficulty |
|---|---|---|
| 1 | Two Sum | Easy |
| 2 | Valid Parentheses | Easy |
| 3 | Maximum Subarray | Easy |
| 4 | Longest Common Subsequence | Medium |
| 5 | Number of Islands | Medium |
| 6 | Merge Sorted Arrays | Medium |
| 7 | Shortest Path in Grid | Medium |
| 8 | Range Sum Query | Hard |

---

## Quick Start (Local)

### Prerequisites
- Docker Desktop
- Git

### 1. Clone and configure
```bash
git clone https://github.com/YOUR_USERNAME/codejudge.git
cd codejudge
cp .env.example .env
# Edit .env — set SECRET_KEY at minimum
```

### 2. Build sandbox images
```bash
docker build -t codejudge-cpp    ./sandbox/cpp
docker build -t codejudge-python ./sandbox/python
docker build -t codejudge-java   ./sandbox/java
```

### 3. Start everything
```bash
docker-compose up -d
```

### 4. Open the app
Visit **http://localhost** — the full React app loads immediately.

API docs at **http://localhost/docs** (via Swagger UI, proxied through frontend nginx).

---

## Project Structure

```
codejudge/
├── frontend/                   # React app
│   ├── src/
│   │   ├── api/client.js       # Axios API wrapper
│   │   ├── context/            # Auth context
│   │   ├── hooks/              # WebSocket hook
│   │   ├── components/         # Navbar, VerdictBadge, ProtectedRoute
│   │   └── pages/              # Home, Problems, Solver, Leaderboard, Profile
│   ├── Dockerfile              # Build React → serve with nginx
│   └── nginx.conf              # SPA routing + API proxy
├── api/                        # FastAPI backend
│   ├── core/                   # Config, DB, Redis, Auth
│   ├── models/                 # User, Problem, Submission, TestCase, Leaderboard
│   └── routes/                 # auth, problems, submissions, test_cases, leaderboard
├── worker/
│   ├── worker.py               # Redis Stream consumer
│   └── verdict_engine.py       # Docker sandbox executor
├── sandbox/
│   ├── cpp/                    # C++ judge image
│   ├── python/                 # Python judge image
│   └── java/                   # Java judge image
├── db/seeds/001_problems.sql   # 8 problems + test cases auto-seeded
├── nginx/nginx.conf            # Reverse proxy (used if running without frontend container)
├── infra/setup.sh              # EC2 one-shot bootstrap
├── .github/workflows/          # CI/CD auto-deploy
├── docker-compose.yml
└── .env.example
```

---

## AWS Deployment (Free Tier)

### Step 1 — Launch EC2 t2.micro
1. AWS Console → EC2 → Launch Instance
2. **Ubuntu Server 22.04 LTS**, instance type **t2.micro**
3. Create key pair → download `.pem`
4. Security Group: open ports `22` (your IP), `80`, `443`

### Step 2 — Launch RDS db.t3.micro
1. RDS → Create database → PostgreSQL 15 → Free tier
2. DB name: `codejudge`, username: `codejudge`, set password
3. Same VPC as EC2, Public access: No
4. Note the **endpoint URL**

### Step 3 — Bootstrap EC2
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
bash <(curl -s https://raw.githubusercontent.com/YOUR_USERNAME/codejudge/main/infra/setup.sh)
```

### Step 4 — Configure environment
```bash
nano /opt/codejudge/.env
```
Update:
```env
SECRET_KEY=<python3 -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=postgresql+asyncpg://codejudge:PASSWORD@RDS_ENDPOINT:5432/codejudge
DATABASE_URL_SYNC=postgresql://codejudge:PASSWORD@RDS_ENDPOINT:5432/codejudge
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

### Step 5 — Deploy
```bash
cd /opt/codejudge
docker build -t codejudge-cpp    ./sandbox/cpp
docker build -t codejudge-python ./sandbox/python
docker build -t codejudge-java   ./sandbox/java
docker-compose up -d
```

Visit **http://YOUR_EC2_IP** — done.

---

## CI/CD (GitHub Actions)

Add to GitHub → Settings → Secrets:

| Secret | Value |
|---|---|
| `EC2_HOST` | EC2 public IP |
| `EC2_SSH_KEY` | Contents of `.pem` file |

Every push to `main` auto-deploys.

---

## Adding Your Own Problems (Admin)

1. Register an account
2. Manually set `is_admin = true` in DB:
```sql
UPDATE users SET is_admin = true WHERE username = 'yourusername';
```
3. Use the API to create problems and upload test cases:
```bash
# Create problem
curl -X POST http://localhost/api/problems \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Problem","slug":"my-problem","description":"...","difficulty":"medium"}'

# Bulk upload test cases (JSON file)
curl -X POST http://localhost/api/problems/9/testcases/bulk \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@testcases.json"
```

Test case JSON format:
```json
[
  {"input": "5\n1 2 3 4 5\n", "output": "15\n", "is_sample": true},
  {"input": "3\n10 20 30\n", "output": "60\n", "is_sample": false}
]
```
