# Utiliza la imagen base de Redis desde Docker Hub
FROM redis:alpine

# Copia el archivo de configuración personalizado
COPY redis.conf /usr/local/etc/redis/redis.conf

# Exponer el puerto por defecto de Redis (6379)
EXPOSE 6379

# Comando por defecto para iniciar el servidor Redis
#CMD ["redis-server --bind 0.0.0.0"]

