### **1️⃣ CMD vs Docker Compose `command` conflict**

* Your `Dockerfile` had:

  ```dockerfile
  CMD ["python", "main.py"]
  ```
* Your Compose service had:

  ```yaml
  command: uvicorn src.main:app --host 0.0.0.0 --port 8888 --reload
  ```
* **Problem:** CMD in Dockerfile is overridden by Compose `command`. Not really an error, but caused confusion about what actually runs in the container.

---

### **2️⃣ Network alias issue**

* Error:

  ```
  invalid config for network bridge: network-scoped alias is supported only for containers in user defined networks
  ```
* **Cause:** You were trying to use a network alias without properly defining a **user-defined network**.
* **Resolution:** You created `balagh_network` (user-defined) and attached containers to it.

---

### **3️⃣ Celery module not found (`ModuleNotFoundError`)**

* Errors in `fetch_lectures_beat` and `pipeline_worker`:

  ```
  ModuleNotFoundError: No module named 'src'
  ```
* **Cause:** The Celery worker/beat container could not find your app code (`src` folder) because:

  * The Dockerfile or mounted volume didn’t include it.
  * PYTHONPATH was not set, so Python couldn’t locate `src`.
* **Resolution:** Ensure code is copied into container (`COPY . .`) and/or mount volumes and set `PYTHONPATH`.

---

### **4️⃣ Flower container issues**

* Errors:

  ```
  ModuleNotFoundError: No module named 'src'
  You have incorrectly specified the following celery arguments after flower command: ['--broker'].
  ```
* **Cause:**

  * Flower image did not include your app code.
  * Flower requires the Celery app to exist to connect to broker.
  * Arguments were given in wrong order (`flower --broker` instead of `celery flower --broker` in some cases).
* **Resolution:** Build Flower from your app image or mount code with `PYTHONPATH` set. Ensure `-A src.celery_app` points to the app.

---

### **5️⃣ Superuser warning**

* Warning in worker logs:

  ```
  You're running the worker with superuser privileges: this is absolutely not recommended!
  ```
* **Cause:** Celery worker is running as root inside container.
* **Resolution:** Optionally run as non-root using `--uid` or `USER` in Dockerfile.

---

### **6️⃣ Docker build/export errors**

* Errors like:

  ```
  failed to prepare extraction snapshot: parent snapshot sha256:... does not exist
  ```
* **Cause:** Docker build cache or layers issue (possibly from large context or interrupted build).
* **Resolution:** Clean Docker system (`docker system prune -a`) and rebuild images.

---

### **7️⃣ Large image sizes (~477MB each)**

* Cause: All services use the **same Python slim base** and include all dependencies + full code.
* Resolution: Can reduce size by:

  * Using multi-stage builds.
  * Installing only necessary dependencies.
  * Avoid copying unnecessary files.

---

### **8️⃣ Celery deprecation warnings**

* Warnings:

  ```
  The 'CELERY_TIMEZONE', 'CELERY_ROUTES', 'CELERY_RESULT_BACKEND', 'CELERY_QUEUES' settings are deprecated
  ```
* **Cause:** Using old Celery configuration format.
* **Resolution:** Update to Celery 5+ recommended settings:

  ```python
  timezone = "UTC"
  task_routes = {...}
  result_backend = "mongodb://..."
  task_queues = [...]
  ```

---

✅ **Summary:** Most critical errors were:

1. **ModuleNotFoundError for `src`** — Celery and Flower couldn’t find your code.
2. **Flower misconfiguration** — arguments/order and missing app code.
3. **Docker build/export errors** — large context and cache issues.

Other issues were warnings or configuration nuances.
