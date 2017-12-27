class DBRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'panglao':
            return 'panglao'
        if model._meta.app_label == 'cheapcdn':
            return 'cheapcdn'
        if model._meta.app_label == 'lifecycle':
            return 'lifecycle'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'panglao':
            return 'panglao'
        if model._meta.app_label == 'cheapcdn':
            return 'cheapcdn'
        if model._meta.app_label == 'lifecycle':
            return 'lifecycle'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'panglao':
            if obj2._meta.app_label != 'panglao':
                return False
        if obj1._meta.app_label == 'cheapcdn':
            if obj2._meta.app_label != 'cheapcdn':
                return False
        if obj1._meta.app_label == 'lifecycle':
            if obj2._meta.app_label != 'lifecycle':
                return False

    def allow_migrate(self, db, app_label, **hints):
        if db == 'cheapcdn' and app_label == 'cheapcdn':
            return True
        if db == 'lifecycle' and app_label == 'lifecycle':
            return True
        return False
