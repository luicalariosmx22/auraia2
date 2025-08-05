Descripción de proyecto
SDK empresarial de Facebook para Python
PyPI Estado de compilación Licencia

Introducción
El SDK de Facebook para Empresas es una solución integral que ayuda a nuestros socios a mejorar el servicio a sus negocios. Los socios utilizan múltiples API de Facebook para satisfacer las necesidades de sus clientes. Adoptar todas estas API y mantenerlas actualizadas en las distintas plataformas puede ser una tarea laboriosa y, en última instancia, prohibitiva. Por ello, Facebook ha desarrollado el SDK para Empresas, integrando muchas de sus API en un solo SDK para facilitar su implementación y mantenimiento. El SDK para Empresas es una versión mejorada del SDK de la API de Marketing, que incluye la API de Marketing, así como muchas API de Facebook de diferentes plataformas, como Páginas, Business Manager, Instagram, etc.

Inicio rápido
Guía de inicio rápido del SDK empresarial

Python es actualmente el lenguaje más popular entre nuestros desarrolladores externos. facebook_businessEs un paquete de Python que proporciona una interfaz entre tu aplicación Python y las API de Facebook dentro del SDK para empresas . Este tutorial abarca los conocimientos básicos necesarios para usar el SDK y ofrece algunos ejercicios.

NOTA : facebook_business¡el paquete es compatible con Python 2 y 3!

Prerrequisitos
Registrar una aplicación
Para comenzar a utilizar el SDK, debes tener una aplicación registrada en developer.facebook.com .

Para administrar la API de marketing, visite el Panel de control de su aplicación y agregue el producto API de marketing a su aplicación.

IMPORTANTE : Por seguridad, se recomienda que active la opción 'Prueba de secreto de aplicación para llamadas a la API del servidor' en la página Configuración->Avanzada de su aplicación.

Obtener un token de acceso
Cuando alguien se conecta con una aplicación usando el inicio de sesión de Facebook y aprueba la solicitud de permisos, la aplicación obtiene un token de acceso que proporciona acceso temporal y seguro a las API de Facebook.

Un token de acceso es una cadena opaca que identifica a un usuario, una aplicación o una página.

Por ejemplo, para acceder a la API de marketing, debe generar un token de acceso de usuario para su aplicación y solicitar ads_managementpermiso; para acceder a la API de páginas, debe generar un token de acceso de página para su aplicación y solicitar manage_pagepermiso.

Consulte nuestra Guía de token de acceso para obtener más información.

Por ahora, podemos usar el Explorador de gráficos para obtener un token de acceso.

Instalar paquete
La forma más sencilla de instalar el SDK es a través pipde su shell.

NOTA : Para Python 3, utilice pip3y python3en su lugar.

NOTA : Úselo sudosi alguno de estos presenta problemas con los permisos. (Esto podría suceder si está usando un sistema con Python instalado).

Si no tienes pip:

easy_install pip
Ahora ejecuta cuando tengas pip:

pip install facebook_business
Si prefieres la última versión en lugar de una versión posiblemente desactualizada del repositorio pypi.python.org , consulta el repositorio en GitHub o descarga un archivo tar de la versión . Una vez descargado y descomprimido el paquete, instálalo:

python setup.py install
¡Genial, ahora estás listo para usar el SDK!

Arranque
Crear test.py
Cree un archivo test.py con el contenido a continuación (suponiendo que su sistema usa Python 2.7 y está instalado en /opt/homebrew. Actualice a la ubicación correcta de Python):

import sys sys . path . append ( '/opt/homebrew/lib/python2.7/site-packages' ) # Reemplace esto con el lugar donde instaló facebookads usando pip sys . path . append ( '/opt/homebrew/lib/python2.7/site-packages/facebook_business-3.0.0-py2.7.egg-info' ) # Igual que arriba 
 
 

desde facebook_business.api importar FacebookAdsApi desde facebook_business.adobjects.adaccount importar AdAccount   
   

my_app_id  =  'tu-id-de-aplicación' 
my_app_secret  =  'tu-secreto-de-aplicación' 
my_access_token  =  'tu-token-de-acceso-a-página' 
FacebookAdsApi . init ( my_app_id ,  my_app_secret ,  my_access_token ) 
my_account  =  AdAccount ( 'act_<tu-id-de-cuenta-ad>' ) 
campaigns  =  my_account . get_campaigns () 
print ( campaigns )
Pruebe su instalación
Pruebe su instalación con el siguiente comando:

 prueba de Python .py
