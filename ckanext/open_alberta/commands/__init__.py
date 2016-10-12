from pylons import config

def generate_email(template_nm, **kwargs):
    env = config['pylons.app_globals'].jinja_env
    template = env.get_template('emails/'+template_nm)
    kwargs.update(site_title=config['ckan.site_title'],
                  site_url=config['ckan.site_url'])
    lines = [ln for ln in template.generate(kwargs)]
    subject = lines[0]
    body = ''.join(lines[1:])
    return subject, body

