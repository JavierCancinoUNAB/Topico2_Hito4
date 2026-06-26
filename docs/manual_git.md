# Manual de Git - Soporte Técnico Interno

## 1. Introducción a Git

Git es un sistema de control de versiones distribuido creado por Linus Torvalds en 2005. Permite rastrear cambios en el código fuente, colaborar con otros desarrolladores y mantener un historial completo del proyecto.

## 2. Conceptos Fundamentales

### 2.1 Repositorio
Un repositorio es el directorio donde Git almacena el historial completo del proyecto. Existe en forma local (.git) y puede tener un remoto (GitHub, GitLab, Bitbucket).

### 2.2 Commit
Un commit es una instantánea del estado del repositorio en un momento específico. Cada commit tiene un identificador único (hash SHA-1).

### 2.3 Branch (Rama)
Una rama es una línea independiente de desarrollo. La rama principal suele llamarse `main` o `master`.

### 2.4 Merge
El merge combina los cambios de una rama con otra.

### 2.5 Staging Area (Área de Preparación)
El área de staging o índice es una zona intermedia donde se preparan los cambios antes de hacer un commit.

## 3. Configuración Inicial

```
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
git config --global core.editor nano
git config --list       # Ver configuración actual
```

## 4. Comandos Esenciales

### 4.1 Inicializar y Clonar

**Crear nuevo repositorio:**
```
git init
git init nombre_proyecto
```

**Clonar repositorio existente:**
```
git clone https://url-del-repositorio.git
git clone https://url-del-repositorio.git nombre_local
```

### 4.2 Estado y Diferencias

**Ver estado del repositorio:**
```
git status
```

**Ver cambios no preparados:**
```
git diff
```

**Ver cambios preparados (staged):**
```
git diff --staged
```

**Ver historial de commits:**
```
git log
git log --oneline       # Formato resumido
git log --oneline --graph --all   # Vista gráfica de ramas
git log -n 10           # Últimos 10 commits
git log --author="nombre"  # Commits de un autor
```

### 4.3 Gestión de Cambios

**Agregar archivos al staging area:**
```
git add nombre_archivo
git add .               # Agregar todos los cambios
git add *.py            # Agregar todos los archivos .py
git add directorio/     # Agregar directorio completo
```

**Quitar archivo del staging:**
```
git restore --staged nombre_archivo
```

**Descartar cambios en archivo:**
```
git restore nombre_archivo
```

**Hacer commit:**
```
git commit -m "Mensaje descriptivo del cambio"
git commit -am "Mensaje"    # Agrega y hace commit de archivos rastreados
```

**Modificar último commit:**
```
git commit --amend -m "Nuevo mensaje"
```

### 4.4 Trabajo con Ramas

**Ver ramas:**
```
git branch              # Ramas locales
git branch -a           # Todas las ramas (locales y remotas)
git branch -v           # Con último commit
```

**Crear rama:**
```
git branch nombre_rama
```

**Cambiar a una rama:**
```
git checkout nombre_rama
git switch nombre_rama  # Forma moderna
```

**Crear y cambiar a nueva rama:**
```
git checkout -b nombre_rama
git switch -c nombre_rama   # Forma moderna
```

**Eliminar rama:**
```
git branch -d nombre_rama           # Solo si ya fue mergeada
git branch -D nombre_rama           # Fuerza eliminación
git push origin --delete nombre_rama  # Eliminar rama remota
```

**Renombrar rama:**
```
git branch -m nombre_antiguo nombre_nuevo
```

### 4.5 Fusionar Ramas (Merge)

**Mergear rama en la rama actual:**
```
git merge nombre_rama
```

**Merge sin fast-forward (crea commit de merge):**
```
git merge --no-ff nombre_rama
```

**Abortar un merge con conflictos:**
```
git merge --abort
```

### 4.6 Repositorios Remotos

**Ver remotos configurados:**
```
git remote -v
```

**Agregar remoto:**
```
git remote add origin https://url-del-repositorio.git
```

**Descargar cambios del remoto sin aplicar:**
```
git fetch origin
```

**Descargar y aplicar cambios (fetch + merge):**
```
git pull
git pull origin main
```

**Actualizar el repositorio local con cambios remotos:**
```
git pull origin nombre_rama
```

**Enviar cambios al remoto:**
```
git push origin nombre_rama
git push -u origin nombre_rama   # Primera vez, establece tracking
git push --force-with-lease      # Forzar push (más seguro que --force)
```