Debería ver el resultado en la ventana de su terminal. Si se informa de un token caducado, repita el proceso para solicitar un token de acceso a la página descrito en la sección de prerrequisitos anterior.

NOTA : Usaremos el módulo de objetos en el resto del tutorial. También puedes usar directamente los archivos de clase individuales en adobjects.

Entendiendo CRUD
El SDK implementa un diseño CRUD (crear, leer, actualizar, eliminar). Los objetos relevantes para explorar el gráfico se encuentran en el módulo de objetos del paquete facebook_business.

Todos los objetos del grafo son instancias de AbstractObject. Algunos objetos pueden consultarse directamente y, por lo tanto, son instancias de AbstractCrudObject(una subclase de AbstractObject). Ambas clases abstractas se encuentran en facebook_business.adobjects.

Hay una carpeta adicional adobjectsen facebook_business. Allí verá un archivo para cada objeto de anuncio en nuestra API de Marketing. Estos archivos se generan automáticamente desde nuestra API y, por lo tanto, son prácticamente iguales a lo que ofrece. Según las operaciones CRUD que se puedan realizar en cada objeto, verá la presencia de los siguientes métodos:

api_get
api_update
api_delete
create_xxx
get_xxx
Por ejemplo, Campaign cuenta con todos estos métodos, pero AdAccount no. Consulta la documentación de la API de Marketing para obtener más información sobre cómo se utilizan los diferentes objetos de anuncio .

Hay algunas funciones obsoletas en AbstractCrudObject, como

remote_create
remote_read
remote_update
remote_delete
Intente dejar de usarlos ya que es posible que los dejemos obsoletos pronto.

Explorando el gráfico
El SDK abstrae la API mediante la definición de clases que representan objetos en el gráfico. Estas definiciones de clase y sus ayudantes se encuentran en facebook_business.adobjects.

Inicialización de objetos
Consulte los métodos AbstractObjectde y AbstractCrudObjectde __init__para obtener más información. La mayoría de los objetos del gráfico pertenecen a una de las dos subclases.

Al instanciar un objeto de anuncio, puedes especificar su ID si ya existe definiendo fbidun argumento. Además, si quieres interactuar con la API usando un objeto de API específico en lugar del predeterminado, puedes especificar el apiargumento.

Bordes
Observa los métodos de un objeto para ver qué asociaciones podemos iterar. Por ejemplo, un Userobjeto tiene un método get_ad_accountsque devuelve un iterador de AdAccountobjetos.

Cuenta publicitaria
La mayoría de las operaciones relacionadas con anuncios se realizan en el contexto de una cuenta publicitaria. Puedes ir al Administrador de Anuncios para ver las cuentas para las que tienes permiso. La mayoría de ustedes probablemente tengan una cuenta personal.

Obtengamos todas las cuentas de anuncios del usuario con el token de acceso especificado. Solo tengo una cuenta, así que se imprime lo siguiente:

>>>  de facebook_business.adobjects.user import Usuario >>> yo = adobjects.User ( fbid = 'yo' ) >>> mis_cuentas = lista ( yo.get_ad_accounts ( )) >>> imprimir ( mis_cuentas ) [ { ' id_cuenta' : u ' 17842443' , ' id' : u ' act_17842443' } ] >>> tipo ( mis_cuentas [ 0 ]) < clase ' facebook_business.adobjects.AdAccount ' >   
   
   
 
      
 
 
ADVERTENCIA : No especificamos un argumento de palabra clave api=apial instanciar el Userobjeto aquí porque ya hemos configurado la API predeterminada durante el arranque.

NOTA : Envolvemos el valor de retorno de get_ad_accountscon list() porque get_ad_accountsdevuelve un EdgeIteratorobjeto (ubicado en facebook_business.adobjects) y queremos obtener la lista completa de inmediato en lugar de que el iterador cargue las cuentas de manera diferida.

Para nuestros propósitos, podemos simplemente elegir una cuenta y hacer nuestros experimentos en su contexto:

>>>  mi_cuenta  =  mis_cuentas [ 0 ]
O si ya conoces el ID de tu cuenta:

>>>  mi_cuenta  =  adobjects . CuentaAd ( 'act_17842443' )
Crear
Creemos una campaña. Está en el contexto de la cuenta, es decir, su padre debería ser la cuenta.

