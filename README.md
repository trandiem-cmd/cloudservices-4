### WEEK 4 ASSIGNMENT
## Deployment

The application is deployed on Rahti/OpenShift using Kubernetes resources.

It consists of three main components:

* **Frontend:** Nginx serving the web interface.
* **Backend:** Flask API running on port 8000.
* **Database:** MySQL running on port 3306 with persistent storage.

The frontend communicates with the backend through the `backend` Service, while the backend connects to MySQL through the `db` Service.

### Useful Commands

```bash
# Check application Pods
oc get pods

# Check Services
oc get svc

# Check public Routes
oc get route

# Check persistent storage
oc get pvc

# Scale the backend
oc scale deployment/backend --replicas=3

# Return backend to one replica
oc scale deployment/backend --replicas=1
```

The MySQL database uses the `mysql-data` PersistentVolumeClaim, so database data remains available when the MySQL Pod is replaced.
## Deployment Steps

1. Create the ConfigMap and Secret:

```bash
oc apply -f configmap.yaml
oc apply -f secret.yaml
```

2. Create the persistent storage for MySQL:

```bash
oc apply -f mysql-pvc.yaml
```

3. Deploy MySQL:

```bash
oc apply -f mysql-deployment.yaml
oc apply -f mysql-service.yaml
```

4. Deploy the Flask backend:

```bash
oc apply -f backend-deployment.yaml
oc apply -f backend-service.yaml
```

5. Deploy the Nginx frontend:

```bash
oc apply -f frontend-deployment.yaml
oc apply -f frontend-service.yaml
```

6. Create the frontend Route:

```bash
oc create route edge frontend --service=frontend
```

7. Verify the deployment:

```bash
oc get pods
oc get svc
oc get route
oc get pvc
```

8. Open the URL shown by `oc get route` to access the application.

The deployment creates the frontend, backend, and MySQL components, connects them through Kubernetes Services, and uses a PVC to provide persistent database storage.

### WEEK 5 ASSIGNMENT - Adding Redis Cache
This week, the project from the previous assignment was extended by adding Redis as a caching layer. The existing Flask backend, MySQL database, and frontend were kept as the foundation, while Redis was deployed as an additional service in OpenShift (Rahti).

The purpose of this assignment is to demonstrate how Redis can be integrated with a backend application and how its behavior differs from persistent data storage in MySQL.
1. Deploy Redis

Redis was deployed to OpenShift using a Deployment and a Service.
```bash
oc apply -f rahti/redis-deployment.yaml
oc apply -f rahti/redis-service.yaml
```
The Deployment manages the Redis container, while the Service provides a stable hostname and port for the backend to connect to Redis.

Redis is available internally through:

cache:6379
2. Update the Backend

The Flask backend was updated to connect to Redis using the Redis Python client.
```bash
r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "cache"),
    port=6379,
    decode_responses=True
)
```
A new endpoint was added:
```bash
@app.get('/api/view')
def view():
    count = r.incr('view_count')
    return jsonify(view=count)
```
Each request increments the view_count value stored in Redis.

3. Build and Deploy the Updated Backend

After modifying the backend, a new Docker image was built and pushed to Docker Hub.

docker build -f backend/Dockerfile -t diemtran1993/lemp-backend:<version> .
docker push diemtran1993/lemp-backend:<version>

The OpenShift Deployment was then updated to use the new backend image.

oc set image deployment/backend backend=diemtran1993/lemp-backend:<version>

The deployment was verified with:

oc rollout status deployment/backend
4. Test Redis

Redis was tested directly using redis-cli:

oc exec -it <redis-pod> -- redis-cli INCR view_count

The counter increases with each request:

(integer) 1
(integer) 2
(integer) 3

The backend endpoint was also tested:

GET /api/view

Example response:

{
  "view": 1
}

Calling the endpoint again increases the Redis counter.

5. Compare Redis and MySQL

The existing MySQL-based endpoint was kept:

```bash
POST /api/views
```
This endpoint updates the persistent page_views table in MySQL.

The new Redis endpoint is:
```bash
GET /api/view
```
This endpoint increments the view_count key in Redis.

Therefore, the two counters are independent:

MySQL:
page_views.views
    ↓
Persistent database value

Redis:
view_count
    ↓
Fast in-memory counter/cache

Testing both endpoints demonstrates that Redis and MySQL can be used for different purposes in the same backend application.

6. Frontend

A new frontend version was created to display the updated functionality while keeping the backend, MySQL, and Redis services unchanged.

The frontend was built as a Docker image, pushed to Docker Hub, and deployed to OpenShift with its own Service and Route.
```bash
docker build -f frontend/Dockerfile -t diemtran1993/lemp-frontend:<version> .
docker push diemtran1993/lemp-frontend:<version>
```
The frontend was then exposed through an OpenShift Route.
```bash
oc create route edge frontend-new --service=frontend-new
```
Result

The Week 5 project extends the previous application with Redis without replacing the existing MySQL database.

The final application demonstrates:

Flask backend running in a container
MySQL for persistent data storage
Redis for fast in-memory data handling
Frontend deployed separately
Communication between services through OpenShift Services
External access through an OpenShift Route
Docker images stored in Docker Hub
Redis and MySQL providing independent counters
Conclusion

The assignment demonstrates how Redis can be integrated into an existing containerized application as a fast data store/cache. MySQL remains responsible for persistent application data, while Redis provides a separate mechanism for fast-changing data such as counters and cache entries.