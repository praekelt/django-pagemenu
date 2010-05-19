class Item(object):
    def __init__(self, title, get, default=False):
        self.title=title
        self.default=default
        get['value'] = str(get['value'])
        self.get=get

class IntegerFieldRangeItem(Item):
    def __init__(self, title, get, field_name, filter_range, default=False):
        self.field_name = field_name
        self.filter_range = filter_range
        super(IntegerFieldRangeItem, self).__init__(title, get, default)

    def action(self, queryset):
        return queryset.filter(**{"%s__range" % self.field_name: self.filter_range})