campos  =  [ 
] 
parámetros  =  { 
  adobjects . Campaign . Field . name  :  'Conversiones de la campaña' , 
  adobjects . Campaign . Field . configuration_status :  adobjects . Campaign . Status . paused , 
} 
campaña  =  AdAccount ( id ) . create_campaign ( campos ,  parámetros )
A continuación, especificamos algunos detalles sobre la campaña. Para determinar qué propiedades definir, consulte los campos disponibles del objeto (ubicados en [nombre del objeto Campaign.Field]) y también la documentación del objeto de anuncio (por ejemplo, " Campaña ").

NOTA : Para encontrar los campos, mire el archivo de clase individual en el directorio adobjects.

Si se produce un error, se generará una excepción. Las posibles excepciones y sus descripciones se enumeran en facebook_business.exceptions.

Leer
También podemos leer las propiedades de un objeto desde la API, suponiendo que el objeto ya está creado y tiene una ruta de nodo. Acceder a las propiedades de un objeto es sencillo, ya que AbstractObjectimplementa collections.MutableMapping. Se puede acceder a ellas como si se accediera a la clave de un diccionario:

>>>  print ( mi_cuenta ) 
{ 'id_cuenta' :  u '17842443' ,  'id' :  u 'act_17842443' } 
>>>  mi_cuenta  =  mi_cuenta . api_get ( campos = [ adobjects . AdAccount . Field . amount_spent ]) 
>>>  print ( mi_cuenta [ adobjects . AdAccount . Field . amount_spent ]) 
{ 'amount_spent' :  21167 ,  'id_cuenta' :  u '17842443' ,  'id' :  u 'act_17842443' }
Actualizar
Para actualizar un objeto, podemos modificar sus propiedades y luego llamar al api_updatemétodo para sincronizarlo con el servidor. Corrijamos la errata de "Campaña" por "Campaña":

>>>  campaña.api_update ( campos = [ ] , parámetros = { adobjects.campaña.campo.nombre : " Campaña de la Papa " } ) 
Puedes ver los resultados en el administrador de anuncios.

Borrar
Si decidimos que ya no queremos la campaña que creamos:

campaña .api_delete ( )
Argumentos útiles
TOKENS DE ACCESO MÚLTIPLE
En la documentación, se llama al método FacebookAdsApi.init antes de realizar cualquier llamada a la API. Este método configura un objeto FacebookAdsApi predeterminado que se usa en todas partes. Esto simplifica el uso, pero no es viable cuando un sistema que usa el SDK realiza llamadas en nombre de varios usuarios.

Esto no es viable porque cada usuario debería tener su propia sesión de Facebook, con su propio token de acceso, en lugar de usar la misma sesión para todos. Cada sesión debería usarse para crear un objeto FacebookAdsApi independiente. Vea el ejemplo a continuación:

my_app_id  =  '<APP_ID>' 
my_app_secret  =  '<APP_SECRET>' 
my_access_token_1  =  '<ACCESS_TOKEN_1>' 
my_access_token_2  =  '<ACCESS_TOKEN_2>' 
proxies  =  { 'http' :  '<HTTP_PROXY>' ,  'https' :  '<HTTPS_PROXY>' }  # agregue proxies si es necesario

sesión1  =  FacebookSession ( 
    mi_id_de_aplicación , 
    mi_secreto_de_aplicación , 
    mi_token_de_acceso_1 , 
    proxies , 
)

sesión2  =  FacebookSession ( 
    mi_id_de_aplicación , 
    mi_secreto_de_aplicación , 
    mi_token_de_acceso_2 , 
    proxies , 
)

api1  =  FacebookAdsApi ( sesión1 ) 
api2  =  FacebookAdsApi ( sesión2 )
En los ejemplos del SDK, siempre configuramos un único objeto FacebookAdsApi como predeterminado. Sin embargo, al trabajar con varios tokens de acceso, es necesario usar varias API. Podemos configurar una API predeterminada para un usuario, pero para los demás, usaremos su objeto API como parámetro. En el siguiente ejemplo, creamos dos AdUsers: el primero con la API predeterminada y el segundo con su objeto API:

FacebookAdsApi.set_default_api ( api1 )​​

me1  =  Usuario de anuncio ( fbid = 'yo' ) 
me2  =  Usuario de anuncio ( fbid = 'yo' ,  api = api2 )
Otra forma de crear los mismos objetos anteriores sería:

