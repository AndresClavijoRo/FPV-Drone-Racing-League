# Cloud setup

gcloud auth configure-docker us-central1-docker.pkg.dev

docker compose -f docker-compose.yaml  build 

docker tag entrega4-app  us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/backend5

docker push us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/backend5



gcloud run deploy backend5 \
--image=us-central1-docker.pkg.dev/elated-coil-323901/vinilos-app/backend5@sha256:8b2807e713dc83abdd18d221b5c374c47d5007fb3b43c9af498ed2dde8fccfc4 \
--allow-unauthenticated \
--port=8080 \
--service-account=429089580341-compute@developer.gserviceaccount.com \
--max-instances=10 \
--region=us-central1 \
--project=elated-coil-323901