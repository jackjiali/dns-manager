import os
root_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'peb_dns_author_lijiajia'
    ROOT_DIR = root_dir

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        import logging
        app.logger.setLevel(logging.INFO)

        # log to syslog
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

        # log to stderr
        from logging import StreamHandler
        st_handler = StreamHandler()
        st_handler.setLevel(logging.WARNING)
        app.logger.addHandler(st_handler)

        # log to file
        info_log = os.path.join(app.root_path, "logs", "peb_dns_info.log")
        if not os.path.exists(os.path.dirname(info_log)):
            os.makedirs(os.path.dirname(info_log))
        if not os.path.exists(info_log):
            open(info_log,"w+").close()
        info_file_handler = logging.handlers.RotatingFileHandler(
            info_log, maxBytes=1048576, backupCount=20)
        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]')
        )
        app.logger.addHandler(info_file_handler)

config = {
    'prod': ProductionConfig,
    'default': ProductionConfig
}

config_pyfiles = {
    'prod': 'config/peb_dns.cfg',
    'default': 'config/peb_dns.cfg'
}