me1  =  AdUser ( fbid = 'yo' ,  api = api1 ) 
me2  =  AdUser ( fbid = 'yo' ,  api = api2 )
A partir de aquí, el flujo de trabajo para estos objetos se mantiene igual. Las únicas excepciones son las llamadas a métodos de clase, donde ahora debemos pasar la API que queremos usar como último parámetro en cada llamada. Por ejemplo, una llamada al método Aduser.get_by_ids debería ser así:

sesión  =  FacebookSession ( 
 mi_id_de_aplicación , 
 mi_secreto_de_aplicación , 
 mi_token_de_acceso_1 , 
 proxies , 
)

api  =  FacebookAdsApi ( sesión1 ) 
Aduser.get_by_ids ( ids = [ ' <UID_1> ' , '<UID_2>' ], api = api )  
CRUD
Todas las llamadas CRUD admiten un paramsargumento de palabra clave que toma un diccionario que asigna los nombres de los parámetros a sus valores en caso de que se requiera una modificación avanzada. Puede encontrar la lista de nombres de parámetros como atributos de [nombre de la {your object class}.Fieldclase]. Dentro de la clase Campo puede haber otras clases que contengan, como atributos, campos válidos del valor de una de las propiedades principales.

api_updatey create_xxxadmite un filesargumento de palabra clave que toma un diccionario que asigna nombres de referencia de archivo a objetos de archivo binarios abiertos.

api_getAdmite un fieldsargumento de palabra clave, lo cual es una forma conveniente de especificar el parámetro 'campos'. fieldsToma una lista de campos que deben leerse durante la llamada. Los campos válidos se encuentran como atributos de la clase Campo.

Bordes
Al inicializar un EdgeIteratoro al llamar a un método como por ejemplo AdAccount.get_ad_campaigns:

Puede especificar un fieldsargumento que tome una lista de campos para leer para los objetos que se están leyendo.
Puede especificar un paramsargumento que pueda ayudarle a especificar o filtrar el borde con mayor precisión.
Llamadas por lotes
Es eficiente agrupar un gran número de llamadas en una sola solicitud HTTP. El SDK simplifica este proceso. Puedes agrupar las llamadas en una instancia de FacebookAdsApiBatch[disponible en facebook_business.api]. Para obtener fácilmente una para tu instancia de API:

mi_api_batch  =  api . nuevo_batch ()
Las llamadas se pueden agregar al lote en lugar de ejecutarse inmediatamente:

campaña .api_delete ( batch = my_api_batch )​
Una vez que haya terminado de agregar llamadas al lote, puede enviar la solicitud:

my_api_batch .execute ( )
Siga las directrices de llamadas por lotes de la documentación de la API de Marketing . Hay un número óptimo de llamadas por lote. Además, tenga en cuenta la limitación de velocidad, ya que una llamada por lotes simplemente mejora el rendimiento de la red y cada llamada cuenta individualmente para la limitación de velocidad.

Excepciones
Consulte facebook_business.exceptionsla lista de excepciones que puede generar el SDK.

Pruebas
Pruebas unitarias
Las pruebas unitarias no requieren un token de acceso ni acceso a la red. Ejecútelas con su versión predeterminada de Python, como se indica a continuación:

python -m facebook_business.test.unit
También puedes usar tox para ejecutar las pruebas unitarias con múltiples versiones de Python:

sudo apt-get install python-tox  # Debian/Ubuntu
sudo yum install python-tox      # Fedora
tox --skip-missing-interpreters
Puedes aumentar la cobertura del intérprete instalando versiones adicionales de Python. En Ubuntu, puedes usar el PPA de deadsnakes . En otras distribuciones, puedes compilar desde el código fuente y luego usarlo sudo make altinstallpara evitar conflictos con la versión instalada en tu sistema.

Ejemplos
Los ejemplos de uso se encuentran en la examples/carpeta.

Depurar
Si este SDK no funciona como se espera, puede ser un problema del SDK o de la API.

Esto se puede identificar construyendo una solicitud cURL sin procesar y viendo si la respuesta es la esperada.

Por ejemplo:

desde facebook_business.adobjects.page importar Página desde facebook_business.api importar FacebookAdsApi   
   

FacebookAdsApi .init ( access_token = access_token , debug = True ) page = Page ( page_id ) .api_get ( fields = campos , params = parámetros )​​ 
  
