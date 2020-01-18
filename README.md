https://github.com/manuvillalba-uclm/PajareroVillalba.git

## Luis Pajarero Reina y Manuel Villalba Montalbán



# Para lanzar el sistema dividimos en dos partes:

CABE DESTACAR QUE ES NECESARIO ESTAR EN EL MISMO DIRECTORIO QUE EL PROYECTO.

## Parte del servidor:

Tenemos dos opciones:

 - ### Makefile: 
 $make run, tendríamos todos los nodos funcionando.Si quisieramos una configuración de nodos más personalizada podriamos hacer $make clean $make app-workspace y ya ir iniciando los nodos que queramos, aconsejablemente primero el registry.
 
 Y una vez iniciados los nodos; icegridgui, cargar nuestro .xml, logearnos en el icegrid registry, save to registry y finalmente Tools>Application>Patch Distribtion.Si tenemos dos host tenemos que hacerlo en los dos.
 
  ### **NOTA:** 
  Si quisiesemos hacer _"el sistema debería ser   completamente   funcional   en   un   despliegue   en   dos   hosts: nodos  registry-node  y orchestrator-node en el Host 1 y downloads-node en el Host 2."_ es necesario sustituir la ip hostlocal de icegrid.locator del downloads-node.config con la ip donde se encuentre registry-node 
 
 - ### ShellScript: 
 $sh run_server.sh, funciona muy parecido que $make run, pero perdemos la característica de configuración de qué nodos queremos activos en cada host, los activa todos.
 
  Y una vez iniciados los nodos; icegridgui, cargar nuestro .xml, logearnos en el icegrid registry, save to registry y finalmente Tools>Application>Patch Distribtion.Si tenemos dos host tenemos que hacerlo en los dos.
 
 ## Parte del cliente:
 Tenemos tres opciones:
  - ### ShellScript:
  $sh run_cliente.sh ejeccuta una prueba de descarga, lista y transferencia con una url ya definida. Es una prueba un poco tonta, recomendamos las otras dos opciones.
  
  - ### MakeFile: 
    - $make run-client-download 1="url"
    - $make run-client-list
    - $make run-client-transfer 1="nombre.mp3" 
    
    ### **NOTA:** 
    
    nombre.mp3 va sin id, por tanto si tenemos en la lista:
    
    {
    
    name = VKMw2it8dQY - yooooooooooo.mp3
    
    hash = 8439dacdd604de6941cb7876c8647f409d230a0f351c143cd02262a9aca5ec7d
    
    }
    
    Nuestro nombre sería yooooooooooo.mp3
    
 - ### client.py:
   - client.py --Ice.Config=client.config "orchestrator" --download "url"
   - client.py --Ice.Config=client.config "orchestrator"
   - client.py --Ice.Config=client.config "orchestrator" --transfer "nombre.mp3"

 
 
