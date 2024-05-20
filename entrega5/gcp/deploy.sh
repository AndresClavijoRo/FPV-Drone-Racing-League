# Cloud setup

gcloud auth configure-docker us-central1-docker.pkg.dev


docker build -t backend .
docker tag backend us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/backedn5
docker push us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/backedn5


gcloud run deploy backend5 \
--image=us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/backedn5 \
--allow-unauthenticated \
--port=8080 \
--service-account=429089580341-compute@developer.gserviceaccount.com \
--max-instances=10 \
--region=us-central1 \
--project=elated-coil-323901