Al ejecutar este código, esta solicitud cURL se imprimirá en la consola como:

curl -X 'GET' -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' -H 'Connection: keep-alive' -H 'User-Agent: fbbizsdk-python-v3.3.1' 'https://graph.facebook.com/v3.3/<pageid>/?access_token=<access_token>&fields=name%2Cbirthday%2Cphone'
Generación de código SDK
Nuestro SDK se genera automáticamente a partir de SDK Codegen . Si desea obtener más información sobre cómo se genera el código de nuestro SDK, consulte este repositorio.

Asunto
Como queremos gestionar los errores de forma más eficiente, hemos decidido cerrar el sistema de informes de errores en Github y pasar a nuestro canal dedicado. Si encuentra un error con Business SDK (Python), infórmelo en nuestro canal de informes de errores para desarrolladores .

Licencia
El SDK empresarial de Facebook para Python tiene licencia bajo el archivo LICENSE en el directorio raíz de este árbol de origen.


Solicitudes por lotes
Envía una solicitud HTTP que contenga varias llamadas a la API Graph de Facebook. Las operaciones independientes se procesan en paralelo mientras tus operaciones dependientes se procesan consecutivamente. Una vez que todas las operaciones están completas, se te devuelve una respuesta consolidada y se cierra la conexión HTTP.

El orden de las respuestas se corresponde con el orden de las operaciones en la solicitud. Por ese motivo, deberías procesar las respuestas para determinar qué operaciones resultaron satisfactorias y cuáles deberían intentarse en las operaciones posteriores.

Limitaciones
Las solicitudes por lotes se limitan a 50 solicitudes por lote. Cada llamada dentro del lote se cuenta por separado con el fin de calcular los límites de recursos y de llamadas a la API. Por ejemplo, un lote de diez llamadas a la API contará como diez llamadas y cada llamada dentro del lote contribuirá a los límites de recursos de CPU de la misma manera. Consulta nuestra Guía de limitación de frecuencia para obtener más información.
Las solicitudes por lote no pueden incluir varios conjuntos de anuncios en la misma campaña. Obtén más información sobre el procesamiento por lotes de las solicitudes de la API de marketing.
Solicitudes por lotes
Una solicitud por lotes presenta un objeto JSON que consiste en una matriz de tus solicitudes. Devuelve una matriz de respuestas HTTP lógicas representadas como matrices JSON. Cada respuesta tiene un código de estado, una matriz de encabezados opcional y un cuerpo opcional (que es una cadena con codificación JSON).

Para realizar una solicitud por lotes, envía una solicitud POST a un punto de conexión punto de conexión en el que el parámetro batch sea tu objeto JSON.

POST /ENDPOINT?batch=[JSON-OBJECT]
Ejemplo de solicitud por lotes

En este ejemplo, obtenemos información de dos páginas que nuestra app administra.

El formato se modificó para facilitar la lectura.
curl -i -X POST 'https://graph.facebook.com/me?batch=  
  [
    {
      "method":"GET",
      "relative_url":"PAGE-A-ID"
    },  
    {
      "method":"GET",
      "relative_url":"PAGE-B-ID"
    }
  ]
  &include_headers=false             // Included to remove header information
  &access_token=ACCESS-TOKEN'
Una vez que todas las operaciones estén completas, se envía una respuesta con el resultado de cada operación. Dado que los encabezados devueltos a veces pueden ser más grandes que la respuesta de la API real, tal vez prefieras eliminarlos a fin de mejorar la eficacia. Para incluir información de encabezado, elimina el parámetro include_headers o configúralo como true.

Ejemplo de respuesta

El campo del cuerpo contiene un objeto JSON de cadena codificada:

[
  {
    "code": 200,
    "body": "{
      \"name\": \"Page A Name\",
      \"id\": \"PAGE-A-ID\"
      }"
  },
  {
    "code": 200,
    "body": "{
      \"name\": \"Page B Name\",
      \"id\": \"PAGE-B-ID\"
      }"
  }
]
Solicitudes por lotes complejas
Es posible combinar operaciones que normalmente utilizarían distintos métodos HTTP en una sola solicitud por lotes. Mientras que las operaciones GET y DELETE solo pueden tener una dirección relative_url y un campo method, las operaciones POST y PUT pueden tener un campo body opcional. El cuerpo debe tener el formato de una cadena POST HTTP sin procesar, similar a una cadena de consulta URL.

