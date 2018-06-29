var fbAppId = '194084651239617';
var ID;
var accessToken;
//var objectToLike = 'http://www.ign.com/videos/2013/11/01/battlefield-4-next-gen-vs-current-gen';

// Solo para validar que el App ID sea un string
if (fbAppId == ' ') {
  alert('Por favor coloca un App ID valido.');
}
/*
 * Aca inicializamos el codigo pertinente para poder
 * correr el SDK en JS de Facebook 
 */

window.fbAsyncInit = function() {
  FB.init({
    appId      : fbAppId, // App ID
    status     : true,    // check login status
    cookie     : true,    // enable cookies to allow the
                          // server to access the session
    xfbml      : true     // parse page for xfbml or html5
                          // social plugins like login button below
                        });

  // Put additional init code here
};

// Cargamos el SDK de manera asincrona.
(function(d, s, id){
 var js, fjs = d.getElementsByTagName(s)[0];
 if (d.getElementById(id)) {return;}
 js = d.createElement(s); js.id = id;
 js.src = "//connect.facebook.net/en_US/all.js";
 fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


/*
* APIs usada en la funcion load():
* FB.getLoginStatus con JS:
*   https://developers.facebook.com/docs/reference/javascript/FB.getLoginStatus/
*/

function load () {
    FB.getLoginStatus(function(response) {
        if (response.status === 'connected') {
          // El usuario esta loggeado y se ha autenticado con
          // tu aplicacion. response.authResponse nos retorna
          // el user's ID, un access token valido, el access
          // token nos dice el tiempo que tenemos valido para
          // seguir loggeado.
          var uid = response.authResponse.userID;
          var accessToken = response.authResponse.accessToken;

          document.getElementById('logout_button').style.display = "inline-block";
          document.getElementById('login_button').style.display = "none";
          document.getElementById('status').innerHTML = "Logged.";
        } else if (response.status === 'not_authorized') {
          // El usuario esta loggeado pero no
          // ha autenticado la aplicacion.
          document.getElementById('logout_button').style.display = "inline-block";
          document.getElementById('login_button').style.display = "inline-block";
        } else {
          // El usuario no ha iniciado sesion.
          document.getElementById('logout_button').style.display = "none";
          document.getElementById('login_button').style.display = "inline-block";
        }
    });
}

/*
* APIs usada en la funcion login_fb():
* FB.login con JS:
*   https://developers.facebook.com/docs/reference/javascript/FB.login/
*/

function login_fb () {
    FB.login(function(response) {
        if (response.authResponse) {
            accessToken = response.authResponse.accessToken;
            document.getElementById('status').innerHTML ='Bienvenido!  Adquiriendo informacion.... ';
            FB.api('/me', function(response) {
               document.getElementById('status').innerHTML = '\nUn placer verte de nuevo por aca, ' + response.name + '.';
               recargarboton("login");
            });
        } else {
            document.getElementById('status').innerHTML = 'El usuario cancelo el login o tuvo un error al ingresar los datos.';
        }
    },{scope: 'user_friends,public_profile,email'});
}

function logout(){
    FB.logout(function(response) {
        // user is now logged out
        recargarboton("logout");
    });
    document.getElementById('status').innerHTML = '\nHasta pronto.';
}

function recargarboton(accion){
    if (accion=="login"){
        document.getElementById('logout_button').style.display = "inline-block";
        document.getElementById('login_button').style.display = "none";
    }
    else{
        document.getElementById('logout_button').style.display = "none";
        document.getElementById('login_button').style.display = "inline-block";
    }
}

function load_friends(){
    FB.getLoginStatus(function(response) {
        if (response.status === 'connected') {
            FB.api(
      			  '/me/friends',
      			  function(response) {
      			      // Insert your code here
                  alert("Tienes "+response.summary.total_count+" amigos");
                  console.log(response);
      			  }
      			);
        }else{
            alert("No estas Conectado");
        }
    });
}

function load_post(){
    FB.getLoginStatus(function(response) {
        if (response.status === 'connected') {
            FB.ui({
              method: 'feed',
              link: 'http://www.ciens.ucv.ve/portalasig2/',
              caption: 'An example caption',
            }, function(response){});
        }else{
            alert("No estas Conectado");
        }
    });
}