**Enviar todas las ramas:**
```
git push --all origin
```

**Enviar tags:**
```
git push --tags
```

### 4.7 Tags

**Crear tag:**
```
git tag v1.0.0
git tag -a v1.0.0 -m "Versión 1.0.0"    # Tag anotado
```

**Listar tags:**
```
git tag
git tag -l "v1.*"
```

**Ir a un tag:**
```
git checkout v1.0.0
```

**Eliminar tag:**
```
git tag -d v1.0.0
git push origin --delete v1.0.0   # Eliminar tag remoto
```

### 4.8 Stash (Guardado Temporal)

**Guardar cambios temporalmente:**
```
git stash
git stash save "descripción del stash"
```

**Ver lista de stashes:**
```
git stash list
```

**Recuperar último stash:**
```
git stash pop       # Aplica y elimina el stash
git stash apply     # Aplica sin eliminar el stash
```

**Recuperar stash específico:**
```
git stash pop stash@{2}
```

**Eliminar stash:**
```
git stash drop stash@{0}
git stash clear     # Elimina todos los stashes
```

## 5. Flujos de Trabajo

### 5.1 Flujo Básico
1. `git pull` - Actualizar repositorio local
2. `git checkout -b feature/nueva-funcionalidad` - Crear rama de trabajo
3. Realizar cambios en el código
4. `git add .` - Preparar cambios
5. `git commit -m "Descripción del cambio"` - Confirmar cambios
6. `git push origin feature/nueva-funcionalidad` - Enviar al remoto
7. Crear Pull Request para revisión

### 5.2 GitFlow
- `main`: código en producción
- `develop`: rama de integración
- `feature/*`: nuevas funcionalidades
- `release/*`: preparación de versiones
- `hotfix/*`: correcciones urgentes en producción

## 6. Revertir Cambios

**Deshacer último commit manteniendo cambios:**
```
git reset --soft HEAD~1
```

**Deshacer último commit eliminando cambios:**
```
git reset --hard HEAD~1
```

**Revertir un commit específico (crea nuevo commit):**
```
git revert hash_del_commit
```

**Volver a un commit específico:**
```
git reset --hard hash_del_commit
```

## 7. .gitignore

El archivo `.gitignore` define qué archivos y directorios deben ser ignorados por Git.

**Ejemplo de .gitignore:**
```
# Dependencias
node_modules/
__pycache__/
*.pyc
.venv/

# Variables de entorno
.env
.env.local

# Archivos del editor
.vscode/
.idea/
*.swp

# Archivos de compilación
dist/
build/
*.log

# Sistema operativo
.DS_Store
Thumbs.db
```

## 8. Resolución de Conflictos

Un conflicto ocurre cuando dos ramas modifican la misma parte de un archivo.

**Identificar archivos en conflicto:**
```
git status
```

Los conflictos se marcan así en el archivo:
```
<<<<<<< HEAD
Tu versión del código
=======
Versión de la otra rama
>>>>>>> nombre_rama
```

**Pasos para resolver:**
1. Abrir el archivo y resolver manualmente el conflicto
2. Eliminar los marcadores `<<<<<<<`, `=======`, `>>>>>>>`
3. `git add archivo_resuelto`
4. `git commit -m "Resuelve conflicto en archivo"`

## 9. Comandos Avanzados

**Rebase:**
```
git rebase main             # Rebase sobre main
git rebase -i HEAD~3        # Rebase interactivo (últimos 3 commits)
```

**Cherry-pick (copiar commit de otra rama):**
```
git cherry-pick hash_commit
```

**Bisect (encontrar commit que introdujo un bug):**
```
git bisect start
git bisect bad              # El commit actual es malo
git bisect good v1.0        # Este tag era bueno
```

**Blame (ver quién modificó cada línea):**
```
git blame archivo.py
```

## 10. Solución de Problemas Comunes

**Deshacer git add antes del commit:**
```
git restore --staged archivo
```

**Recuperar archivo eliminado:**
```
git checkout HEAD -- archivo_eliminado
```

**Error "refusing to merge unrelated histories":**
```
git pull origin main --allow-unrelated-histories
```

**Cambiar URL del remoto:**
```
git remote set-url origin nueva_url
```

**Ver qué commit eliminó un archivo:**
```
git log --all -- nombre_archivo
```
