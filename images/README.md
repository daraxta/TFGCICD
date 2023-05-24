# CI/CD ArgoCD & Tekton

### Requisitos mínimos:

- Docker
- Minikube
- Bash
- Token de GitHub
- Token de DockerHub
- Servidor Linux (El laboratorio está realizado en Ubuntu)
- Ser administrador o tener permisos donde se puedan ejecutar comandos con sudo.

---

### Objetivo del repositorio

1. Programador/Desarrollador hace las modificaciones necesarias sobre una página web
2. Cuando el desarrollador hace un *push* sobre el repositorio, éste activa un *webhook* que envía una alerta a un *EventListener* que ejecuta una pipeline cuya función es la siguiente: 
    - Clonar el repositorio
    - Listar el contenido
    - Extraer los últimos 7 caractéres del último *commit* del repositorio
    - Construir una imagen en Docker donde la versión corresponde al resultado anterior.
    - Para finalizar, despliega un archivo yaml(en este caso un deployment) sobre Kubernetes con la imagen creada anterior.

---
### Pasos

1. Instalar Docker
- El depligue de MiniKube se hace levantando un contenedor de MiniKube para ello necesitamos tener Docker instalado.
La instalación se puede realizar desde los siguientes comandos o seguir la guía de la [página oficial](https://docs.docker.com/engine/install/)

    ~~~
     $ curl -fsSL https://get.docker.com -o get-docker.sh
     
     $ sudo sh get-docker.sh
    ~~~

- Si no queremos usar *sudo* añadiremos nuestro usuario al grupo de *docker*
   
   ~~~
    $ sudo usermod -aG docker $USER
   ~~~
- Para terminar tendremos que reiniciar el sistema.
   
   ~~~
    $ sudo reboot
   ~~~ 

2. Instalar MiniKube & Kubectl

- Para instalar minikube accedemos a la [página oficial ](https://minikube.sigs.k8s.io/docs/start/), en nuestro caso usaremos un sistema linux.

    ~~~
    $ curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

    $ sudo install minikube-linux-amd64 /usr/local/bin/minikube
    ~~~

- Por último, iniciamos el servicio de minikube.
    ~~~
    $ minikube start
    ~~~

- Instalamos Kubectl

    ~~~
    $ curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"

    $ sudo install kubectl /usr/local/bin/kubectl
    ~~~

3. Instalar las aplicaciones
- ##### ARGOCD 
    - Para la instalación primero debemos crear *namespace* donde se va a ejecutar el servicio.
        ~~~
        $ kubectl create namespace argocd
        $ kubectl get namespaces
        ~~~
    - A continuación, ejecutamos el siguiente comando sobre el namespace creado anteriormente.
        ~~~
        $ kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
        ~~~
    - Comprobamos el estado del servicio.
        ~~~
        $ kubectl get all -n argocd
        ~~~
- ##### TEKTON

    - Para la instalación deberemos ejecutar el siguiente comando.

        ~~~
        $ kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
        ~~~
    
    - En nuestro caso también vamos a hacer uso de la interfaz gráfica. 

        ~~~
        kubectl apply -f https://storage.googleapis.com/tekton-releases/dashboard/previous/v0.32.0/release-full.yaml
        ~~~

    - Comprobamos el estado del servicio.
        ~~~
        $ kubectl get namespaces
        ~~~ 
    - En este caso se deben de haber desplegado tres aplicaciones.
        ~~~
        $ kubectl get all  -n tekton-pipelines
        ~~~
4. Acceso a las aplicaciones

    Para acceder a las aplicaciones desde el servidor tendremos primero que conocer que puertos usa cada servicio.

    Por defecto, en ArgoCD el puerto interno por el que el servicio está escuchando es 8080, pero ejecutaremos el siguiente comando para comprobarlo.

    ~~~
    $ kubectl get svc -n argocd
    ~~~

    En el servicio que nos debemos de fijar es el *argocd-applicationset-controller*

    ![](images/PortServiceArgoCD.PNG)

    En el caso de Tekton el puerto por defecto es 9097

    ![](images/PortServiceTekton.PNG)
    
    Una vez tengamos los puertos tenemos que hacer un reenvío para poder acceder a los servicios. 

    - ArgoCD

        - Desde la propia máquina
            ~~~
            $ kubectl --namespace argocd port-forward svc/argocd-server 8081:80 
            ~~~
        - En el caso de querer acceder desde otra máquina y ponerlo en segundo plano.
            ~~~
            $ kubectl --namespace argocd port-forward svc/argocd-server 8081:80 --address 0.0.0.0 &>/dev/null &
            ~~~
        - Ahora podremos acceder desde el navegador introduciendo la siguiente url http://IP:8081 

            ![](images/argocdini.png)
        
        - Para el acceso tendremos que buscar la contraseña temporal. El usuario por defecto es admin.

            ~~~
            kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d;echo
            ~~~
        
        - Ya tendríamos ArgoCD.

            ![](images/menuargocd.png)


    - Tekton
    
        - Desde la propia máquina
            ~~~
            $ kubectl --namespace tekton-pipelines port-forward svc/tekton-dashboard 8082:9097
            ~~~
        - En el caso de querer acceder desde otra máquina y ponerlo en segundo plano.
            ~~~
            $ kubectl --namespace tekton-pipelines port-forward svc/tekton-dashboard 8082:9097 --address 0.0.0.0 &>/dev/null &
            ~~~

        - Accedemos por vía web, tekton por defecto no tiene credenciales de acceso.

            ![](images/tektondashboard.png)

5. Clonar el repositorio.
    - Para descargar los recursos tendremos que tener *git* instalado en la máquina.
        
        ~~~
        $ sudo apt-get update
        $ sudo apt-get install git
        ~~~
    - A continuación, clonamos el repositorio, éste contendrá todos los archivos necesarios para desplegar el CI/CD completo.

        ~~~
        $ git clone https://github.com/daraxta/CICDTekton.git
        ~~~

6. Creación de secret.
    - Es necesario que para subir una imagen a docker o a un repositorio de github se precise de unas credenciales para tener acceso a las mismas.

    - Creación de token en DockerHub.

        - Nos dirigimos a DockerHub, y a los ajustes de cuenta.

           ![](images/dockerhub.png)

        - Desde el apartado seguridad creamos un token.

            ![](images/dockersecurityhub.png)

        - Ahora con el token creado, iniciamos sesión en la máquina con los siguientes comandos.

            ~~~
            $ docker login index.docker.io
            ~~~

        - Ejecutamos el siguiente contenido, con nuestras credenciales y esto creará un secret.

            ~~~
            $ kubectl create secret docker-registry docker-credentials --docker-username=[usuario] --docker-password=[token] --docker-email=[correo]
            ~~~


    - Creación token GitHub.

        - Desde GitHub nos dirigimos a "*Settings*" $\rightarrow$ "*Developer settings*" $\rightarrow$ "*Personal access token*" $\rightarrow$ "*Tokens (classic)*".

            ![](images/githubtoken.png) 
     
        - Desde esta opción podemos crear un token.

            ![](images/githubcreatoken.png)

        - Creamos un archivo llamado gitcredentials.yaml, donde el objeto es una secret de Kubernetes.

          ```yaml
          apiVersion: v1
          kind: Secret
          metadata:
            name: auth-git
          type: Opaque
          stringData:
           .gitconfig: |
             [credential "https://github.com"]
             helper = store
           .git-credentials: https://USER:TOKEN@github.com
          ```
        - Por último lo ejecutamos.

            ~~~
            $ kubectl apply -f gitcredentials.yaml
            ~~~
        
7. Ejecución de Task y Pipelines.

    - Los primeros pipelines son para ejecutar los triggers.

        ~~~
        $ kubectl apply --filename \
        https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml    

        $ kubectl apply --filename \
        https://storage.googleapis.com/tekton-releases/triggers/latest/interceptors.yaml
        ~~~
    
    - Desde el TektonHub lanzaremos tres tareas, la primera es de Git, encargada de clonar un repositorio, la segunda es kaniko, una tarea para la creación de imágenes con docker y la tercera son para permitir hacer despliegues en kubernetes desde tekton.

        ~~~
        $ kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/git-clone/0.9/git-clone.yaml

        $ kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/kaniko/0.6/kaniko.yaml

        $ kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/kubernetes-actions/0.2/kubernetes-actions.yaml 
        ~~~

    - En este punto debemos de movernos a la carpeta nginx del repositorio y lanzar las tasks.

        ~~~
        $ cd CICDTekton/nginx

        $ kubectl apply -f gitlist.yaml,lsgit.yaml
        ~~~

    - Y ejecutamos los triggers necesarios, para ello desde la carpeta principal iremos a la carpeta de *triggers*.

        ~~~
        $ cd CICDTekton/triggers

        $ kubectl apply -f serviceaccount.yaml,triggerbinding.yaml,triggertemplate.yaml,eventlistener.yaml
        ~~~

    - Finalmente nos dirigimos a la carpeta de *pipelineruns* y ejecutamos el pipeline.

        ~~~
        $ cd CICDTekton/pipelineruns

        $ kubectl apply -f pipelineclone.yaml
        ~~~

8. Creacion del WebHook y configuración del EventListeners

    - Primero tendremos que exponer el puerto del GitHub WebHook, tendremos que ver si funciona 

        ~~~
        $ kubectl port-forward svc/el-github-pr 9000:8080
        ~~~

    - El WebHook tiene que poder acceder a una página, en este caso nuestra apertura de puertos es local, para poder exponerlo a internet usaremos la herramienta Ngrok.

        - Instalar Ngrok

        ~~~
        $ curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok 
        ~~~ 

    - Exponemos el puerto a internet.

        ~~~
        $ ngrok http 9000
        ~~~

    - Una vez generado tendremos que copiar la url *https* para su posterior uso.

        ![](images/ngrok.png)


    - Desde el repositorio de GitHub accedemos a *Settings*
    
        ![](images/githubset.png)
    
    - Una vez dentro desde el apartado de webhook 

        ![](images/gitwebhook.png)
    
    - Configuramos el WebHook con la url anterior.

        ![](images/gitwebhookcreacion.png)
    
    - Automáticamente en Tekton se lanza la pipeline.

        ![](images/tektonpipe.png)

9. El último paso será configurar ArgoCD para poder visualizar lo que se ha desplegado.

    - El primer paso será añadir un repositorio a la aplicación.

        ![](images/argocdrepo.png)

    - Añadimos las credenciales de GitHub.

        ![](images/argocdrepoadd.png)

    - Una vez configurado, creamos la aplicación apuntando hacia el repositorio donde tiene almacenado el deployment.

        ![](images/argoapplication.png)

    - Finalmente ya tenemos la application de ArgoCD configurada.(Por defecto al no tener un WebHook configurado al aplicación se sincroniza cada 3 min).

        ![](images/argoapp.png)
    
