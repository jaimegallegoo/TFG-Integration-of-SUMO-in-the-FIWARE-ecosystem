# Implementación e Integración de Herramientas de Simulación de Tráfico en el ecosistema FIWARE para la Gestión del Tráfico Urbano

Urban Mobility Manager es una aplicación web que permite administrar datos de transporte público en diferentes ciudades.

La aplicación proporciona información recopilada desde el simulador SUMO sobre las líneas de autobús, metro y tren de cercanías, así como las paradas de transporte público de la ciudad.

Además, ofrece la posibilidad de editar rutas y relanzar simulaciones para visualizar los cambios realizados.

## Guía de instalación

Instrucciones sobre cómo instalar y configurar tu proyecto.

### Requisitos previos

1. **Instalación de Docker**  
   Será necesario instalar [Docker](https://docs.docker.com/engine/install/) para poder ejecutar los contenedores de la aplicación. Para dispositivos Windows y Mac, se recomienda instalar [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/) debido a la facilidad de uso.
2. **Instalación de Docker Compose**  
   En el caso de haber instalado Docker Desktop, este paso no es necesario, ya que viene incluido en la instalación. En caso contrario, se deberá instalar [Docker Compose](https://docs.docker.com/compose/install/) para poder desplegar varios contenedores simultáneamente.

### Arranque de la aplicación

1. **Clonar el repositorio**  
   El primer paso consiste en clonar el repositorio donde se aloja el código de la aplicación mediante el siguiente comando en la terminal:  
   `$ git clone https://github.com/jaimegallegoo/TFG-Integration-of-SUMO-in-the-FIWARE-ecosystem.git`
2. **Acceder a la carpeta raíz del proyecto**  
   Después, hay que situarse en la carpeta raíz:  
   `$ cd TFG-Integration-of-SUMO-in-the-FIWARE-ecosystem`
3. **Arrancar la aplicación**  
   Desde la raíz, mediante Docker Compose se despliegan todos los contenedores y se arranca la aplicación:  
   `$ docker compose up -d`
4. **Acceder a la interfaz web**  
   Una vez los contenedores estén en funcionamiento, se podrá acceder desde cualquier navegador a la interfaz web a través de la siguiente dirección desde la máquina local:  
   `http://localhost:8000/`

### Cierre de la aplicación

Para cerrar la aplicación y detener todos los contenedores, se ejecuta el siguiente comando:  
`$ docker compose down`

## Tecnologías Utilizadas

Este proyecto hace uso de varias tecnologías clave, incluyendo:

- **[SUMO](https://www.eclipse.org/sumo/)** - Simulador de tráfico de vehículos utilizado para la creación de escenarios de movilidad urbana.
  <p align="center">
    <img src="/web/images/sumo.png" alt="SUMO" width="200" style="margin-top: 10px;"/>
  </p>
- **[FIWARE](https://www.fiware.org/)** - Plataforma utilizada para la integración y gestión de datos del simulador.
  <p align="center">
    <img src="/web/images/fiware.png" alt="FIWARE" width="200" style="margin-top: 10px;"/>
  </p>
- **[Docker](https://www.docker.com/)** - Herramienta utilizada para la contenerización y despliegue de la aplicación.
  <p align="center">
    <img src="/web/images/docker.png" alt="Docker" width="200" style="margin-top: 10px;"/>
  </p>

## Acerca del Proyecto

Este proyecto forma parte de un Trabajo de Fin de Grado realizado por Jaime Gallego Chillón. El objetivo principal ha sido integrar herramientas de simulación de tráfico en el ecosistema FIWARE para mejorar la gestión del tráfico urbano.
