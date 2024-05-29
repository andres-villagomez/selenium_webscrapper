docker pull selenium/standalone-chrome
#docker image tag selenium/standalone-chrome us.gcr.io/<PROJECT_NAME>/<SELENIUM_IMAGE_NAME>
docker image tag selenium/standalone-chrome gcr.io/selenium_image
#docker push us.gcr.io/<PROJECT_NAME>/<SELENIUM_IMAGE_NAME>
docker push gcr.io/selenium_image

#gcloud run deploy <SELENIUM_SERVICE_NAME> \
#	--image us.gcr.io/<PROJECT_NAME>/<SELENIUM_IMAGE_NAME> \
#    --port 4444 \
#    --memory 2G
#    --region us-west1
gcloud run deploy selenium-service-webscraper --region us-west1 --image gcr.io/selenium_image --port 4444 --memory 2G

#gcloud iam service-accounts create <INVOKING_SERVICE_ACCOUNT> 
#	--description "This service accounts invokes Selenium on Google Cloud Run." 
#    --display-name "Selenium Invoker"

gcloud iam service-accounts create selenium-service-account --description "This service accounts invokes Selenium on Google Cloud Run." --display-name "Selenium Invoker"

#gcloud run services add-iam-policy-binding <SERVICE_NAME>  \
#    --member serviceAccount:<INVOKING_SERVICE_ACCOUNT>@iam.gserviceaccount.com \
#    --role roles/run.invoker
#    --region us-west1

gcloud run services add-iam-policy-binding selenium-service-webscraper --member serviceAccount:selenium-service-account@iam.gserviceaccount.com --role roles/run.invoker --region us-west1