Ejemplo de solicitud

En el siguiente ejemplo, se muestra una publicación en una página que administramos y en la que tenemos permisos de publicación, y después las noticias de la página en una sola operación:

curl "https://graph.facebook.com/PAGE-ID?batch=
  [
    { 
      "method":"POST",
      "relative_url":"PAGE-ID/feed",
      "body":"message=Test status update"
    },
    { 
      "method":"GET",
      "relative_url":"PAGE-ID/feed"
    }
  ]
  &access_token=ACCESS-TOKEN"
El resultado de esta llamada es:

[
    { "code": 200,
      "headers": [
          { "name":"Content-Type", 
            "value":"text/javascript; charset=UTF-8"}
       ],
      "body":"{\"id\":\"…\"}"
    },
    { "code": 200,
      "headers": [
          { "name":"Content-Type", 
            "value":"text/javascript; charset=UTF-8"
          },
          { "name":"ETag", 
            "value": "…"
          }
      ],
      "body": "{\"data\": [{…}]}
    }
]
En el siguiente ejemplo, se crea un nuevo anuncio para una campaña y después se obtienen detalles del objeto recién creado. Ten en cuenta la operación URLEncoding para el parámetro del cuerpo:

curl \
-F 'access_token=...' \
-F 'batch=[
  {
    "method":"POST",
    "name":"create-ad",
    "relative_url":"11077200629332/ads",
    "body":"ads=%5B%7B%22name%22%3A%22test_ad%22%2C%22billing_entity_id%22%3A111200774273%7D%5D"
  }, 
  {
    "method":"GET",
    "relative_url":"?ids={result=create-ad:$.data.*.id}"
  }
]' \
https://graph.facebook.com
En el siguiente ejemplo, se agregan varias páginas a un administrador comercial:

curl \
-F 'access_token=<ACCESS_TOKEN>' \
-F 'batch=[
  {
    "method":"POST",
    "name":"test1",
    "relative_url":"<BUSINESS_ID>/owned_pages",
    "body":"page_id=<PAGE_ID_1>"
  }, 
  {
    "method":"POST",
    "name":"test2",
    "relative_url":"<BUSINESS_ID>/owned_pages",
    "body":"page_id=<PAGE_ID_2>"
  }, 
  {
    "method":"POST",
    "name":"test3",
    "relative_url":"<BUSINESS_ID>/owned_pages",
    "body":"page_id=<PAGE_ID_3>"
  }, 
]' \
"https://graph.facebook.com/v12.0"
Dónde:

<ACCESS_TOKEN> es un token de acceso con el permiso business_management.
<BUSINESS_ID> es el identificador del administrador comercial al cual deben solicitarse las páginas.
<PAGE_ID_n> son los identificadores de la página que se debe solicitar.
Errores
Es posible que una de tus operaciones solicitadas genere un error. Esto podría deberse a que, por ejemplo, no tienes permiso para realizar la operación solicitada. La respuesta es similar a la API Graph estándar, pero encapsulada en la sintaxis de respuesta por lotes:

[
    { "code": 403,
      "headers": [
          {"name":"WWW-Authenticate", "value":"OAuth…"},
          {"name":"Content-Type", "value":"text/javascript; charset=UTF-8"} ],
      "body": "{\"error\":{\"type\":\"OAuthException\", … }}"
    }
]
Las restantes solicitudes del lote deberían seguir correctamente de todas formas y se devolverán, como siempre, con un código de estado 200.

Tiempos de espera
El tiempo de espera de los lotes grandes o complejos se puede agotar si todas las solicitudes dentro del lote tardan mucho en completarse. En tal circunstancia, el resultado es un lote parcialmente completado. En un lote parcialmente completado, las solicitudes que se completan de forma satisfactoria devolverán el resultado normal con el código de estado 200. Las respuestas a las solicitudes que no sean satisfactorias serán null. Puedes volver a intentar realizar cualquier solicitud que no haya sido satisfactoria.

Llamadas por lotes con JSONP
La API por lotes admite JSONP, al igual que el resto de la API Graph (la función de devolución de llamada de JSONP se especifica con el parámetro de publicación de formulario o cadena de consulta callback).

Uso de varios tokens de acceso
Las solicitudes individuales de una misma solicitud por lotes pueden especificar sus propios tokens de acceso como cadena de consulta o formar parámetros de publicación. En ese caso, el token de acceso de nivel superior se considera un token de reserva y se utiliza si una solicitud individual no especificó explícitamente un token de acceso.

