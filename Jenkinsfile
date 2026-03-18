pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "inventory"
    // macOS Jenkins (brew/launchd) often has a restricted PATH, so docker isn't found.
    // Include common Docker Desktop CLI locations (Intel + Apple Silicon).
    PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:${env.PATH}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Run (Docker)') {
      steps {
        sh 'docker compose -f docker-compose.yml -f docker-compose.ci.yml build --no-cache'
        sh 'docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d'
        sh '''
          set -e
          echo "Waiting for API to start..."
          for i in $(seq 1 60); do
            if curl -fsS http://localhost:8001/docs >/dev/null 2>&1; then
              echo "API is up."
              exit 0
            fi
            sleep 2
          done
          echo "API did not start in time" >&2
          docker compose -f docker-compose.yml -f docker-compose.ci.yml logs api || true
          exit 1
        '''
      }
    }

    stage('Load CSV into MongoDB') {
      steps {
        sh 'docker compose -f docker-compose.yml -f docker-compose.ci.yml exec -T api python3 scripts/import_csv.py --csv data/products.csv --mongo-uri mongodb://mongo:27017 --db inventory --collection products'
      }
    }

    stage('Run Postman/Newman tests') {
      steps {
        sh '''
          docker run --rm --network ${COMPOSE_PROJECT_NAME}_default \
            -v "$WORKSPACE/postman:/etc/newman" \
            postman/newman:latest \
            run /etc/newman/inventory-api.postman_collection.json \
            --env-var baseUrl=http://api:8000
        '''
      }
    }

    stage('Generate README.txt') {
      steps {
        sh 'docker compose -f docker-compose.yml -f docker-compose.ci.yml exec -T api python3 scripts/generate_readme.py > README.txt'
      }
    }

    stage('Package zip artifact') {
      steps {
        sh '''
python3 - <<'PY'
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import zipfile

ts = datetime.now().strftime("%Y%m%d-%H%M%S")
out = Path(f"complete-{ts}.zip")
include = [
  "app",
  "scripts",
  "data",
  "postman",
  "tests",
  "monitoring",
  "Dockerfile",
  "docker-compose.yml",
  "docker-compose.dev.yml",
  "docker-compose.monitoring.yml",
  "docker-compose.ci.yml",
  "requirements.txt",
  ".env.example",
  "Jenkinsfile",
  "README.txt",
]

with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
  for item in include:
    p = Path(item)
    if p.is_dir():
      for fp in p.rglob("*"):
        if fp.is_file():
          z.write(fp, fp.as_posix())
    elif p.is_file():
      z.write(p, p.as_posix())

print(out)
PY
        '''
        archiveArtifacts artifacts: 'complete-*.zip', fingerprint: true
        archiveArtifacts artifacts: 'README.txt', fingerprint: true
      }
    }
  }

  post {
    always {
      sh 'docker compose -f docker-compose.yml -f docker-compose.ci.yml down -v || true'
    }
  }
}

