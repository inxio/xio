
- pb gestion fichier .tpl (pas chargé car pas .html)

- pb de gestion de template par defaut (eg: getTemplate d'une section)


- pb des connectedcallback
    => a eviter car un contenu peut etre transformé via les template (eg app.content)
    => utilier render qui garantit un post templating + la gestion de rendu deja fait
    => bug connu ou le contenu n'est pas present (eg this.innerText), co tournement : declarer les element sous document.addEventListener('DOMContentLoaded', ) 

    solution actuelle:
        connectedcallback utilisant timeout avec render par default

- pb des rendering multiple (envoi d'etre utilisé dans un template)   

    -=> empeche d'utilisé les attribute, etcc


- pb des render multiples

    => desactivé par defaut, a charge d'un element d'appeller ses child

    => utilisation des event pour auto render ? les element subscribes au parent (eg page) pour declencher un render ?



- pb des element devant etre rendu aprés les enfants (eg element data contenant plusieurs elements include)

    => test avec connection callback et nx.status
