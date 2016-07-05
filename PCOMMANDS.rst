#Various paster commands to reference as we need them.

#User add
paster --plugin=ckan user add USERNAME email=user@example.com -c /etc/ckan/default/development.ini

#Promote a user to administrator.
paster --plugin=ckan sysadmin add USERNAME-c /etc/ckan/default/development.ini


#Purge all datasets marked as deleted
paster --plugin=ckan dataset list -c /etc/ckan/production.ini|grep \(deleted\)\$|cut -f 1 -d ' '|xargs -I {} -P 3 paster --plugin=ckan dataset purge {} -c /etc/ckan/production.ini


