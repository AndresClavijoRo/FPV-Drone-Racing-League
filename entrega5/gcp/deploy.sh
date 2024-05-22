# Cloud setup

gcloud auth configure-docker us-central1-docker.pkg.dev


docker build -t backend .
docker tag backend us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/backedn5
docker push us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/backedn5


docker build -t worker -f Dockerfile.worker .
docker tag worker us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/worker5
docker push us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/worker5


gcloud run deploy backend5 \
--image=us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/backedn5 \
--allow-unauthenticated \
--port=8080 \
--service-account=429089580341-compute@developer.gserviceaccount.com \
--max-instances=10 \
--region=us-central1 \
--project=elated-coil-323901 \
--memory=2Gi \
--concurrency=200 

https://backend5-jui7h7vh3a-uc.a.run.app/

gcloud run deploy worker \
--image=us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/worker5 \
--no-allow-unauthenticated \
--port=8080 \
--service-account=429089580341-compute@developer.gserviceaccount.com \
--min-instances=1 \
--max-instances=10 \
--no-cpu-throttling \
--region=us-central1 \
--project=elated-coil-323901 \
--memory=2Gi \
--concurrency=1 

https://worker-jui7h7vh3a-uc.a.run.app
