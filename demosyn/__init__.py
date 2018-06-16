from pyramid.config import Configurator


def main(global_config, **settings):
    with Configurator(settings=settings) as config:
        config.include('cornice')
        config.include('demosyn.loopworker')
        config.scan('demosyn.views')
        return config.make_wsgi_app()