Esto puede resultar útil cuando quieres consultar la API con distintos tokens de acceso de usuario o tokens de acceso a la página, o si es necesario realizar algunas de las llamadas con un token de acceso de app.

Debes incluir un token de acceso como parámetro de nivel superior, aun cuando todas las solicitudes individuales contengan sus propios tokens.

Subir datos binarios
Puedes subir varios elementos binarios como parte de una llamada por lotes. Para ello, necesitas agregar todos los elementos binarios como archivos adjuntos MIME o de varias partes a tu solicitud y necesitas que cada operación haga referencia a sus elementos binarios con la propiedad attached_files en la operación. La propiedad attached_files admite una lista separada por comas de nombres de archivos adjuntos en su valor.

En el siguiente ejemplo, se muestra cómo subir dos fotos en una sola llamada por lotes:

curl 
     -F 'access_token=…' \
     -F 'batch=[{"method":"POST","relative_url":"me/photos","body":"message=My cat photo","attached_files":"file1"},{"method":"POST","relative_url":"me/photos","body":"message=My dog photo","attached_files":"file2"},]' \
     -F 'file1=@cat.gif' \
     -F 'file2=@dog.jpg' \
    https://graph.facebook.com

## Obtener Conversaciones de Mensajería (Messaging Conversations)

### Introducción a las Métricas de Conversaciones

Las conversaciones iniciadas por mensajería son una métrica crucial para anuncios que tienen como objetivo generar leads a través de plataformas de mensajería como WhatsApp, Instagram Direct o Facebook Messenger. Estas métricas son especialmente importantes para campañas Click-to-Message.

### Tipos de Acciones de Mensajería Disponibles

La API de Facebook devuelve varios tipos de acciones relacionadas con mensajería:

- `onsite_conversion.messaging_conversation_started_7d` - Conversaciones iniciadas en ventana de 7 días
- `onsite_conversion.messaging_first_reply` - Primeras respuestas del usuario
- `onsite_conversion.total_messaging_connection` - Total de conexiones de mensajería
- `onsite_conversion.messaging_user_depth_2_message_send` - Usuarios que enviaron 2+ mensajes
- `onsite_conversion.messaging_user_depth_3_message_send` - Usuarios que enviaron 3+ mensajes
- `onsite_conversion.messaging_welcome_message_view` - Visualizaciones del mensaje de bienvenida
- `onsite_conversion.messaging_conversation_replied_7d` - Conversaciones respondidas en 7 días

### Método 1: Usando Graph API Directamente

```python
import requests
import json
from datetime import datetime, date, timedelta

def obtener_conversaciones_graph_api(ad_account_id, access_token, fecha_inicio, fecha_fin):
    url = f"https://graph.facebook.com/v19.0/act_{ad_account_id}/insights"
    
    params = {
        'access_token': access_token,
        'level': 'ad',
        'fields': 'ad_id,ad_name,actions,spend,impressions',
        'action_attribution_windows': ['7d_click', '1d_view'],
        'time_range': json.dumps({
            'since': fecha_inicio.strftime('%Y-%m-%d'),
            'until': fecha_fin.strftime('%Y-%m-%d')
        }),
        'limit': 500
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    insights = data.get('data', [])
    
    for insight in insights:
        actions = insight.get('actions', [])
        for action in actions:
            action_type = action.get('action_type')
            value = action.get('value')
            
            # Buscar conversaciones de mensajería
            if 'messaging_conversation_started' in action_type:
                print(f"Conversaciones: {action_type} = {value}")
```

### Método 2: Usando Facebook Business SDK (Recomendado)

```python
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.ad import Ad

# Inicializar API
FacebookAdsApi.init(app_id, app_secret, access_token)

def obtener_conversaciones_sdk(ad_account_id, fecha_inicio, fecha_fin):
    account = AdAccount(f'act_{ad_account_id}')
    
    # Obtener anuncios
    ads = account.get_ads(fields=['id', 'name', 'status'])
    
    for ad in ads:
        # Obtener insights del anuncio
        insights = ad.get_insights(
            fields=[
                'ad_id',
                'ad_name',
                'actions',
                'spend',
                'impressions'
            ],
            params={
                'time_range': {
                    'since': fecha_inicio.strftime('%Y-%m-%d'),
                    'until': fecha_fin.strftime('%Y-%m-%d')
                },
                'action_attribution_windows': ['7d_click', '1d_view']
            }
        )
        
        for insight in insights:
            actions = insight.get('actions', [])
            
            for action in actions:
                action_type = action.get('action_type', '')
                value = action.get('value', 0)
                
                # Filtrar acciones de mensajería
                if any(keyword in action_type.lower() for keyword in ['messaging', 'conversation']):
                    print(f"💬 {action_type}: {value}")
```

