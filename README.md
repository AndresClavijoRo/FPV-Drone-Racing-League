# FPV-Drone-Racing-League
Aplicacion de misw4204 desarrollo-de-sw-en-la-nube

## Ejecución Entrega 01
Para ejecutar el programa usar 
```docker compose up```

Esto expondra la aplicación en el puerto `8080`, 

## Documentación API
la documentación la encuentra en [Postman](https://documenter.getpostman.com/view/11604273/2sA3BhfvA3)


## Ejecución Entrega 02

Correr el servicio web
```sudo docker compose -f docker-compose-web-server.yaml  up --build```

Correr el worker
```sudo docker compose -f worker-docker-compose.yml  up --build```

Correr pruebas de esters para el wroker
```sudo docker compose -f worker-load-tests.yml  up --build```
