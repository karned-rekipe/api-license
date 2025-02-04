# api-licence

sur Keycloak
- créer un client (il s'agira d'une app ou d'une api)
- dans ce client, créer les roles
- créer un groupe (il s'agira de l'uuid du produit)
- dans ce groupe, ajouter les roles

L'affectation d'une licence à un utilisateur consistera donc à l'ajouter à un groupe
La désaffectation... à le retirer du groupe

Les opérations d'affectation et de désaffectation de licences seront réalisées par un consumer Kafka pour gérer les changements en masse.
Les licences seront stockées dans une base de données.
Toutes les heures un airflow listera les licences expirées pour les désactiver.

## todo
connexion à keycloak en mode public avec le client_id et client_secret

## fonctionnement
### sale
- uuid
- details
  - product_uuid
  - name
  - description
  - quantity
  - net_price
  - vat
  - gross_price
- entity_uuid
- net_subtotal
- vat
- order_amount
- total_quantity
- paid
- payment_amount
- paiement_details
  - kind
  - amount
- webhook

### entity
- uuid
- name

### user
- uuid (from keycloak)
- entities : array

### product (type de licence)
- uuid 
- name
- description
- type ? (utiliser pour grouper les licences ex : app-recipe)
- value ?
- net_price
- vat
- gross_price
- iat
- exp

le produit sera proposé en différentes déclinaisons : à la journée (1), au mois (30), à l'année (365)

### licence
- uuid
- type_uuid (produit_uuid)
- sales
  - sale_uuid 
  - status (unpaid, overdue, paid, cancelled)
- nom
- iat
- exp
- user_uuid
- historical (historique des affectations : iat, exp, user_id, manager_id)
- auto_renew
- entities_uuid (entreprise / asso  uuid)


## Routes

GET /purchase
lister les plans de licences disponibles à l'achat
soit dans la base product les uuid groupé par type, ordonné par net_price
{
    name
}

POST /purchase/{type_uuid}
achat d'une licence. le paiement déclenchera la création de la licence.

GET /unassigned
lister les licences non assignées à un utilisateur
soit dans la base de données license celle dont user_uuid est vide

GET /assigned
lister les licences assignées
soit dans la base de données celle dont user_uuid n'est pas vide

GET /expired
lister les licences ayant expirées
soit celle dont le exp est dans le passé, classées par ordre inverse de exp

GET /pending
lister les licences en attente de paiement
soit celle dont le paiement_status n'est pas à paid dans les sales

POST /{uuid}/assign/{user_uuid}
affecte une licence à un utilisateur
soit ajout à un groupe de l'utilisateur concerné

POST /{uuid}/transfer/{user_id}
transfert de la licence à un utilisateur
retrait du groupe de l'ancien utilisateur
ajout à un groupe du nouvel utilisateur

POST /{uuid}/revoke
retire la licence à un utilisateur
retrait du groupe de l'utilisateur

POST /{uuid}/renew
renouvelle une licence en se basant sur le produit (type_uuid). Le paiement déclenchera le renouvellement.

POST /{uuid}/cancel
passe auto_renew à false
la licence reste active et affectée jusqu'à la fin de validité

POST /{uuid}/activate
active les licences en lien avec la vente payée
soit ajout à un groupe de l'utilisateur concerné

POST /{uuid}/deactivate
désactive une licence
soit retrait du groupe de l'utilisateur





à voir plus tard... sur une autre API ?

GET /sale
lister les ventes

GET /sale/{sale_uuid}
lister les licences associées à une vente

POST /sale/{sale_uuid}/pay
marque la vente comme payée
active les licences associées

POST /sale/{sale_uuid}/cancel
annule la vente