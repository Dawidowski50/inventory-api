pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "inventory"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Run (Docker)') {
      steps {
        sh 'docker compose build --no-cache'
        sh 'docker compose up -d'
        sh '''
          set -e
          echo "Waiting for API to start..."
          for i in $(seq 1 60); do
            if curl -fsS http://localhost:8000/docs >/dev/null 2>&1; then
              echo "API is up."
              exit 0
            fi
            sleep 2
          done
          echo "API did not start in time" >&2
          docker compose logs api || true
          exit 1
        '''
      }
    }

    stage('Load CSV into MongoDB') {
      steps {
        sh 'docker compose exec -T api python3 scripts/import_csv.py --csv data/products.csv --mongo-uri mongodb://mongo:27017 --db inventory --collection products'
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
        sh 'docker compose exec -T api python3 scripts/generate_readme.py > README.txt'
      }
    }

    stage('Package zip artifact') {
      steps {
        sh '''
          python3 - <<'PY'
          from __future__ import annotations
          import os
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
            "docker-compose.monitoring.yml",
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
      sh 'docker compose down -v || true'
    }
  }
}

