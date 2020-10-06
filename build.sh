
HASH=`git rev-parse --short HEAD`
TAG=sitesearch-app:$HASH
IMAGE="gcr.io/redislabs-university/$TAG"

echo "Building $IMAGE..."
docker build -t $TAG --build-arg "REDIS_PASSWORD=$REDIS_PASSWORD" .