### Método 3: Insights Específicos por Anuncio

```python
from facebook_business.adobjects.ad import Ad

def obtener_conversaciones_por_anuncio(ad_id, fecha_inicio, fecha_fin):
    ad = Ad(ad_id)
    
    insights = ad.get_insights(
        fields=['messages', 'conversations_started', 'actions'],
        params={
            'time_range': {
                'since': fecha_inicio.strftime('%Y-%m-%d'),
                'until': fecha_fin.strftime('%Y-%m-%d')
            }
        }
    )
    
    for insight in insights:
        # Métricas directas (si están disponibles)
        messages = insight.get('messages', 0)
        conversations = insight.get('conversations_started', 0)
        
        print(f"Mensajes: {messages}")
        print(f"Conversaciones iniciadas: {conversations}")
        
        # Acciones detalladas
        actions = insight.get('actions', [])
        for action in actions:
            if 'messaging' in action.get('action_type', '').lower():
                print(f"{action.get('action_type')}: {action.get('value')}")
```

### Requisitos para Obtener Métricas de Conversaciones

1. **Objetivo de Campaña**: Los anuncios deben tener objetivo de "Mensajes" o "Generación de clientes potenciales"
2. **Tipo de Anuncio**: Click-to-Message, Click-to-WhatsApp, o Click-to-Messenger
3. **Configuración**: Los anuncios deben estar configurados específicamente para iniciar conversaciones
4. **Permisos**: El token de acceso debe tener permisos `ads_management`
5. **Ventana de Atribución**: Usar ventanas de 7 días para capturar conversaciones completas

### Ejemplo Completo de Implementación

```python
import os
from datetime import datetime, date, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

def sincronizar_conversaciones_meta_ads():
    # Configuración
    access_token = os.getenv('META_ACCESS_TOKEN')
    app_id = os.getenv('META_APP_ID', 'dummy_app_id')
    app_secret = os.getenv('META_APP_SECRET', 'dummy_secret')
    
    FacebookAdsApi.init(app_id, app_secret, access_token)
    
    # Fechas
    fecha_fin = date.today() - timedelta(days=1)
    fecha_inicio = fecha_fin - timedelta(days=7)
    
    # Cuenta publicitaria
    account = AdAccount('act_YOUR_ACCOUNT_ID')
    
    # Obtener insights con conversaciones
    insights = account.get_insights(
        fields=['actions', 'spend', 'impressions'],
        params={
            'time_range': {
                'since': fecha_inicio.strftime('%Y-%m-%d'),
                'until': fecha_fin.strftime('%Y-%m-%d')
            },
            'level': 'ad',
            'action_attribution_windows': ['7d_click', '1d_view']
        }
    )
    
    total_conversaciones = 0
    
    for insight in insights:
        actions = insight.get('actions', [])
        
        for action in actions:
            action_type = action.get('action_type', '')
            value = int(action.get('value', 0))
            
            # Capturar todas las métricas de conversaciones
            if action_type in [
                'onsite_conversion.messaging_conversation_started_7d',
                'onsite_conversion.messaging_first_reply',
                'onsite_conversion.total_messaging_connection'
            ]:
                total_conversaciones += value
                print(f"✅ {action_type}: {value}")
    
    print(f"Total conversaciones encontradas: {total_conversaciones}")
    
    return total_conversaciones

# Ejecutar sincronización
if __name__ == "__main__":
    conversaciones = sincronizar_conversaciones_meta_ads()
```

### Notas Importantes

- **Formato de Respuesta**: Las acciones de mensajería vienen con prefijo `onsite_conversion.`
- **Ventanas de Atribución**: Usar `7d_click` y `1d_view` para máxima cobertura
- **Filtrado**: No todos los anuncios generarán conversaciones de mensajería
- **Debugging**: Siempre imprimir todas las acciones disponibles para verificar estructura
- **Rendimiento**: Usar llamadas por lotes para cuentas con muchos anuncios