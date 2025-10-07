# 🚀 ¡Bienvenido al Repositorio del Hackathon! 🚀

Este es nuestro espacio de trabajo para el análisis de datos de Sonora. Para mantener el orden y evitar desastres 💥, seguiremos un flujo de trabajo simple usando **branches**.

## ✨ Lineamientos para Contribuir ✨

La regla de oro: **NUNCA trabajes directamente sobre la rama `main`**. La rama `main` es nuestra versión "estable" y funcional.

### Paso 1: Crea tu Propia Rama (Branch) 🌿

Antes de escribir una sola línea de código, crea una rama personal para trabajar en tu nueva funcionalidad o corrección.

1.  **Asegúrate de tener la última versión del código:**
    ```bash
    git checkout main
    git pull origin main
    ```

2.  **Crea y múevete a tu nueva rama.** Nómbrala de forma descriptiva, usando `tu-nombre/lo-que-vas-a-hacer`.
    ```bash
    # Ejemplo:
    git checkout -b geosal/agregar-mapa-interactivo
    ```

### Paso 2: Haz tu Magia (¡Programa!) 💻

Ahora estás en tu propia "caja de arena". Trabaja en el notebook, crea tus visualizaciones, entrena tu modelo, etc. Puedes hacer commits tan seguido como quieras para guardar tu progreso.

1.  **Añade tus cambios:**
    ```bash
    # Añade el notebook o cualquier otro archivo que modificaste
    git add nombre_del_notebook.ipynb
    ```

2.  **Guarda tus cambios con un mensaje claro:**
    ```bash
    git commit -m "feat: Se agrega mapa interactivo con Folium"
    # Usa prefijos como:
    # feat: para una nueva funcionalidad (feature)
    # fix: para una corrección (bug fix)
    # docs: para cambios en la documentación
    ```

3.  **Sube tu rama a GitHub:**
    ```bash
    # La primera vez que subes la rama:
    git push -u origin geosal/agregar-mapa-interactivo
    # Para las siguientes actualizaciones en la misma rama:
    git push
    ```

### Paso 3: Integra tu Trabajo (Pull Request) 📬

Cuando tu funcionalidad esté lista y probada, es hora de proponer que se integre a la rama `main`. Esto se hace con un **Pull Request (PR)**.

1.  Ve a la página de nuestro repositorio en GitHub.
2.  Verás un botón amarillo que dice **"Compare & pull request"**. Dale clic.
    
3.  **Escribe un título y una descripción clara** de lo que hiciste. Si resolviste un problema, explícalo. Si creaste algo nuevo, describe cómo funciona.
4.  Asigna a un compañero como **revisor (reviewer)**. Nadie debe fusionar su propio código sin que al menos otra persona le dé el visto bueno.
5.  Una vez que tu PR sea aprobado, la persona que lo revisó (o tú, si te dan permiso) puede hacer clic en **"Merge pull request"**.
6.  ¡Listo! Tu código ahora es parte de la rama `main`. No te olvides de borrar tu rama antigua desde GitHub para mantener todo limpio.

---

### 📋 Resumen del Flujo de Trabajo

**`main` → `crear-branch` → `programar` → `commit` → `push` → `pull-request` → `revisión` → `merge` → 🎉**

Siguiendo estos pasos, nos aseguramos de que nuestro proyecto se mantenga organizado y funcional durante todo el hackathon. ¡A programar!
